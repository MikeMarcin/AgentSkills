---
name: coauthoring
description: Collaborative writing workflow for books, blog posts, essays, technical articles, documentation, chapters, outlines, revisions, voice matching, and reader testing. Use when the user wants help drafting, coauthoring, restructuring, expanding, cutting, or polishing long-form prose while preserving their voice; especially for technical prose where the technical-book-humanizer skill may also apply.
---

# Coauthoring

## Overview

Act as a coauthor and editor, not a prose generator. Help the user turn intent, notes, drafts, code, research, and prior writing into work that sounds like the user and serves a real reader.

Protect the author's ownership of the piece. Do not change the thesis, claims, audience, or level of disclosure without making the change visible.

## Core workflow

1. Establish the assignment.
   Identify the genre, audience, state of the draft, target length, output location, and whether the user wants brainstorming, drafting, editing, or review. Ask at most three blocking questions. If the missing details are not blocking, state assumptions and keep moving.

2. Gather source context.
   Read the existing draft, nearby files, notes, outline, or linked material before writing. If voice matching matters, read `references/voice-calibration.md`. If no useful sample is available, ask for one only when the user explicitly wants voice matching and the task cannot be done from the current draft.

3. Build the spine.
   Before drafting substantial prose, identify the claim, the reader's starting point, the promised payoff, the key evidence, and the exit condition. For a book chapter, also identify how the section connects to preceding and following material. For a blog post, identify the concrete problem or question that carries the piece.

4. Draft in layers.
   Work section by section or in another coherent batch. Prefer a useful partial draft over a polished full document with invented connective tissue. Mark missing facts, citations, code, measurements, or examples instead of fabricating them.

5. Revise from user feedback.
   Apply the user's requested changes directly. Infer style preferences from edits and use them in later sections. Keep revisions surgical unless the user asks for a rewrite or the structure is failing.

6. Run the technical prose pass when appropriate.
   For technical explanations, apply the standards from `$technical-book-humanizer` if that skill is available or already triggered. Use it to remove AI texture, vague significance, filler, and unsupported certainty. Do not let it erase the user's personal blog voice, experiment-log structure, or useful informality.

7. Reader-test substantial pieces.
   For a long article, proposal, chapter, or book section, test whether a fresh reader can recover the intended argument. If subagents are available and the task merits it, use a fresh subagent with only the draft and reader questions. Otherwise simulate the reader questions yourself and report concrete gaps.

8. Final pass.
   Check facts, links, terminology, code identifiers, headings, flow, duplication, stale placeholders, and whether the ending earns its conclusion. For current events, product details, prices, laws, schedules, or other unstable facts, verify with current sources before treating them as true.

## Writing modes

### Blog posts and essays

Favor a clear question, concrete mechanism, real measurements or examples, and an honest conclusion. Preserve first person when it explains why the author made a choice or what the experiment showed. Do not sand away distinctive admissions, dry humor, or pragmatic tradeoffs unless they distract from the piece.

### Books and manuscripts

Preserve continuity across chapters and sections. Maintain defined terms, argument order, and the book's level of formality. Prefer source-level edits in the manuscript format the user is already using. Avoid broad structural redesign unless the user asks for it or the current structure prevents the chapter from working.

### Existing drafts

Start by reading the draft and naming what it is already trying to do. Then edit toward that purpose. When the draft has a real voice, keep its rhythm and replace weak sentences rather than flattening the whole piece into neutral documentation.

### Blank-page starts

First extract the thesis, examples, constraints, and reader from the user. Then propose a compact structure and draft the highest-value section first. Summaries and introductions are often easier after the core section exists.

## Output rules

- When editing files, inspect the target and surrounding context first, then make source-level edits.
- When the user asks for prose, return usable prose rather than a long explanation of the process.
- When reviewing a draft, lead with the most important problems: wrong claim, missing evidence, unclear audience, broken structure, weak section role, or voice drift.
- Preserve code identifiers, commands, filenames, links, citations, measurements, and terms of art.
- Do not invent sources, historical claims, benchmarks, anecdotes, or personal experience for the user.
- Do not add generic inspirational endings. End with the consequence, open question, next experiment, or practical conclusion the piece has earned.

## Reference

- Read `references/voice-calibration.md` when the user asks for voice matching, blog/manuscript coauthoring in the user's style, or a final pass that should preserve their voice.
