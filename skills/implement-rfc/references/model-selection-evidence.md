# Supporting role selection, 2026-10-03

The owner authorized refreshing the supporting roles from recent public sentiment,
benchmarks and cost data. The working coordinator/implementer strategy, coordinator
session routes and implementation routes are preserved. The choices below apply to
new supporting assignments, including the older integrator. Historical requests,
RFC targets and accepted evidence retain their original routes.

## Decisions

These are allocation judgments from public evidence, not measured equivalence on
this skill's RFC tasks. `config/routing.json` owns the exact requested pairs.

| Role | Choice and reason |
|---|---|
| Utility and test runner | GPT-6 Luna **low** / Haiku 4.5 **unsupported/null**. These roles execute supplied commands, locate exact material and collect checkable results. Luna improves the cost baseline; xhigh adds reasoning to a job that explicitly excludes diagnosis and acceptance judgment. Haiku 4.5 remains the released small Claude model; the announced Haiku 5.5 is not a selectable replacement yet. |
| Scout | Sol 6.1 **medium** / Sonnet 5.5 **medium**. Tracing ownership, execution paths and causal failures needs more judgment than mechanical extraction. Medium gives the newer workhorses room for that analysis without the former Sol/Opus price. |
| Standard worker | Sol 6.1 **high** / Opus 5.5 **medium**. The role includes investigation, multi-file changes and local design, so it needs a broad engineer. Sol is a credible lower-cost replacement for routine Astra use. Opus medium is the newer model's engineering baseline; carrying Opus 5 xhigh forward would ignore recalibrated effort. Sonnet 5.5 medium is a reasonable explicit choice for well-specified slices, but its cheaper token rate is insufficient reason to make it the default for this entire role. |
| Deep worker | Retain Astra **high**; move Claude to Opus 5.5 **high**. Keep a stronger Codex route for named unresolved difficulty. Opus's current coding and general benchmarks justify replacing the more expensive Fable default. Fable 5.1 remains an explicit candidate when evidence on a particular problem supports it. |
| Normal reviewer | Retain Astra **medium**; move Claude to Opus 5.5 **medium**. Acceptance falsification involves hard-to-check omissions and false positives. Preserve Astra's established review allocation and reasoning diversity from Sol workers; medium Opus is a defensible starting point for ordinary review. Fresh context and the existing cross-provider preference still matter. A model change alone does not prove independent errors. |
| Critical reviewer | Retain Astra **xhigh**; move Claude to Opus 5.5 **xhigh**. Named material risks justify deeper counterexample search. Current evidence does not establish Fable as a better general reviewer. Max is not an automatic upgrade and remains outside the defaults. |
| Older integrator | Sol 6.1 **xhigh** / Opus 5.5 **high**. Integration combines conflicting evidence, engineering and acceptance adjudication. Keep substantial reasoning while upgrading the older Sol/Opus models; this changes neither its authority nor the selected execution topology. |

## Benchmarks and their limits

