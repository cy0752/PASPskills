#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' "Usage: $0 [--force] [--copy] [--source <PASPskills-repo-or-skills-dir>] [target-project-dir]"
  printf '%s\n' ""
  printf '%s\n' "Install the PASP skills package plus Codex and Claude integration into a target project."
  printf '%s\n' "If target-project-dir is omitted, install into the current working directory."
  printf '%s\n' ""
  printf '%s\n' "Installs:"
  printf '%s\n' "  <target>/skills/                         PASP runtime skills package"
  printf '%s\n' "  <target>/.agents/skills/pasp-helper       Codex project skill symlink"
  printf '%s\n' "  <target>/.agents/skills/pasp-verifier/     Codex verifier skill wrapper"
  printf '%s\n' "  <target>/.codex/skills/pasp-helper     Codex project skill symlink"
  printf '%s\n' "  <target>/.codex/skills/pasp-verifier/    Codex verifier skill wrapper"
  printf '%s\n' "  <target>/.codex/agents/pasp-verifier.toml Read-only Codex agent config"
  printf '%s\n' "  <target>/.claude/agents/pasp-verifier.md Read-only Claude subagent config"
  printf '%s\n' "  <target>/.claude/skills/pasp-helper    Claude project skill symlink"
  printf '%s\n' ""
  printf '%s\n' "Options:"
  printf '%s\n' "  --force    overwrite existing installed files"
  printf '%s\n' "  --copy     copy this repo's skills directory instead of symlinking it"
  printf '%s\n' "  --source   source PASPskills repo directory, or the skills directory itself"
  printf '%s\n' ""
  printf '%s\n' "Source resolution order:"
  printf '%s\n' "  1. --source argument"
  printf '%s\n' "  2. PASP_SKILLS_SOURCE environment variable"
  printf '%s\n' "  3. path relative to this script, when run from the PASPskills repo"
  printf '%s\n' "  4. ./ relative to the current working directory"
}

force=0
copy=0
target="."
source_hint="${PASP_SKILLS_SOURCE:-}"
default_source_root="./"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --force)
      force=1
      shift
      ;;
    --copy)
      copy=1
      shift
      ;;
    --source)
      shift
      if [ "$#" -eq 0 ]; then
        printf 'Missing value for --source.\n' >&2
        usage >&2
        exit 2
      fi
      source_hint="$1"
      shift
      ;;
    --source=*)
      source_hint="${1#--source=}"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [ "$target" != "." ]; then
        printf 'Only one target directory is allowed.\n' >&2
        usage >&2
        exit 2
      fi
      target="$1"
      shift
      ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$target"
target="$(cd "$target" && pwd)"

resolve_source_skills() {
  local candidate="$1"

  if [ -z "$candidate" ] || [ ! -d "$candidate" ]; then
    return 1
  fi

  if [ -f "$candidate/skills/SKILL.md" ]; then
    cd "$candidate/skills" && pwd -P
    return 0
  fi

  if [ -f "$candidate/SKILL.md" ] && [ -d "$candidate/subskills" ] && [ -d "$candidate/knowledge" ]; then
    cd "$candidate" && pwd -P
    return 0
  fi

  return 1
}

source_skills=""
if [ -n "$source_hint" ]; then
  source_skills="$(resolve_source_skills "$source_hint" || true)"
else
  if [ "$(basename "$script_dir")" = "scripts" ]; then
    source_skills="$(resolve_source_skills "$script_dir/.." || true)"
  fi
  if [ -z "$source_skills" ] && [ "$script_dir" != "$target" ]; then
    source_skills="$(resolve_source_skills "$script_dir" || true)"
  fi
  if [ -z "$source_skills" ]; then
    source_skills="$(resolve_source_skills "$default_source_root" || true)"
  fi
fi

if [ -z "$source_skills" ] || [ ! -f "$source_skills/SKILL.md" ]; then
  if [ -n "$source_hint" ]; then
    printf 'Cannot find source PASP skills package from --source/PASP_SKILLS_SOURCE: %s\n' "$source_hint" >&2
  else
    printf 'Cannot find source PASP skills package.\n' >&2
    printf 'Tried relative paths from this script and default source root: %s\n' "$default_source_root" >&2
  fi
  printf 'Provide the source repo with: %s --source /path/to/PASPskills\n' "$0" >&2
  printf 'Cannot find source PASP skills package at: %s\n' "$source_skills" >&2
  exit 1
fi

