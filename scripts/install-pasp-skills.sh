#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--force] [--copy | --link] [--source <repo-or-skill-dir>] [target-project-dir]

Install the complete PASP helper directly into a target project:
  .agents/skills/pasp-helper/             Runtime package (copy by default)
  .agents/skills/pasp-verifier/           Read-only verifier wrapper
  .codex/agents/pasp-verifier.toml        Codex agent configuration
  .claude/skills/pasp-helper             Link to the same project package
  .claude/agents/pasp-verifier.md         Claude agent configuration

No project-root skills/ directory or .codex/skills/ aliases are created.
The target defaults to the current directory.

Options:
  --force   replace managed project entries and migrate recognized old installs
  --copy    copy the package (default; independent of the source repository)
  --link    link .agents/skills/pasp-helper directly to the external source
  --source  source repository, package directory, or installed project

Source resolution: --source, PASP_SKILLS_SOURCE, script location, then ./.
Old copied root packages are backed up under .agents/pasp-install-backups/.
User-level skills are left unchanged.
EOF
}

force=0
mode=copy
target=.
target_set=0
source_hint="${PASP_SKILLS_SOURCE:-}"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --force) force=1; shift ;;
    --copy) mode=copy; shift ;;
    --link) mode=link; shift ;;
    --source)
      shift
      if [ "$#" -eq 0 ] || [ -z "$1" ]; then
        printf 'Missing value for --source.\n' >&2
        exit 2
      fi
      source_hint="$1"
      shift
      ;;
    --source=*)
      source_hint="${1#--source=}"
      if [ -z "$source_hint" ]; then
        printf 'Missing value for --source.\n' >&2
        exit 2
      fi
      shift
      ;;
    -h|--help) usage; exit 0 ;;
    -*) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
    *)
      if [ "$target_set" -eq 1 ]; then
        printf 'Only one target directory is allowed.\n' >&2
        exit 2
      fi
      target="$1"
      target_set=1
      shift
      ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

resolve_source_skills() {
  local candidate="$1"
  local package
  [ -d "$candidate" ] || return 1
  for package in "$candidate/skills" "$candidate" "$candidate/.agents/skills/pasp-helper"; do
    if [ -f "$package/SKILL.md" ] && [ -d "$package/subskills" ] && [ -d "$package/knowledge" ]; then
      (cd "$package" && pwd -P)
      return 0
    fi
  done
  return 1
}

source_skills=""
if [ -n "$source_hint" ]; then
  source_skills="$(resolve_source_skills "$source_hint" || true)"
else
  source_skills="$(resolve_source_skills "$script_dir/.." || true)"
  if [ -z "$source_skills" ]; then
    source_skills="$(resolve_source_skills "$script_dir" || true)"
  fi
  if [ -z "$source_skills" ]; then
    source_skills="$(resolve_source_skills . || true)"
  fi
fi
if [ -z "$source_skills" ]; then
  printf 'Cannot find source PASP skills package; use --source /path/to/PASPskills.\n' >&2
  exit 1
fi

mkdir -p "$target"
target="$(cd "$target" && pwd -P)"
legacy_root="$target/skills"
target_agent_skills="$target/.agents/skills"
target_agent_pasp_helper="$target_agent_skills/pasp-helper"
target_agent_pasp_verifier="$target_agent_skills/pasp-verifier"
target_pasp_verifier_agent="$target/.codex/agents/pasp-verifier.toml"
target_claude_verifier_agent="$target/.claude/agents/pasp-verifier.md"
target_claude_pasp_helper="$target/.claude/skills/pasp-helper"

exists() { [ -e "$1" ] || [ -L "$1" ]; }

# Managed parent directories must remain inside this target, rather than
# redirecting installation or recursive replacement into another project.
for parent in "$target/.agents" "$target_agent_skills" "$target/.codex" \
  "$target/.codex/agents" "$target/.claude" "$target/.claude/agents" "$target/.claude/skills"; do
  if [ -L "$parent" ]; then
    printf 'Refusing symlinked installation parent: %s\n' "$parent" >&2
    exit 1
  fi
done

is_pasp_package() {
  [ -f "$1/SKILL.md" ] && [ -d "$1/knowledge" ] && [ -d "$1/subskills" ] &&
    grep -Eq '^name:[[:space:]]*pasp-helper[[:space:]]*$' "$1/SKILL.md"
}

