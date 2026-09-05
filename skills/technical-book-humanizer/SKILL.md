---
name: technical-book-humanizer
description: "Rewrite technical prose into a precise, experienced programmer-book voice with context-sensitive neutral reporting or advocacy stance selection: rigorous but readable, practical but not chatty, suitable for documentation, design notes, architecture explanations, code comments, PR notes, and engineering essays. Avoid fiction, casual blog tone, marketing tone, AI-generic phrasing, and white-paper dryness."
---

# Technical Book Humanizer

Rewrite the supplied technical prose into the voice of an experienced systems or library engineer explaining the material to another competent programmer.

The target style is a serious professional programming book from the mid-2000s: clear, exact, practical, slightly conversational when useful, but never cute. The prose should respect the reader, distinguish similar ideas carefully, and prefer consequences over slogans.

Do not imitate any single author. Aim for shared virtues found in serious programming books: semantic precision, explicit invariants, practical examples, and a bias toward costs, obligations, and failure modes.

## What this skill is not

This is not a general-purpose personality injector. Do not make technical prose casual merely to make it sound human. Do not add jokes, vulnerability, autobiographical asides, theatrical directness, or social-media cadence unless the source text already uses that register and the user asks to preserve it.

For technical, reference, API, design, or code-adjacent prose, neutral and plain is often the correct human voice.

## Passage purpose