target_skills="$target/skills"
target_agent_skills="$target/.agents/skills"
target_agent_pasp_helper="$target_agent_skills/pasp-helper"
target_agent_pasp_verifier="$target_agent_skills/pasp-verifier"
target_codex_skills="$target/.codex/skills"
target_codex_agents="$target/.codex/agents"
target_claude_agents="$target/.claude/agents"
target_pasp_helper="$target_codex_skills/pasp-helper"
target_pasp_verifier_skill="$target_codex_skills/pasp-verifier"
target_pasp_verifier_agent="$target_codex_agents/pasp-verifier.toml"
target_claude_verifier_agent="$target_claude_agents/pasp-verifier.md"
target_claude_skills="$target/.claude/skills"
target_claude_pasp_helper="$target_claude_skills/pasp-helper"
legacy_claude_user_skills_dir="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
legacy_claude_user_pasp_dev="$legacy_claude_user_skills_dir/pasp-dev"
legacy_claude_user_paspskills="$legacy_claude_user_skills_dir/paspskills"
legacy_claude_user_pasp_helper="$legacy_claude_user_skills_dir/pasp-helper"
legacy_codex_pasp_dev="$target_codex_skills/pasp-dev"
legacy_claude_pasp_dev="$target_claude_skills/pasp-dev"
legacy_codex_paspskills="$target_codex_skills/paspskills"
legacy_claude_paspskills="$target_claude_skills/paspskills"
legacy_agent_pasp_dev="$target_agent_skills/pasp-dev"
legacy_agent_paspskills="$target_agent_skills/paspskills"

# Removing a real target directory must never remove the selected source.
# A target symlink pointing at the source is safe to replace during upgrades.
if [ -d "$target_skills" ] && [ ! -L "$target_skills" ]; then
  physical_target_skills="$(cd "$target_skills" && pwd -P)"
  case "$source_skills/" in
    "$physical_target_skills/"*)
      printf 'Source skills are inside the destination: %s\n' "$target_skills" >&2
      printf 'Choose a separate target project; the source was left unchanged.\n' >&2
      exit 1
      ;;
  esac
fi

require_overwrite_ok() {
  local path="$1"
  if { [ -e "$path" ] || [ -L "$path" ]; } && [ "$force" -ne 1 ]; then
    printf 'Refusing to overwrite existing path: %s\n' "$path" >&2
    printf 'Re-run with --force to replace it.\n' >&2
    exit 1
  fi
}

require_overwrite_ok "$target_skills"
require_overwrite_ok "$target_agent_pasp_helper"
require_overwrite_ok "$target_agent_pasp_verifier"
require_overwrite_ok "$target_pasp_helper"
require_overwrite_ok "$target_pasp_verifier_skill"
require_overwrite_ok "$target_pasp_verifier_agent"
require_overwrite_ok "$target_claude_verifier_agent"
require_overwrite_ok "$target_claude_pasp_helper"

mkdir -p "$target_agent_skills" "$target_codex_skills" "$target_codex_agents" "$target_claude_agents" "$target_claude_skills"

if { [ -e "$target_skills" ] || [ -L "$target_skills" ]; } && [ "$force" -eq 1 ]; then
  rm -rf "$target_skills"
fi

if [ "$copy" -eq 1 ]; then
  cp -a "$source_skills" "$target_skills"
else
  ln -s "$source_skills" "$target_skills"
fi

if { [ -e "$target_agent_pasp_helper" ] || [ -L "$target_agent_pasp_helper" ]; } && [ "$force" -eq 1 ]; then
  rm -rf "$target_agent_pasp_helper"
fi
ln -s "../../skills" "$target_agent_pasp_helper"

if { [ -e "$target_agent_pasp_verifier" ] || [ -L "$target_agent_pasp_verifier" ]; } && [ "$force" -eq 1 ]; then
  rm -rf "$target_agent_pasp_verifier"
fi
mkdir -p "$target_agent_pasp_verifier"

if { [ -e "$target_pasp_helper" ] || [ -L "$target_pasp_helper" ]; } && [ "$force" -eq 1 ]; then
  rm -rf "$target_pasp_helper"
fi
ln -s "../../skills" "$target_pasp_helper"

if { [ -e "$target_pasp_verifier_skill" ] || [ -L "$target_pasp_verifier_skill" ]; } && [ "$force" -eq 1 ]; then
  rm -rf "$target_pasp_verifier_skill"
fi
ln -s "../../.agents/skills/pasp-verifier" "$target_pasp_verifier_skill"
cat > "$target_agent_pasp_verifier/SKILL.md" <<'EOF'
---
name: pasp-verifier
description: Use the local read-only PASP verifier contract for bounded fact collection tasks.
---

Read and follow `skills/subskills/pasp-verifier/skill.md` in this target project.

This project-level skill is a thin Codex wrapper. The canonical verifier contract lives in the installed PASP package so it stays versioned with `skills/knowledge/`.
EOF

if { [ -e "$target_claude_pasp_helper" ] || [ -L "$target_claude_pasp_helper" ]; } && [ "$force" -eq 1 ]; then
  rm -rf "$target_claude_pasp_helper"
fi
ln -s "../../skills" "$target_claude_pasp_helper"

