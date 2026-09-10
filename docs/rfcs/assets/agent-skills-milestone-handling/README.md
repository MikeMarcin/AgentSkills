# AgentSkills — milestone handling correction

**Implementation RFC pack · September 9, 2026 · AgentSkills only**

Start with [IMPLEMENTATION_PROMPT.md](IMPLEMENTATION_PROMPT.md). The canonical
execution grouping for this packet is [milestone-plan.json](milestone-plan.json);
[MILESTONES.md](MILESTONES.md) is its generated readable view.

The packet contains one new proposed RFC, **RFC-ASK-0011**, and seven provisional
cards, **ASK-0059–0065**, grouped into **two integrated milestones**. No M0/import
milestone and no one-integrator-per-card policy. These IDs follow the supplied
September 8 snapshot and are not a reservation; [IMPORT.md](IMPORT.md) governs live
reconciliation. Settled RFCs and historical evidence remain unchanged.

## What changes

A supplied offline milestone plan becomes the default execution plan. The skill
must discover, validate, remap and adopt it, retain its grouping on resume, and
amend it only for a concrete reason. Structured JSON is the normal new-pack shape;
legacy Markdown plans and planless RFC/issue targets remain supported.

Assignments bind outcomes and obligations, not whichever card happens to finish.
Completion and context replacement are separate decisions. The first integrator
performs needed preparation and then engineering; it is not a disposable planner.
Related cards stay together, required acceptance remains intact, and fresh
integrators still provide useful isolation at substantial boundaries.

## Read only what your operation needs

| Operation | Material |
|---|---|
| Implement | Implementation prompt, live RFC and adopted current milestone |
| Import / reconcile | IMPORT.md and reference/SOURCE_BASIS.md |
| Define plan data / continuation | contracts/PLAN.md, schema and contracts/CONTINUATION.md |
| Write future offline packs | authoring/PACK_AUTHORING.md and its minimal template |
| Verify | VERIFICATION.md; native guide only at native qualification |
| Check this packet | `python3 -B tools/validate_pack.py` and `python3 -B -m unittest discover -s tools -p 'test_*.py'` |

The scripts in this packet are local lint/render/test tools, not an installer,
production scheduler or permission to run arbitrary supplied code. The runtime
feature, changed native instructions and deployment are implementation work.
See [VALIDATION.md](VALIDATION.md) for checks actually performed here.