points_to_legacy_root() {
  [ -L "$1" ] || return 1
  local link
  link="$(readlink "$1")"
  [ "$link" = ../../skills ] || [ "$link" = "$legacy_root" ]
}

# Copying a package into its own subtree would recursively embed previous
# installations on the next upgrade. Installing into the authoring repository
# remains safe because its source package is the sibling root skills/ folder.
if [ "$target_agent_pasp_helper" != "$source_skills" ]; then
  case "$target_agent_pasp_helper/" in
    "$source_skills/"*)
      printf 'Destination is inside the source package; choose a separate project.\n' >&2
      exit 1
      ;;
  esac
fi

legacy_install=0
if is_pasp_package "$legacy_root"; then
  for entry in "$target_agent_pasp_helper" "$target/.codex/skills/pasp-helper" "$target_claude_pasp_helper"; do
    if points_to_legacy_root "$entry"; then
      legacy_install=1
    fi
  done
fi

managed_paths=("$target_agent_pasp_helper" "$target_agent_pasp_verifier"
  "$target_pasp_verifier_agent" "$target_claude_verifier_agent" "$target_claude_pasp_helper")
for path in "${managed_paths[@]}"; do
  if exists "$path" && [ "$force" -ne 1 ]; then
    printf 'Refusing to overwrite existing path: %s\nRe-run with --force to replace it.\n' "$path" >&2
    exit 1
  fi
  # Replacing a symlink itself never removes its referent. Replacing a real
  # directory must not remove the selected source package or any ancestor.
  if [ -d "$path" ] && [ ! -L "$path" ]; then
    physical_path="$(cd "$path" && pwd -P)"
    case "$source_skills/" in
      "$physical_path/"*)
        printf 'Source skills are inside the destination: %s\nSource was left unchanged.\n' "$path" >&2
        exit 1
        ;;
    esac
  fi
done
if [ "$legacy_install" -eq 1 ] && [ "$force" -ne 1 ]; then
  printf 'Recognized an old root skills/ installation; re-run with --force to migrate it.\n' >&2
  exit 1
fi

# Prepare copies before replacing anything; a copy remains independent even
# when --source names a symlink. This staging directory is outside discovery.
staging="$(mktemp -d "${TMPDIR:-/tmp}/pasp-install.XXXXXX")"
trap 'rm -rf "$staging"' EXIT
if [ "$mode" = copy ]; then
  cp -a "$source_skills" "$staging/package"
fi

backup=""
ensure_backup() {
  if [ -z "$backup" ]; then
    if [ -L "$target/.agents/pasp-install-backups" ]; then
      printf 'Refusing symlinked backup directory.\n' >&2
      exit 1
    fi
    mkdir -p "$target/.agents/pasp-install-backups"
    backup="$(mktemp -d "$target/.agents/pasp-install-backups/migration.XXXXXX")"
  fi
}

if [ "$legacy_install" -eq 1 ]; then
  preserve_root=0
  if [ -d "$legacy_root" ]; then
    physical_legacy="$(cd "$legacy_root" && pwd -P)"
    case "$source_skills/" in "$physical_legacy/"*) preserve_root=1 ;; esac
  fi
  if [ "$preserve_root" -eq 1 ] && [ ! -L "$legacy_root" ]; then
    printf 'Preserved root skills/: it contains the selected source package.\n'
  elif [ -L "$legacy_root" ]; then
    rm "$legacy_root"
  else
    ensure_backup
    mv "$legacy_root" "$backup/skills"
  fi
fi

# Only remove known old project aliases, never arbitrary folders or user-level
# skills. Unrecognized real folders remain unchanged.
for name in pasp-helper pasp-verifier; do
  old="$target/.codex/skills/$name"
  if [ -L "$target/.codex/skills" ]; then
    break
  fi
  if [ -L "$old" ]; then
    link="$(readlink "$old")"
    case "$link" in
      ../../skills|../../.agents/skills/pasp-helper|../../.agents/skills/pasp-verifier|"$legacy_root")
        if [ "$force" -eq 1 ]; then rm "$old"; fi
        ;;
    esac
  fi
done