if [ "$force" -eq 1 ]; then
  if { [ -e "$legacy_codex_pasp_dev" ] || [ -L "$legacy_codex_pasp_dev" ]; }; then
    rm -rf "$legacy_codex_pasp_dev"
  fi
  if { [ -e "$legacy_claude_pasp_dev" ] || [ -L "$legacy_claude_pasp_dev" ]; }; then
    rm -rf "$legacy_claude_pasp_dev"
  fi
  if { [ -e "$legacy_codex_paspskills" ] || [ -L "$legacy_codex_paspskills" ]; }; then
    rm -rf "$legacy_codex_paspskills"
  fi
  if { [ -e "$legacy_claude_paspskills" ] || [ -L "$legacy_claude_paspskills" ]; }; then
    rm -rf "$legacy_claude_paspskills"
  fi
  if { [ -e "$legacy_agent_pasp_dev" ] || [ -L "$legacy_agent_pasp_dev" ]; }; then
    rm -rf "$legacy_agent_pasp_dev"
  fi
  if { [ -e "$legacy_agent_paspskills" ] || [ -L "$legacy_agent_paspskills" ]; }; then
    rm -rf "$legacy_agent_paspskills"
  fi
else
  if { [ -e "$legacy_codex_pasp_dev" ] || [ -L "$legacy_codex_pasp_dev" ] || [ -e "$legacy_claude_pasp_dev" ] || [ -L "$legacy_claude_pasp_dev" ] || [ -e "$legacy_codex_paspskills" ] || [ -L "$legacy_codex_paspskills" ] || [ -e "$legacy_claude_paspskills" ] || [ -L "$legacy_claude_paspskills" ]; }; then
    printf '%s\n' "Warning: legacy project skill entries named pasp-dev or paspskills were left unchanged."
    printf '%s\n' "Re-run with --force to remove legacy entries from .codex/skills and .claude/skills."
  fi
  if { [ -e "$legacy_agent_pasp_dev" ] || [ -L "$legacy_agent_pasp_dev" ] || [ -e "$legacy_agent_paspskills" ] || [ -L "$legacy_agent_paspskills" ]; }; then
    printf '%s\n' "Warning: legacy Codex skill entries under $target_agent_skills were left unchanged."
    printf '%s\n' "Re-run with --force to remove legacy pasp-dev and paspskills entries from .agents/skills."
  fi
fi

if [ "$force" -eq 1 ]; then
  if { [ -e "$legacy_claude_user_pasp_dev" ] || [ -L "$legacy_claude_user_pasp_dev" ]; }; then
    rm -rf "$legacy_claude_user_pasp_dev"
  fi
  if { [ -e "$legacy_claude_user_paspskills" ] || [ -L "$legacy_claude_user_paspskills" ]; }; then
    rm -rf "$legacy_claude_user_paspskills"
  fi
  if { [ -e "$legacy_claude_user_pasp_helper" ] || [ -L "$legacy_claude_user_pasp_helper" ]; }; then
    rm -rf "$legacy_claude_user_pasp_helper"
  fi
else
  if { [ -e "$legacy_claude_user_pasp_dev" ] || [ -L "$legacy_claude_user_pasp_dev" ] || [ -e "$legacy_claude_user_paspskills" ] || [ -L "$legacy_claude_user_paspskills" ] || [ -e "$legacy_claude_user_pasp_helper" ] || [ -L "$legacy_claude_user_pasp_helper" ]; }; then
    printf '%s\n' "Warning: legacy Claude user-scope PASP skill entry was left unchanged."
    printf '%s\n' "Re-run with --force to remove the legacy user-scope PASP skill entry."
  fi
fi

cat > "$target_pasp_verifier_agent" <<'EOF'
name = "pasp-verifier"
description = "Use this agent whenever you need to check, validate, or inspect files in a PASP workflow, including input file validation, format checking, reference lookup, directory inspection, structure analysis, or output verification before continuing to the next stage."
sandbox_mode = "read-only"

developer_instructions = """
You are the read-only PASP verifier agent.

Before doing any task, read and follow:
- skills/subskills/pasp-verifier/skill.md

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
- `skills/subskills/pasp-verifier/skill.md`

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
printf '%s\n' "  skills package: $target_skills"
if [ "$copy" -eq 1 ]; then
  printf '%s\n' "  skills mode:    copy"
else
  printf '%s\n' "  skills mode:    symlink -> $source_skills"
fi
printf '%s\n' "  Codex skill:    $target_agent_pasp_helper/SKILL.md"
printf '%s\n' "  Verifier skill: $target_agent_pasp_verifier/SKILL.md"
printf '%s\n' "  Legacy alias:   $target_pasp_helper/SKILL.md"
printf '%s\n' "  Codex agent:    $target_pasp_verifier_agent"
printf '%s\n' "  Claude agent:   $target_claude_verifier_agent"
printf '%s\n' "  Claude skill:   $target_claude_pasp_helper/SKILL.md"