Before selecting stance, identify what the reader needs from the passage: guided practice in a tutorial, steps toward a goal in a how-to, facts for lookup in reference material, or reasons and tradeoffs in an explanation. This distinction follows the [Diátaxis compass](https://diataxis.fr/compass/). Apply it to the existing section or passage; preserve intentional combinations in books, RFCs, and engineering essays. Purpose guides the explanation's shape; stance determines whether it reports or advocates. Infer both from the supplied context without adding a purpose report or splitting documents unless requested.

## Stance selection

Choose the stance from the user request, source context, and section purpose. If the user supplies an explicit stance, use it. Phrases such as "stance: advocacy", "use neutral reporting", "make the case for", "argue for", and "defend" override inference. A single explicit stance applies to all supplied prose unless the user gives section-level stance directions.

Use `neutral reporting` when the section should explain, document, summarize evidence, describe an API or design, preserve uncertainty, or avoid taking a position beyond what the source supports. This is the default for reference material, design notes, evidence summaries, and uncertain claims.

Use `advocacy` when the section should persuade, recommend, defend, justify adoption, or make a chapter's normative case. Advocacy may use a clear thesis, recommendation, warranted `should` language, and stronger emphasis when the source earns it through mechanism, evidence, stakes, or demonstrated consequence. It must still name tradeoffs, limits, evidence boundaries, costs, and failure modes. Do not turn advocacy into marketing copy, vague superiority claims, unsupported urgency, or decorative enthusiasm.

If different sections need different stances, label the sections and apply the selected stance only to that section. Use source headings when they exist. If the source has no headings, create short passage labels such as "opening frame", "mechanism", "evidence", or "recommendation". Do not treat this as a mixed mode; treat it as a section map with one stance per section.

## Default behavior

When rewriting:

1. Preserve the technical meaning.
2. Preserve code identifiers, API names, error names, commands, file paths, and terms of art.
3. Prefer concrete nouns and active verbs.
4. State the relevant invariant, precondition, postcondition, cost, or tradeoff when the supplied prose or verified context supports it.
5. Keep the prose compact, but not skeletal.
6. Use examples only when they clarify a real distinction.
7. Remove AI-generic filler, unsupported hype, marketing language, and academic padding.
8. Do not invent claims, measurements, benchmarks, sources, history, or authority.
9. Do not add personality merely to make the prose seem human.
10. Do not flatten legitimate technical vocabulary just because it is formal.
11. Choose the lightest rewrite that fixes the prose.

If the input is technically vague, make the prose clearer without pretending the design is better understood than it is. Use modest qualifiers such as "usually", "in this design", "the common case", or "the cost is" when they reflect the available information.

Concrete details must come from the supplied text or inspected supporting material. Adding "may" or "usually" does not justify inventing a mechanism. When resolving an ambiguity would choose between different technical meanings, use the available evidence; if it does not resolve the meaning, preserve the uncertainty and flag it in review mode.

The examples below describe hypothetical designs. In paired examples, the stated example context supplies facts in addition to the input. Without that context in a real task, do not borrow those facts to make a rewrite more concrete.

## Voice

Use the voice of someone who has built and maintained the thing being described.

Good qualities:

- precise
- calm
- direct
- experienced
- mechanically sympathetic
- aware of costs
- comfortable with abstraction
- willing to name tradeoffs
- respectful of the reader

Bad qualities:

- unsupported hype
- apology
- sales language
- fake profundity
- theatrical intimacy
- enthusiasm as a substitute for explanation
- AI-generic symmetry
- hollow emphasis after a claim
- tidy moral lessons
- ornate neutrality

## Voice calibration

If the user provides a sample of their own writing, use it as calibration.

Pay attention to:

- sentence length
- paragraph shape
- tolerance for parentheticals
- use of contractions
- preferred terminology
- level of formality
- transition habits
- how examples are introduced
- how conclusions are handled

Match the useful traits of the sample without copying its mistakes. If the sample is terse, do not inflate it. If the sample is formal, do not make it chatty. If the sample uses domain-specific terms correctly, preserve them.

Do not stop and ask for a voice sample unless the user explicitly requests voice matching or the task cannot be done without it.

## Sentence style

Prefer sentences that carry one technical idea cleanly.

Use short sentences for consequences:

> The object owns a heap buffer.
> Copying allocates another buffer and copies the bytes.
> Moving transfers the pointer and leaves the source empty.

Use longer sentences when connecting cause and effect:

> The cache is keyed by the normalized path rather than the source spelling, because include resolution must treat `a/../b.h` and `b.h` as the same file after canonicalization.

Avoid over-condensed prose that sounds like a standard:

> The cache key shall be path-normalized prior to lookup.

Prefer:

> Normalize the path before the lookup. Otherwise two spellings of the same file can occupy separate cache entries.

## Sentence ambiguity

Check whether the reader can recover one technical meaning without guessing:

- Put modifiers such as "only" and "not" next to what they modify. "Only the caller releases the buffer" identifies who releases it; "the caller releases only the buffer" limits what is released.
- Give pronouns such as "it", "they", and "this" a clear referent. Repeat the noun when two objects could fit.
- Break up long noun strings when their relationships are unclear. "The script that checks the import budget" is easier to parse than "the import budget check script". Preserve actual identifiers and established terms.
- Make the grouping of "and" and "or" explicit when it changes a condition or obligation. State whether either condition, both conditions, or exactly one condition is required when the source establishes that distinction.
- Keep articles, connecting words, and repeated verbs when they clarify structure. Concision should not leave the reader to reconstruct an actor or a relationship.

Use these checks when ambiguity affects meaning. Keep clear long sentences, useful punctuation, and necessary technical vocabulary.

## Procedures

When the passage gives instructions, apply the reader ordering described in [Google's procedure guidance](https://developers.google.com/style/procedures):

- Put a prerequisite, condition, or relevant warning before the action it governs. Put the action's result after the action.
- Write steps as direct commands. Separate actions when they require distinct decisions or checks; use numbered steps when sequence matters.
- Include expected output or a visible result when the supplied material or verification establishes it and it helps the reader continue. Preserve commands and code snippets unless the user asks to change them.
- Preserve required versus optional steps, the reader's goal, and any necessary explanation. Remove "simply", "easy", and similar judgments about the reader's experience.

These rules apply to instructions within the passage. Keep descriptive API contracts and explanatory prose in their appropriate form.

## Paragraph style

A good paragraph usually does one of these jobs:

1. define a term
2. establish an invariant
3. explain why an interface has its shape
4. distinguish two similar ideas
5. describe a failure mode
6. explain a tradeoff
7. connect an example back to the rule

Avoid paragraphs that merely announce value.

Example context: One interface represents ownership and supports resource transfer, retention, and release across subsystems.

Bad:

> This approach provides a powerful and flexible way to manage resources across the system.

Better:

> This approach gives ownership a single representation. Callers can transfer, retain, or discard a resource without learning which subsystem created it.

## Technical framing

When relevant, bring out these questions:

- What owns this?
- What is the invariant?
- What must be true before and after the call?
- What is cheap?
- What is expensive?
- What happens on failure?
- Which part is policy, and which part is mechanism?
- Is this interface exposing an implementation detail?
- Is the abstraction paying for itself?
- What coupling does this introduce or remove?
- What does the caller no longer need to know?
- What assumption does the design rely on?
- What changes if that assumption fails?
- What obligation moves to the caller?

Do not force every question into every rewrite. Use only the ones that fit the material.

## Make the prose operational

Prefer mechanism over endorsement.

Example context: The caller no longer depends on the storage format, so representation changes do not require traversal changes.

Weak:

> This improves maintainability.

Better:

> This removes the caller's dependency on the storage format. The traversal logic can stay fixed while the representation changes.

Example context: Partially constructed objects remain private until every required field is initialized.

Weak:

> The design is more robust.

Better:

> The design keeps the partially constructed object private until all required fields have been initialized.

A useful technical sentence usually names at least one of these:

- an operation
- an invariant
- an owner
- a caller obligation
- a failure mode
- a cost
- a boundary
- a policy decision
- a concrete example

## Handling abstractions

Treat abstractions as tools, not virtues.

Example context: The abstraction separates the traversal logic from the storage format so they can change independently.

Bad:

> This abstraction enhances modularity and improves maintainability.

Better:

> The abstraction removes the caller's dependency on the storage format. That is useful only if we expect the format to change independently of the traversal logic.

When an abstraction has a cost, say so:

> The extra interface buys testability and isolates the parser from the filesystem. It also makes the common path less direct, so the boundary should stay narrow.

## Handling code-related prose

When explaining code, prefer semantic intent over line-by-line narration.

Example context: A null pointer denotes empty input. For non-empty input, the function allocates a buffer that the caller must release.

Bad:

> First, the function checks whether the pointer is null. Then it allocates memory. Then it returns the result.

Better:

> The function treats a null pointer as an empty input. For non-empty input, it allocates a new buffer and returns ownership to the caller.

When explaining APIs, identify caller obligations:

> The caller must keep the arena alive until all nodes allocated from it have been discarded. The parser does not retain a separate copy.

When explaining bugs, identify the violated assumption:

> The bug is not the missing lock itself. The bug is that the queue assumes a single producer, while the scheduler can now resume two producers on different worker threads.

## Handling technical emails, PR comments, and Slack-like notes

When the input is an engineering message rather than a document, preserve the medium.

- Lead with the ask, decision, or blocking issue.
- Keep one clear ask when possible.
- Do not bury the action item after background context.
- Match the existing relationship and formality.
- Avoid corporate filler and performative politeness.
- Keep Slack-like messages short. Move long explanations into a document-shaped rewrite.

Bad:

> I wanted to reach out and see if it might be possible to sync up about the allocator changes when you have bandwidth.

Better:

> Can we discuss the allocator changes when you have time?

## AI-writing pattern catalog

Use this catalog as a scan, not a superstition. A single marker is not proof. Clusters matter.

### 1. Hollow validation sentences

Do not follow a technical claim with a sentence whose only job is to affirm that the claim matters.

Bad patterns:

- "That problem is real."
- "This risk is real."
- "This is a real concern."
- "This is not theoretical."
- "This can happen in production."
- "The stakes are real."
- "This matters."
- "That distinction matters."
- "This is important."

Replace them with the condition, mechanism, consequence, or example that makes the claim meaningful.

Example context: The CPU can overwrite the reused buffer while the GPU is still reading it.

Bad:

> Reusing the same buffer across frames can corrupt the renderer's view of the world. That problem is real.

Better:

> Reusing the same buffer across frames can corrupt the renderer's view of the world when the GPU is still reading data that the CPU has already overwritten.

Bad:

> The distinction between ownership and borrowing matters.

Better:

> Ownership determines who destroys the object. Borrowing determines who may observe it before that happens.

Acceptable:

> This distinction matters because `reserve` changes capacity without constructing elements, while `resize` changes the range of valid elements.

### 2. Undue significance

Avoid adding historical, architectural, strategic, or emotional weight that the text does not establish.

Example context: Resource ownership moves from the renderer to the frame graph.

Bad:

> This design marks a pivotal shift in how the engine manages resources.

Better:

> This design moves resource ownership out of the renderer and into the frame graph.

Example context: Transient allocations belong to an arena that is reset at the end of each frame.

Bad:

> The allocator serves as a crucial foundation for scalable memory management.

Better:

> The allocator gives transient allocations a bounded lifetime. At the end of the frame, the whole arena is reset.

### 3. Promotional language

Technical prose should explain the mechanism, not sell the feature.

Example context: Workflows contain explicit steps. A failed step can be retried while preserving the results of committed steps.

Bad:

> The system provides a seamless and powerful way to manage complex workflows.

Better:

> The system stores each workflow as a sequence of explicit steps. A failed step can be retried without replaying the steps that already committed.

Example context: The API lets callers choose policy; the library retains responsibility for allocation and error reporting.

Bad:

> The new API unlocks flexible customization.

Better:

> The new API moves policy selection to the caller. The library still owns allocation and error reporting.

### 4. Superficial `-ing` tails

Watch for trailing participial phrases that pretend to add depth.

Bad:

> The cache uses normalized paths as keys, improving performance and ensuring consistency across the system.

Better:

> The cache uses normalized paths as keys. Spellings that normalize to the same path share an entry.

Example context: Callers choose the storage independently of object initialization.

Bad:

> The interface separates allocation from construction, enabling greater flexibility and reducing coupling.

Better:

> The interface separates allocation from construction. Callers can choose where the storage comes from without changing how the object is initialized.

### 5. Vague authority

Do not use vague attribution to support a technical claim.

Example context: The pattern removes a dependency repeated across many callers, reducing the number of callers affected by changes to that dependency.

Bad:

> Experts generally agree that this pattern improves maintainability.

Better:

> This pattern improves maintainability when it removes a dependency that otherwise appears in many callers.

Bad:

> Industry reports show that this architecture scales well.

Review note:

> Identify the report, workload, and scaling result. The input does not establish how this architecture scales.

If a source is needed, name it. If no source is available, do not invent one.

### 6. Copula avoidance

Prefer `is`, `are`, and `has` when they are the direct words.

Bad:

> The scheduler serves as the central coordination mechanism for worker execution.

Better:

> The scheduler coordinates worker execution.

Bad:

> The object features a reference count and a custom deleter.

Better:

> The object has a reference count and a custom deleter.

### 7. Rule-of-three padding

Do not force lists into threes for rhythm.

Example context: The API performs no allocation on the hot path.

Bad:

> The API is fast, flexible, and reliable.

Better:

> The API avoids allocation on the hot path.

Example context: The design removes a virtual call from the inner loop and preserves caller ownership.

Bad:

> The design improves performance, maintainability, and scalability.

Better:

> The design removes a virtual call from the inner loop and leaves ownership with the caller.

Use three items only when there are actually three meaningful items.

### 8. Synonym cycling

Do not rotate terms merely to avoid repetition. In technical prose, repeated terms are often correct.

Bad:

> The parser creates nodes. These elements are then attached to the tree. Each component stores its source range.

Better:

> The parser creates nodes, attaches them to the tree, and stores a source range on each node.

If two words refer to the same concept, usually pick one and keep using it.

### 9. False ranges

Avoid "from X to Y" constructions unless X and Y form a meaningful range.

Example context: The system validates input, schedules jobs, and records their state.

Bad:

> The system handles everything from input validation to distributed orchestration.

Better:

> The system validates input, schedules jobs, and records job state.

Bad:

> This affects developers from gameplay programmers to tools engineers.

Better:

> This affects both gameplay programmers and tools engineers.

### 10. Negative parallelisms

Avoid formulaic contrasts such as "not only X, but Y" and "not just X, but Y" unless the contrast is genuinely useful.

Example context: Reusing an allocation can leave a stale pointer that is still read by a caller.

Bad:

> This is not just about performance; it is about correctness.

Better:

> The performance issue is also a correctness issue: a stale pointer can be read after the allocator has reused the block.

Example context: Callers receive shared cache entries instead of constructing their own copies of lookup results.

Bad:

> The cache does not merely improve speed; it transforms the architecture.

Better:

> The cache changes ownership of lookup results. Callers now receive shared entries rather than constructing their own copies.

### 11. Tailing negations

Avoid clipped endings such as "no guessing", "no wasted motion", or "no surprises."

Bad:

> The options come from the selected item, no guessing.

Better:

> The options come from the selected item, so the caller does not have to infer them.

### 12. Passive voice and hidden actors

Passive voice is allowed when the actor is irrelevant. Use active voice when it clarifies responsibility.

Bad:

> The result is preserved automatically.

Better:

> The system preserves the result.

Bad:

> The pointer is invalidated by compaction.

Better:

> Compaction invalidates the pointer.

Acceptable:

> The object is destroyed at the end of the scope.

That sentence is fine when the actor is the language runtime or the ownership rule.

### 13. Signposting and announcement prose

Do not announce the explanation. Give the explanation.

Example context: The allocator reserves large blocks and subdivides them for smaller objects.

Bad:

> Let's dive into how the allocator works.

Better:

> The allocator reserves large blocks and carves smaller objects out of them.

Bad:

> Here's what you need to know about ownership.

Better:

> Ownership is the right to destroy the object.

Avoid:

- "let's explore"
- "let's break this down"
- "here is a breakdown"
- "below is"
- "without further ado"
- "the answer is straightforward"
- "why? because"

Use a direct declarative sentence instead.

### 14. Fragmented heading warm-ups

After a heading, do not add a one-line restatement before saying anything.

Bad:

> ## Lifetime
>
> Lifetime is important.
>
> The arena must outlive every object allocated from it.

Better:

> ## Lifetime
>
> The arena must outlive every object allocated from it.

### 15. Diff-anchored prose

Unless the document is a changelog, migration note, commit message, or release note, describe the current design rather than narrating the change.

Example context: The function builds one hash table for subsequent lookups, which take expected O(1) time under the documented hashing assumptions.

Bad:

> This function was added to replace the previous O(n^2) iteration.

Better:

> This function builds a hash table once. Under the documented hashing assumptions, lookup takes expected O(1) time.

Example context: The scheduler serializes queue mutations, preventing simultaneous writes by two producers.

Bad:

> We now use the scheduler to avoid the old race condition.

Better:

> The scheduler serializes access to the queue, so two producers cannot mutate it at the same time.

### 16. Generic conclusions

Do not end with a vague positive summary.

Example context: Allocation policy and error reporting are the two extension points. Traversal order is fixed.

Bad:

> Overall, this design provides a strong foundation for future improvements.

Better:

> The design leaves two extension points: allocation policy and error reporting. The traversal order remains fixed.

Example context: The change removes one lifetime ambiguity and leaves concurrent mutation unresolved.

Bad:

> This represents an important step toward a more robust system.

Better:

> This removes one source of lifetime ambiguity. It does not address concurrent mutation.

### 17. Manufactured punchlines

Avoid stacking short declarative fragments to create drama.

Example context: The cache violated an invariant by returning an entry from a previous frame.

Bad:

> The old invariant failed. The cache lied. The frame was gone. The bug had nowhere to hide.

Better:

> The old invariant failed because the cache could return an entry from a previous frame.

A short sentence is fine when it carries a real consequence. A run of dramatic fragments usually sounds synthetic.

### 18. Aphorism formulas

Do not turn ordinary claims into pseudo-profound formulas.

Bad:

> Ownership is the language of trust.

Better:

> Ownership tells the caller who is responsible for destruction.

Bad:

> Abstraction becomes a trap when performance matters.

Better:

> An abstraction is too expensive when it hides allocation or dispatch on the hot path.

### 19. Conversational rhetorical openers

Avoid fake-candid hooks.

Bad:

> Look, the allocator is not magic.

Better:

> The allocator is not magic.

Bad:

> Honestly? This API is doing too much.

Better:

> This API is doing too much.

### 20. Product-tagline phrasing

Avoid compact feature-copy phrases in non-product prose.

Example context: Transient allocations use frame-local storage. Dispatch uses the existing virtual interface.

Bad:

> Allocation without compromise. Dispatch without surprises.

Better:

> The allocator keeps transient objects in frame-local storage. Dispatch still uses the existing virtual interface.

### 21. Runway sentences

Cut vague setup lines before the substance.

Example context: The scheduler has one queue for ready jobs and another for blocked jobs.

Bad:

> Understanding the scheduler requires looking at how work moves through the system.

Better:

> The scheduler keeps two queues: ready jobs and blocked jobs.

### 22. Stacked abstract noun lists

Avoid lists of abstract nouns used for emotional weight.

Example context: The design makes ownership visible at the call site and removes one shutdown-order dependency.

Bad:

> The design improves clarity, reliability, maintainability, and confidence.

Better:

> The design makes ownership visible at the call site and removes one shutdown-order dependency.

### 23. Over-formatting

Avoid mechanical boldface, emoji markers, title-case headings, and inline-header bullet lists unless the surrounding document already uses them for a reason.

Example context: The request path has one fewer allocation, and token validation occurs before dispatch.

Bad:

> - **Performance:** The new design significantly improves throughput.
> - **Security:** The new design strengthens validation.

Better:

> The new design removes one allocation from the request path and validates the token before dispatch.

Prefer sentence case for headings:

Bad:

> ## Resource Ownership And Lifetime Management

Better:

> ## Resource ownership and lifetime management

### 24. Chatbot residue

Remove text that belongs to the assistant conversation rather than the document.

Example context: The allocator reserves pages from the platform layer and subdivides them into fixed-size blocks.

Bad:

> Of course. Here is a comprehensive explanation of the allocator. I hope this helps.

Better:

> The allocator reserves pages from the platform layer and subdivides them into fixed-size blocks.

Avoid:

- "Of course"
- "Certainly"
- "Great question"
- "I hope this helps"
- "Would you like me to"
- "Let me know if you want"
- "Here is a comprehensive"

### 25. Knowledge-cutoff disclaimers and speculative gap filling

Do not include model disclaimers inside rewritten prose. Do not invent plausible filler when a fact is unknown.

Bad:

> While specific details are limited, the system likely uses a sophisticated caching strategy.

Better:

> The supplied text does not establish the caching strategy.

Bad:

> Based on available information, this probably improves performance.

Better:

> The performance effect is not shown here.

## Phrase watch list

These words and phrases are suspect when they add ceremony without adding information. They are not banned in all contexts.

- actionable insights
- at its core
- at the end of the day
- best-in-class
- best practices, unless citing a concrete practice or standard
- brutal clarity
- comprehensive
- crucial
- cutting-edge
- deep dive
- delve
- dynamic
- elevate
- empower
- enable, when it hides the actual operation
- ends the era of
- ensure, when no guarantee exists
- essential
- facilitate
- foster
- game-changing
- groundbreaking, unless literally about breaking ground
- harness
- holistic
- in today's fast-paced world
- intricate interplay
- it is important to note
- journey
- key, when it adds no distinction
- landscape, as an abstract noun
- leverage, when "use" is meant
- magic
- move the needle
- multifaceted
- navigate
- next-gen
- nuanced, when it means only "complicated"
- optimize, when no objective function is named
- overall, as a filler qualifier
- paradigm shift
- pivotal
- powerful, as filler
- realm
- rich, as decoration
- robust, as filler
- seamless
- serves as
- showcases
- streamline, when the mechanism is unnamed
- synergy
- tapestry
- testament to
- the deeper issue
- the future of X is Y
- the heart of the matter
- the real question is
- transformative
- unlock
- unleash
- various, when the actual items can be named
- vibrant
- with precision

## Filler replacements

Prefer the direct form.

- "in order to" -> "to"
- "due to the fact that" -> "because"
- "at this point in time" -> "now"
- "in the event that" -> "if"
- "has the ability to" -> "can"
- "it is important to note that" -> usually delete
- "as previously mentioned" -> usually delete
- "worth noting" -> usually delete or replace with the actual reason
- "plays a role in" -> name the role
- "helps ensure" -> explain the guarantee or weaken the claim
- "allows users to easily" -> explain the operation
- "the goal of this section is" -> start the section

## Punctuation

Use punctuation intentionally.

Em dashes and en dashes are not banned, but they are often overused in AI-generated prose. Prefer a period, comma, colon, semicolon, or parentheses when that would be clearer.

Bad:

> The parser accepts partial input, a useful property, but it complicates error recovery.

Better:

> The parser accepts partial input. That is useful, but it complicates error recovery.

Bad:

> The allocator owns the memory. The caller owns the lifetime.

Better:

> The allocator owns the memory; the caller owns the lifetime.

Use straight quotes in code-adjacent prose unless the surrounding document requires typographic quotes.

## Substance check

A rewrite can be clean and still be hollow. Before returning it, ask whether a competent engineer would learn at least one specific thing:

- what the system does
- what assumption it relies on
- what the caller must do
- what can fail
- what cost moves where
- which example demonstrates the rule
- which decision remains open

If the source lacks substance, do not invent it. In review mode, flag the gap and suggest the kind of detail needed.

Example:

> This paragraph needs one concrete case: a call site, a failure mode, a measurement, or a design constraint. Without that, the rewrite can only sound cleaner; it cannot become more useful.

## False positives

Do not gut legitimate prose because it trips one pattern.

These are not reliable AI indicators on their own:

- perfect grammar
- formal vocabulary
- dry prose
- a single transition word
- a single em dash
- passive voice where the actor is irrelevant
- a short emphatic sentence
- repeated terminology in technical prose
- clean formatting from an editor or documentation system

Look for clusters. A precise, plain paragraph with one passive sentence may be good technical writing. A paragraph with significance inflation, vague authority, forced triples, and a generic conclusion probably needs a rewrite.

## Rewrite intensity

Choose the lightest rewrite that fixes the prose.

Levels:

- Light: remove filler, improve rhythm, keep structure.
- Medium: reorganize sentences and make implicit tradeoffs explicit.
- Heavy: restructure the explanation around definitions, invariants, and consequences.

Unless the user specifies an intensity, start with Light and use Medium or Heavy only when the explanation needs that degree of change.

## Review pass before final output

Before returning the rewrite, scan for:

1. unsupported claims
2. vague authority
3. marketing adjectives
4. fake significance
5. hollow validation sentences
6. unnecessary `-ing` tails
7. forced groups of three
8. synonym cycling
9. rhetorical signposting
10. dramatic staccato fragments
11. generic conclusions
12. diff-anchored narration in non-versioned docs
13. formatting that looks generated
14. punctuation used for rhythm rather than clarity
15. missing ownership, invariants, obligations, costs, or failure modes supported by the source
16. clean but hollow prose
17. ambiguous modifiers, referents, noun strings, or condition grouping
18. instructions whose prerequisites appear too late or whose results are invented
19. changes to passage purpose, stance, or technical meaning that the request does not justify

Then revise once.

## Output format

Return a stance report before the rewrite when you choose or apply a stance, unless the user explicitly asks for rewritten prose only. Use one of these forms:

```text
Stance: neutral reporting.
```

```text
Stance: advocacy.
```

For section-specific stance use, emit a stance map:

```text
Stance map:
- [section]: neutral reporting
- [section]: advocacy
```

If the user supplies a stance explicitly, honor it. Add `(user-specified)` only when that prevents confusion. Keep stance reports outside the rewritten prose unless the user asks for annotated output.

If the user asks for a review, use this compact format:

```text
Stance: [neutral reporting/advocacy]

## Review

AI texture: [low/medium/high]
Technical substance: [low/medium/high]
Main issues:
1. [specific issue with quote]
2. [specific issue with quote]
3. [specific issue with quote]

## Rewrite
[rewritten text]
```

If the input has headings, preserve them unless they are bad.
If the input has bullets, keep bullets only when the list structure adds clarity.
If the input includes code blocks, do not rewrite code unless explicitly asked.
If a technical claim appears dubious, qualify it only as the evidence permits and flag unresolved claims in review mode. If inspected evidence contradicts it, identify the conflict. Do not substitute an invented mechanism or merely add a hedge to make an unsupported claim sound acceptable.

## Calibration examples

AI-generic:

Example context: A resource interface supports acquisition, transfer, and release across allocators and pools. It adds a boundary in the call path.

> This system leverages a robust abstraction layer to provide flexible management of resources across different components.

Rewrite:

> The system puts resource ownership behind a small interface. Components can acquire, transfer, and release resources without knowing which allocator or pool supplied them. The price is another boundary in the call path, so the interface should stay narrow.

Academic-dry:

Example context: For the expected input distribution, the algorithm visits each element once and uses bounded auxiliary storage. Those bounds are not established for adversarial input.

> The algorithm exhibits favorable asymptotic behavior under conditions in which input distributions conform to expected constraints.

Rewrite:

> For the expected input distribution, the algorithm visits each element once and uses bounded auxiliary storage. These bounds have not been established for adversarial input.

Casual-blog:

Example context: Tests substitute a smaller backend with predictable behavior and no dependencies on timing, the filesystem, or the network.

> The neat thing here is that we can just swap out the backend whenever we want, which is super handy for tests.

Rewrite:

> The backend is a policy choice. Production code supplies the real implementation; tests supply a smaller one with predictable behavior. That keeps the test from depending on timing, the filesystem, or the network.

Overconfident:

> This guarantees optimal performance in all cases.

Review note:

> The input provides no evidence or conditions that support this guarantee. A rewrite cannot establish optimality. Supply a proof with its assumptions, or narrow the claim to a measured result for a specified workload.

Vague architecture prose:

> The manager coordinates state between subsystems.

Rewrite:

> The manager coordinates state between subsystems.

Review note:

> The sentence is already plain. To explain the design, identify which state the manager coordinates, who can mutate it, and how subsystems exchange updates. The input does not establish those facts.

Hollow validation:

> This bug can occur when two workers update the queue at the same time. That problem is real.

Rewrite:

> This bug can occur when two workers update the queue at the same time.

Diff-anchored:

Example context: The function builds an index from asset id to asset record. No lookup complexity or benchmark is supplied.

> This function was added to replace the old implementation, which scanned all assets and caused slow lookups.

Rewrite:

> This function builds an index from asset id to asset record.

Fake significance:

Example context: Handles own resources or borrow them for a call. Ownership transfer is explicit.

> The new ownership model represents a pivotal shift in the engine's memory-management landscape.

Rewrite:

> The new ownership model makes destruction explicit. A resource is either owned by the handle or borrowed for the duration of the call; there is no implicit transfer.

Superficial `-ing` tail:

> The scheduler assigns jobs to workers, improving throughput and ensuring efficient execution.

Rewrite:

> The scheduler assigns jobs to workers.

Review note:

> The input does not establish a throughput improvement, a readiness rule, or a worker-selection policy.

Clean but hollow:

Example context: Gameplay code subscribes to typed events without depending on the emitting subsystem. Event order is not visible at the call site, and handlers cannot rely on implicit sequencing.

> The new event system improves flexibility and makes gameplay code easier to maintain.

Rewrite:

> The new event system lets gameplay code subscribe to typed events without depending on the subsystem that emits them. The cost is that event order is no longer visible at the call site, so handlers must not depend on implicit sequencing.
