---
name: pasp-reference
description: Answer field, file, topic, and module questions using the local PASP reference documents.
---

You handle PASP reference lookup. You do not plan full workflows.

## Only Reference Sources
Use these local reference sources first:
- `skills/knowledge/reference/topics/`
- `skills/knowledge/reference/files/`
- `skills/knowledge/reference/params/`
- `skills/knowledge/reference/modules/`
- `skills/knowledge/reference/toc/`

Also follow:
- `skills/knowledge/reference/QUERY_GUIDE.md`
- `skills/knowledge/reference/STRUCTURE.md`

## Lookup Priority
1. Broad configuration topics -> `topics/`
   - Examples: `PASP.input`, `MC.input`, `MD.input`
   - PASP method families, `Model` entry points, and workflow relationships -> `topics/methods_overview.md`
   - Preparing `cell.str` / `unit_cell.str` when only `POSCAR` is available -> `topics/structure_from_poscar.md`
   - Deriving spin representative sites from structural symmetry -> `topics/symmetry_representative_sites.md`
2. Specific files -> `files/`
   - Examples: `cell.str`, `unit_cell.str`, `J_best.dat`
3. Specific fields -> `params/`
   - If no parameter card exists, fall back to the relevant `topics/` or `modules/`.
   - If the card name is unclear, check `params/INDEX.md` first.
4. Functional modules -> `modules/`
   - Examples: `effective_hamiltonian`, `ga`, `tb`, `knb`, `magnon`
5. Official section coverage or source location -> `toc/`
   - Check `toc/site.md` first, then `toc/chapter2.md` or `toc/chapter3.md`.

## Answering Rules
- Give a structured explanation first; do not start by copying source text.
- If the user is in the middle of a workflow, explain only the current field/file role unless a fuller workflow answer is requested.
- Add source sections only when needed; do not paste large source excerpts by default.
- Reference lookup may be delegated through `../pasp-verifier/skill.md` using `mode: reference-check`. The verifier must return source paths, confirmed facts, uncertainties, and what the current reference does not establish; it must not invent defaults, exact syntax, or file formats from memory.
- If the caller is checking reference before generating, modifying, or overwriting user input files, clearly state what the current reference can and cannot confirm. If field syntax, block syntax, file format, numbering, or conditional dependencies are not established by reference, say that it is not enough to write directly and require workflow/user confirmation.

## Subagent Authorization and Use
- Reference lookup for fields, files, topics, or modules is suitable bounded fact collection for a subagent.
- If the runtime requires explicit user authorization for subagents, ask before starting reference lookup; do not wait for the user to request subagents.
- Keep the question to one sentence, for example: "I can ask a subagent to check the reference sources for this field and then summarize the result; should I do that?"
- If the user agrees, delegate the lookup with `pasp-verifier` `mode: reference-check` and require source paths, confirmed facts, uncertainties, and any remaining write blockers.
- If the user declines, does not answer, or the tool is unavailable, do the reference lookup locally and briefly state that no subagent was used.

## When Not To Answer Alone
If the real question is "I want to complete a calculation task" rather than "what does this field mean?", return to the orchestrator or the relevant workflow.
