---
name: pasp-helper
description: Classify PASP user intent and route the request to the most relevant workflow or reference subskill.
---

You are the entry skill for PASP Assistant.

Your responsibilities are only:
1. Decide whether the user is asking for a workflow or for reference information.
2. Continue by reading the smallest relevant local instruction file under the skill root.
3. If the user asks which PASPskills version is installed, read `VERSION` in the skill root and answer with that value.

Do not call nested names such as `pasp-helper:pasp-orchestrator` with the `Skill` tool. In Claude-style runtimes, only the top-level skill name may be registered. The files under `subskills/` are local instruction files, not separately registered skills unless the deployment explicitly says so.

Do not expand PASP domain details here. Keep this entry layer thin and avoid loading unrelated lecture or example context.

## Resource paths
The skill root is the directory containing this loaded `SKILL.md`, following
its symlink if necessary. Discover it from the actual loaded entry; do not
assume the user's working directory is the package directory. The installer
normally places it at `<project>/.agents/skills/pasp-helper/`; the source
repository keeps its authoring copy at `skills/`.

Bare `knowledge/...` and `subskills/...` resource paths in this package are
relative to that skill root. Explicit `./` and `../` paths and Markdown links
are relative to the document containing them. User inputs, outputs and run
directories remain relative to the user's workspace, not the skill root.

When using a shell example, bind `PASP_SKILL_ROOT` to the absolute directory
of the loaded entry and quote it, for example from an installed project root:
`PASP_SKILL_ROOT="$(cd .agents/skills/pasp-helper && pwd -P)"`.
Use `"$PASP_SKILL_ROOT/knowledge/..."` for helper scripts; do not `cd` into the
package or create a project-root `skills/` alias to make commands work.
Pass the resolved skill root to verifier or workflow handoffs so delegated
readers use the same package, including when accessed through the Claude link.

## Routing Principles
- If the user asks what to do, how to start, what the next step is, or how to complete a PASP calculation task, route to workflow first.
- If the user explicitly asks for the meaning, syntax, default, allowed values, or caveats of a field, file, block, parameter, or `Model`, route to reference first.
- If the user asks both about a task and about parameters, or asks which settings to modify inside a task:
  - route to workflow first to identify the stage;
  - then add only the reference details needed for that stage.

## Subskill Routing
- workflow / intent classification / task routing -> read and follow `subskills/pasp-orchestrator/skill.md`
- reference lookup -> read and follow `subskills/pasp-reference/skill.md`
- read-only PASP fact verification tasks -> use `subskills/pasp-verifier/skill.md` only when a downstream workflow or reference subskill asks for bounded subagent-style fact collection.

If you need a workflow or reference subskill, use normal file-reading/context loading on the path above. Do not invoke `Skill(<entry>:<subskill>)` or any colon-qualified skill name.

## Supported Workflows
- Exchange-path analysis and magnetic interaction model preparation
- Effective Hamiltonian construction and fitting
- Monte Carlo simulation
- Dynamics simulation
- GA global structure search
- Tight-binding model construction and analysis
- Spin-induced polarization

## General Notes
- Basic input files such as `PASP.input`, `cell.str`, and `unit_cell.str` belong to general reference/onboarding, not to a separate workflow.
- Runtime behavior should rely only on `knowledge/reference/`, `knowledge/workflows/`, `knowledge/templates/`, and `knowledge/scripts/`. Do not depend on lecture files or external example directories.
- This entry layer only routes the request downstream. Early confirmation, run-directory rules, subagent authorization, and workflow-internal branch rules belong to the downstream subskill or workflow document.
- `subskills/pasp-verifier/skill.md` is a read-only verifier contract, not a user-facing workflow route. It does not decide workflow paths, choose scientific parameters, edit files, promote inputs, prepare submissions, or write final answers.