mkdir -p "$target_agent_skills" "$target/.codex/agents" "$target/.claude/agents" "$target/.claude/skills"
for path in "${managed_paths[@]}"; do
  if exists "$path"; then rm -rf "$path"; fi
done
if [ "$mode" = copy ]; then
  mv "$staging/package" "$target_agent_pasp_helper"
else
  ln -s "$source_skills" "$target_agent_pasp_helper"
fi
mkdir -p "$target_agent_pasp_verifier"
cat > "$target_agent_pasp_verifier/SKILL.md" <<'EOF'
---
name: pasp-verifier
description: Use the local read-only PASP verifier contract for bounded fact collection tasks.
---

Read `.agents/skills/pasp-helper/subskills/pasp-verifier/skill.md` from the
project root. If navigating from this wrapper's directory, the same contract
is `../pasp-helper/subskills/pasp-verifier/skill.md`.

The canonical contract stays inside the installed helper package; do not
copy its workflow or reference rules into this wrapper.
EOF
ln -s "../../.agents/skills/pasp-helper" "$target_claude_pasp_helper"

cat > "$target_pasp_verifier_agent" <<'EOF'
name = "pasp-verifier"
description = "Use this agent whenever you need to check, validate, or inspect files in a PASP workflow, including input file validation, format checking, reference lookup, directory inspection, structure analysis, or output verification before continuing to the next stage."
sandbox_mode = "read-only"

developer_instructions = """
You are the read-only PASP verifier agent.

Before doing any task, read and follow:
- .agents/skills/pasp-helper/subskills/pasp-verifier/skill.md

Your role is bounded fact collection only. You may inspect named repository knowledge files, reference files, user input files, output files, logs, scripts, and directories. You must not modify files, decide scientific parameters, choose the final workflow route, promote inputs, create run directories, prepare submission artifacts, submit jobs, or write the final user-facing answer.

Supported modes:
- reference-check
- input-preflight
- directory-inventory
- output-validation
- structure-analysis
- log-summary
- template-compare
- source-audit

Use the mode requested by the main agent. If no mode is specified, ask the main agent to provide one instead of broadening the task yourself.

Output format:
Scope:
Findings:
Sources:
Uncertain:
Needs main-agent decision:
Conclusion: pass | fail | blocked | not-applicable
"""
EOF

cat > "$target_claude_verifier_agent" <<'EOF'
---
name: pasp-verifier
description: Use this agent whenever you need to check, validate, or inspect files in a PASP workflow, including input file validation, format checking, reference lookup, directory inspection, structure analysis, or output verification before continuing to the next stage.
tools: Read, Glob, Grep
---

# PASP Verifier Agent

You are the read-only PASP verifier agent.

Before doing any task, read and follow:
- `.agents/skills/pasp-helper/subskills/pasp-verifier/skill.md`

Your role is bounded fact collection only. You may inspect named repository knowledge files, reference files, user input files, output files, logs, scripts, and directories. You must not modify files, decide scientific parameters, choose the final workflow route, promote inputs, create run directories, prepare submission artifacts, submit jobs, or write the final user-facing answer.

Supported modes:
- `reference-check`
- `input-preflight`
- `directory-inventory`
- `output-validation`
- `structure-analysis`
- `log-summary`
- `template-compare`
- `source-audit`

Use the mode requested by the main agent. If no mode is specified, ask the main agent to provide one instead of broadening the task yourself.

Output format:

```text
Scope:
Findings:
Sources:
Uncertain:
Needs main-agent decision:
Conclusion: pass | fail | blocked | not-applicable
```
EOF

printf '%s\n' "Installed PASP skills into: $target"
printf '%s\n' "  skills package: $target_agent_pasp_helper"
printf '%s\n' "  skills mode:    $mode"
printf '%s\n' "  Codex skill:    $target_agent_pasp_helper/SKILL.md"
printf '%s\n' "  Verifier skill: $target_agent_pasp_verifier/SKILL.md"
printf '%s\n' "  Codex agent:    $target_pasp_verifier_agent"
printf '%s\n' "  Claude agent:   $target_claude_verifier_agent"
printf '%s\n' "  Claude skill:   $target_claude_pasp_helper/SKILL.md"
if [ -n "$backup" ]; then printf '%s\n' "  Migration backup: $backup"; fi
