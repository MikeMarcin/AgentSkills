---
name: writing-for-agents
description: Write or review documents agents consume. Use for skills, AGENTS.md or CLAUDE.md, role prompts, and other instruction files an agent reaches through a pointer.
---

# Writing for agents

This reference covers any document an agent reads while it works: a skill, a
root or nested `AGENTS.md` or `CLAUDE.md`, a role prompt, or a file reached
through a pointer. The packaging varies by kind; the writing principles are
shared. Aim for a predictable *process*: the agent follows the same path through
the document on every run, even when what it produces differs.

For a skill package, also read [skill mechanics](references/skill-mechanics.md)
before writing its frontmatter, choosing where it is selected, or splitting it.

## Context pointers

Text already in the agent's context that names material outside it, and says
when to fetch that material, is a **context pointer**. A skill description is
one; an `AGENTS.md` line naming a design note is another. Whether the agent ever
fetches the material, and when, depends on the pointer's wording rather than the
target's content. A required target behind vague wording is a variance bug. Fix
the wording first, and move the material inline only if a sharper pointer still
misses.

A pointer does two things: it identifies the material, and it names the
**branches** that need it. A branch is a case the document treats separately;
runs that meet different cases follow different routes through it. Name the
operation along with the target ("before importing a pack, read
`references/import.md`"); a generic "see references" list selects no branch.
When an operation must obey a rule, point to the rule before that operation,
even if the entrypoint grows.

An always-loaded pointer is paid for on every turn, so prune it harder than a
body:

- Put the leading word first. That is where triggering happens.
- Give each branch one trigger. Synonyms for one branch repeat it.
- Leave out self-description the body already provides.

## Two loads

Each document and pointer is paid for in one of two currencies:

- **Context load** is what always-present text costs the agent: a skill
  description, a line of `AGENTS.md`, any text that takes tokens and attention
  on every turn whether it applies or not.
- **Cognitive load** is what the human pays to know which documents exist and
  when each applies; the human is the index. It is what keeping a person in
  charge costs, so spend it where human judgment matters and cut it elsewhere.

A pointer moves its target out of context load at the cost of one line.
Unpointed material depends entirely on someone remembering it.

Moving text out of an entrypoint does not make it free. A path costs everything
it actually loads: the entrypoint, each reference its pointers fire, generated
role prompts, and required reads such as root and nested `AGENTS.md`. Count the
path, not the file.

## Information hierarchy

Documents hold two kinds of content. **Steps** are actions the agent takes in
order; **reference** is the definitions, rules and facts it looks up when
needed. A recipe is all steps, a set of review rules is all reference, and most
documents mix the two. Place each piece on a ladder ordered by how soon the
agent needs it:

1. **In-file steps**: the actions, in sequence. This is the primary rung.
2. **In-file reference**: consulted on demand. A flat list of peer rules on one
   rung is a sound shape, not a defect.
3. **Disclosed reference**: kept in another file and loaded only when its
   pointer fires. The file may sit beside the document or anywhere else.

The two failures pull against each other: an overloaded top buries the steps,
and aggressive disclosure hides material the agent needed.

**Progressive disclosure** demotes material to a lower rung, usually into a
separate file behind a pointer, so the steps stay readable at the top; any token
saving is a bonus. Branches give the clearest test. Keep inline whatever every
branch needs, and disclose what only some branches reach. Reference that should
be disclosed but sits among the steps makes each step easier to skip, which adds
variance as well as clutter.

**Co-location** governs what sits together once a piece has its rung. Put
everything about one concept (its definition, rules and exceptions) under one
heading, so that reading any part brings the rest along. A well co-located
section reads as the agent's documentation for that concept. Scattering splits
one meaning across places; duplication, covered under [Pruning](#pruning),
repeats it.

**Sprawl** is a document longer than its job, even when every line is current
and unique. Attention spreads thinner as length grows, and every line must be
kept true. The ladder is the remedy: move reference behind pointers, and divide
the document at branch or sequence boundaries so no path loads material it does
not use.

## Steps and completion criteria

Close each step with a **completion criterion**, an observable condition that
means the step is finished. It works through two properties.

- **Clarity**: can the agent distinguish finished from unfinished? A vague bound
  such as "once the design is understood" invites **premature completion**:
  attention moves from the work to being done, pulled by the steps still ahead.
  A clear criterion resists that pull. Sharpen the bound first; the fix is local
  and cheap. Move the later steps behind a split only when the bound cannot be
  made sharp and the rush actually appears. Hiding needs a real context
  boundary, such as a handoff or a subagent dispatch; invoking a procedure
  inline keeps the later steps in view.
- **Demand**: how much the criterion requires. "Every changed schema has a
  migration and a test" drives more **legwork**, the investigation the wording
  implies without listing it as steps, than "list the changes" does. Demand
  applies to reference as well: "every rule applied" puts the same
  exhaustiveness bar on a flat rule set that "every step done" puts on a
  sequence.

The best criteria can be checked and leave nothing out. Ending a reply is not
meeting one.

## When to split

Every split costs context load or cognitive load, so make one only when it
pays.

- **By sequence**: split when the steps after the current one pull the agent
  through it too fast; out of view, they stop competing with the work at hand.
  Merging sequences does the opposite and exposes each step to its successors.
- **By invocation**: skills only; see
  [skill mechanics](references/skill-mechanics.md#splitting-by-invocation).

## Leading words

A **leading word** is a short term for a concept the model already learned in
pretraining (_smoke test_, _blast radius_, _golden path_), one the agent reasons
with as it works. Use it repeatedly as a single token instead of re-explaining
it. The uses add up to a definition spread across the document, and the word
brings the model's existing associations with it. An invented term carries no
associations and must be defined at length, so prefer a word the model already
knows.

The word does two jobs. In a body it steers execution: the agent returns to the
same behavior wherever the word appears, and in flat reference it tells the
agent what class of problem to hunt for. A pointer uses it to steer invocation:
when the same word runs through prompts, documents and code, the agent links
that shared vocabulary to the material and finds it more dependably.

Look for restatements a leading word can replace, such as the same three
qualities listed in three places, or a pointer spending a sentence on one idea:

- "preview the change, keep its plan hash, and apply only that plan" becomes a
  _guarded_ apply;
- "the exact commit that was reviewed, whatever HEAD later becomes" becomes a
  _frozen_ revision.

Each replacement is shorter and gives the agent a firmer handle.

A leading word compresses behavior, never obligations; see
[Pruning](#pruning).

**Negation** is the matching failure. A prohibition brings the forbidden
behavior into context, which makes it likelier rather than rarer, because the
"not" is weak beside the concept it modifies. Name the target behavior instead
("stage explicit paths"), so the unwanted one never appears. Keep a prohibition
only as a guardrail that has no positive phrasing, usually an authority or
side-effect boundary such as no push without a request, and pair it with the
instruction to follow.

## Pruning

- **Single source of truth**: give each meaning one authoritative home, so
  changing a behavior means editing one place. **Duplication**, one meaning in
  several places, costs maintenance and tokens and lifts that meaning above its
  real rank. A leading word repeats a token deliberately; duplication repeats a
  meaning by accident.
- **Environment first**: scripts, config files, schemas, directory layout and
  `--help` output are authoritative too. A document that restates them is a
  **cache**, justified only when finding the fact is expensive. Record what
  looking will not reveal: an unwritten convention, the reason for a choice, a
  trap no configuration file shows. Facts a single command can reveal belong to
  the environment, which cannot fall out of date.
- **Relevance**: ask whether each line still affects how the document is
  followed. Lines fail in two ways: they never affected it (background
  exposition, or a branch that belongs behind a pointer), or the behavior they
  describe has since changed. Shorter documents stay relevant with less effort.
  Left unpruned, documents collect **sediment**: old layers nobody removes,
  because adding a line feels safe and removing one feels risky.
- **No-ops**: an instruction that matches what the model does anyway costs load
  and changes nothing. What counts as a no-op depends on the model's defaults,
  not the reader's expectations, so resolve disagreements by running the
  document. Remove the whole sentence; trimming it leaves a shorter no-op. A
  leading word that cannot move the model off its default is also a no-op
  (_check_ a claim, for a reviewer that already checks); replace it with a
  stronger word (_falsify_ the claim) rather than switching technique.
- **Obligations stay explicit**: no cut or compression removes a correctness
  requirement, an authority or side-effect boundary, or a known uncertainty.
  Replace a vague quality word with the requirement it stands for. A step with
  effects outside the workspace, such as publishing, pushing or deleting, states
  who authorizes it next to the step.

## Verify by running

These levers are authoring heuristics, not measured guarantees. Check a document
the way its agent will meet it, in proportion to the change:

- **Tabletop**: give a fresh agent the rendered instructions for one path and a
  concrete task. Its next action must be the intended one; finding the right
  keywords in the text proves nothing.
- **Reachability**: list the common paths (for a workflow: ordinary use, resume,
  a one-line fix, status only) and the files each one loads. Measure each path's
  words or bytes to expose accidental preload and duplication. Counts guide
  pruning; they never justify cutting a required rule or hiding a check.

A single `AGENTS.md` line needs only the pruning tests. A new skill or a
multi-path workflow earns a tabletop of each common path. No fixed length or
context budget applies.