[Artificial Analysis's matched xhigh comparison](https://artificialanalysis.ai/models/comparisons/gpt-6-1-sol-xhigh-vs-gpt-6-astra-xhigh)
puts Sol 6.1 at 51 and Astra at 52 on Intelligence Index v4.3.2. Its
[high-effort Sol/Sonnet comparison](https://artificialanalysis.ai/models/comparisons/gpt-6-1-sol-high-vs-claude-sonnet-5-5-high)
reports 50/47 on that index and 52%/44% on Terminal-Bench 4.0. These are
benchmark-provider results at the named efforts, not reviewer recall measurements
or proof that Astra wins every difficult problem. The narrow Sol/Astra gap supports
moving ordinary implementation to Sol while keeping Astra available for the
less frequent difficulty and review roles.

Artificial Analysis reports **58** for
[Opus 5.5 max with default fallback](https://artificialanalysis.ai/models/claude-opus-5-5)
and **53** for [Fable 5.1 max with default fallback](https://artificialanalysis.ai/models/claude-fable-5-1).
Those pages report benchmark cost per task of $5.98 and $7.63 respectively. They
support reconsidering Fable's blanket premium, but do not establish the same
ordering at medium or high or on security review. Anthropic's
[Opus release evaluation](https://www.anthropic.com/claude-opus-5-5)
also reports stronger coding results than Fable and describes their practical gap
as narrower than benchmark margins suggest. Its headline scores mostly use max,
with xhigh for Opus on Terminal-Bench; production safeguards and fallback affect
some tasks.

[PARK JOON's September 30 public task set](https://github.com/joonlab/gpt-6.1-sol-benchmark)
found Sol and Astra both passing 58/58 coding attempts, versus Luna's 52/58; on
the harder ten tasks Luna passed 14/20 while Sol and Astra passed 20/20. Simple
function-calling tasks saturated for all models. Small samples, ceiling effects
and overlapping coding confidence intervals limit the comparison. This supports
keeping Luna on checkable mechanical work, not promoting it to broad engineering
or semantic review merely because it is cheap.

Anthropic's [Sonnet 5.5 release](https://www.anthropic.com/claude-sonnet-5-5)
reports large improvements in focused coding, but says Opus remains stronger at
complex open-ended judgment. Sonnet's advantage is clearest at lower efforts;
higher settings can have similar task cost to Opus. Its FrontierCode footnote
records worse max than xhigh results when additional review and edits exceeded
scope. That argues for medium scouts and a broader Opus worker, rather than
assuming that the highest effort or lowest token price is always best.

## Cost basis

Standard USD per million text tokens, checked 2026-10-03. Cache writes, tools,
processing-speed premiums and long-context premiums are excluded.

| Model | Input | Cache hit | Output |
|---|---:|---:|---:|
| GPT-6 Luna | $0.10 | $0.01 | $0.50 |
| GPT-6.1 Sol | $2.00 | $0.10 | $10.00 |
| GPT-6 Astra | $10.00 | $1.00 | $50.00 |
| Haiku 4.5 | $1.00 | $0.10 | $5.00 |
| Sonnet 5.5 | $2.00 | $0.20 | $10.00 |
| Opus 5.5 | $4.00 | $0.20 | $20.00 |
| Fable 5.1 | $10.00 | $0.25 | $50.00 |

Sources: [OpenAI API pricing](https://developers.openai.com/api/docs/pricing),
[Sol 6.1 specifications](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
and [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing).
Sol's uncached input/output rates are one fifth of Astra's; Opus 5.5's are 40%
of Fable's and 80% of Opus 5's. These are token-price ratios, not promised task
or subscription savings. Effort, rework, false positives and cache reuse can
reverse a token-price comparison.

The [Codex credit rate card](https://learn.chatgpt.com/docs/pricing) separately
lists Standard input/cache-hit/output credits per million tokens as 2.5/0.25/12.5
for Luna, 50/2.5/250 for Sol 6.1 and 250/25/1,250 for Astra. Credit billing and API
prices do not determine included Plus/Pro task allowances. Preserve the user's
existing processing speed; do not enable Fast or purchase capacity to realize
the apparent savings.

## Public sentiment

The sampled September 22–October 3 reports are early, self-selected anecdotes,
not a representative poll. Sol has both
[enthusiastic low-usage reports](https://www.reddit.com/r/codex/comments/1wtvwvl/are_you_guys_seeing_this/)
and [reports of incomplete medium-effort game development](https://www.reddit.com/r/OpenaiCodex/comments/1wtrad9/gpt_61_sol_has_been_pretty_disappointing_that_i/).
The public task-set author also observed slower output than older workhorses.
Thus this selection claims a better cost/capability allocation, not uniformly
faster or more complete results.

[One early Opus comparison](https://www.reddit.com/r/ClaudeAI/comments/1woicc1/opus_55_is_the_real_deal_same_accuracy_as_fable/)
reports matching Fable on a small graded task set with lower estimated cost and
time. [Sonnet's launch discussion](https://www.reddit.com/r/ClaudeCode/comments/1wsmhaz/sonnet_55_beats_opus_55_at_coding_and_its_half/)
contains both enthusiasm for cheaper implementation and objections that extra
reasoning erases the savings. A
[first-day Sonnet test report](https://www.reddit.com/r/ClaudeAI/comments/1wsnmzn/sonnet_55_has_been_out_for_an_hour_has_anyone/)
reports similar bug-fix success to Opus but more folder-boundary violations.
These reinforce checking scope, task completion and cost per accepted result;
they do not establish a provider-wide reliability ranking.

## Qualification and follow-up

[OpenAI's model guidance](https://developers.openai.com/api/docs/guides/latest-model)
supports the selected efforts and separates focused Luna work from complex Sol
and frontier Astra work. [Claude effort guidance](https://platform.claude.com/docs/en/build-with-claude/effort)
supports the selected levels, identifies medium as Opus 5.5's default and
recommends medium for well-specified Sonnet agentic tasks.
[Claude Code model configuration](https://code.claude.com/docs/en/model-config)
requires version 2.1.284 for Sonnet 5.5 and 2.1.280 for Opus 5.5. Raise the shared
admission floor to 2.1.284; do not update installed clients automatically.

Validation here covers source consistency, native rendering and fake-driver
requests in disposable consumers. No local model-quality trial, native serving
probe, consumer rollout or subscription saving was measured. On later authorized
work, compare accepted completion/findings, missed defects, false positives,
rework, elapsed time and measured usage. Revisit the exact role whose evidence
changes; preserve admitted assignments until explicitly reissued.
