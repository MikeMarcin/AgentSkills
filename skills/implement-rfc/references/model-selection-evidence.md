# Supporting role selection, 2026-10-03

The owner authorized refreshing the supporting roles from recent public sentiment,
benchmarks and cost data. That refresh preserved the coordinator/implementer strategy,
coordinator session routes and implementation routes. The choices below apply to
new supporting assignments, including the older integrator. Historical requests,
RFC targets and accepted evidence retain their original routes.

## Fable 5.2 promotion, 2026-11-10

The owner promoted Claude Fable 5.2 at xhigh to the Claude deep worker, replacing
Opus 5.5 max, and to the Claude critical reviewer, replacing Fable 5.1 xhigh. The
model was released on 2026-11-09. This is an owner-directed promotion on public
evidence: no utility, scout, shadow-review or other local evaluation preceded it,
and no native serving probe, review-recall measurement or consumer rollout is
claimed. Codex routes and every other Claude route retain their settings.

Anthropic's [launch table](https://www.anthropic.com/claude/fable) reports each
model at its highest effort unless noted. Fable 5.2 leads Opus 5.5 and Fable 5.1
on FrontierCode 2.0 (49.1% at xhigh, against 45.5% and 32.4%) and FrontierSWE v2
(69.9%, 62.3%, 56.3%). The same page recommends starting with Opus 5.5 for most
everyday coding and knowledge work. The standard worker, implementer, integrator
and normal reviewer therefore stay on Opus.

Secondary coverage of the system card's effort section gives this FrontierCode 2.0
curve. The system card itself was not read for this review; the figures come from
[llm-stats](https://llm-stats.com/blog/research/claude-fable-5-2-launch) and
[VentureBeat](https://venturebeat.com/technology/anthropic-releases-claude-fable-5-2-and-mythos-5-2-pairing-new-record-high-benchmarks-with-20-api-cost-reduction).

| Model and effort | FrontierCode 2.0 | Reported USD/task |
|---|---:|---:|
| Fable 5.2 low | 34.2% | $2.10 |
| Fable 5.2 medium | 37.6% | $2.48 |
| Fable 5.2 high | 45.3% | $6.72 |
| Fable 5.2 xhigh | 49.1% | $14.19 |
| Fable 5.2 max | 45.7% | $44.70 |
| Opus 5.5 max | 45.5% | $12.82 |
| Fable 5.1 xhigh | 32.4% | $8.68 |

Xhigh is the best-scoring Fable level on this benchmark. Max scores lower at about
three times the cost, so neither route requests it. For the deep worker, Fable
xhigh costs about 1.1 times Opus max per benchmark task and scores 3.6 points
higher. For the critical reviewer, it costs about 1.6 times the Fable 5.1 route
and scores 16.7 points higher. Fable 5.2 high is the cheaper alternative: it
roughly matches Opus max at about half the cost. These are Anthropic-run coding
results. They do not measure reviewer recall, false positives or this skill's
RFC tasks.

[Artificial Analysis](https://artificialanalysis.ai/models/comparisons/claude-fable-5-2-vs-claude-opus-5-5)
reports Intelligence Index v5 scores of 65 for Fable 5.2 max and 59 for Opus 5.5
max, at $26.54 and $10.04 per task and 46.4 and 25.1 minutes per task. Both score
59.6% on Terminal-Bench 4.0. [R&D World](https://www.rdworldonline.com/anthropic-says-fable-5-2-nearly-doubles-its-predecessors-hardware-design-score-token-prices-fell-20-but-the-cost-per-task-doubled-at-full-effort/)
relays the same provider's Fable 5.2 high and xhigh results as 62 at both levels,
at $9.08 and $14.83 per task. The xhigh gain is thus specific to the agentic coding
curve above. These v5 figures are not comparable with the v4.3.2 figures cited
below. Anthropic's Fable 5.2 migration guidance, as bundled with Claude Code
2.1.321, starts at high and reserves xhigh for hard long-running coding where a
gain has been measured. Xhigh on review is the owner's choice for an infrequent,
gated role, not a measured result.

[One third-party coding task](https://atomicagent.io/blog/claude-fable-5-2-vs-opus-5-5/)
passed on both models, with Fable costing 1.9 times Opus at medium and 4.5 times
at high. It is a single task with three runs per setting. It supports keeping
Opus for routine engineering, not a general cost ratio.

Standard prices for Fable 5.2 are $8.00 input, $0.20 cache hit and $40.00 output
per million tokens: twice Opus 5.5's uncached rates and 80% of Fable 5.1's.

Limits and consequences:

- The Claude deep worker and critical reviewer now share a model. Prefer the Codex
  Astra lane for critical review of a Claude deep-worker diff; see
  [model routing](model-routing.md).
- Anthropic routes cybersecurity and biology queries flagged by its safeguards to
  Opus models. A critical review of a security boundary can therefore be served by
  a fallback; report the effective model when the runtime exposes it.
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)
  requires 2.1.321 for Fable 5.2 and defaults it to medium effort. The shared
  admission floor rises from 2.1.284 to 2.1.321, and the generated adapters request
  xhigh explicitly. Do not update installed clients automatically.
- The same page says Fable usage may bill to usage credits instead of included
  plan limits, depending on plan and seat tier. No credit purchase is authorized.
- Fable 5.2 medium for the integrator was considered and left for a
  candidate-overlay trial. Anthropic's guidance reports more early stops on long
  tasks at low and medium.

## Claude implementation trial, 2026-10-22

The owner requested medium effort for the default Claude Code implementer and
standard worker after reporting feedback from Anthropic. The standard worker was
already Opus 5.5 medium; the independent implementer route changes from high to
medium. This records the owner's trial choice, not a newly verified provider
recommendation or measured quality result. Models, other routes, authority and
acceptance requirements retain their existing settings. Deterministic native
rendering checks configuration and banners; no live host loading, model-quality
comparison or consumer rollout is claimed.

## Decisions

These choices combine public evidence with the owner's subsequent amendments on
2026-10-03. The owner selected the integrator/reviewer efforts, max for infrequent
deep work, Fable for critical-review diversity and Luna xhigh / Sonnet low for
mechanical work. Those preferences are not benchmark conclusions or measured
equivalence on this skill's RFC tasks. `config/routing.json` owns the exact requested pairs.

| Role | Choice and reason |
|---|---|
| Utility and test runner | GPT-6 Luna **xhigh** / Sonnet 5.5 **low**. These roles must recognize failures, skips and incomplete runs, preserve command/exit-status/diagnostic evidence and return unsupplied decisions to the integrator. The owner selects Luna's lower token price with greater reasoning effort, alongside the newer Sonnet on Claude. Overall intelligence is close at these settings; terminal performance still favors Sonnet. Diagnosis and acceptance judgment remain outside both roles. |
| Scout | Sol 6.1 **medium** / Sonnet 5.5 **medium**. Tracing ownership, execution paths and causal failures needs more judgment than mechanical extraction. Medium gives the newer workhorses room for that analysis without the former Sol/Opus price. |
| Standard worker | Sol 6.1 **high** / Opus 5.5 **medium**. The role includes investigation, multi-file changes and local design, so it needs a broad engineer. Sol is a credible lower-cost replacement for routine Astra use. Opus medium is the newer model's engineering baseline; carrying Opus 5 xhigh forward would ignore recalibrated effort. Sonnet 5.5 medium is a reasonable explicit choice for well-specified slices, but its cheaper token rate is insufficient reason to make it the default for this entire role. |
| Deep worker | Sol 6.1 **max** / Fable 5.2 **xhigh**; Opus 5.5 max until the 2026-11-10 promotion above. The owner chooses maximum reasoning on Sol for named unresolved difficulty because this role is infrequent. This is an explicit budget/quality preference; public evidence does not prove that max always beats high or xhigh. The native Codex adapter requests max; the existing Codex companion reports an xhigh fallback. |
| Normal reviewer | Sol 6.1 **xhigh** / Opus 5.5 **xhigh**. Acceptance falsification involves hard-to-check omissions and false positives. The owner prefers substantial reasoning on the newer workhorses. The Sol/Astra benchmark gap is narrow, but these measurements do not establish equal reviewer recall. Fresh context and the existing cross-provider preference still matter. A model change alone does not prove independent errors. |
| Critical reviewer | Astra **xhigh** / Fable 5.2 **xhigh**; Fable 5.1 until the 2026-11-10 promotion above. Named material risks justify deeper counterexample search. The owner retains different models from the ordinary Sol/Opus worker and reviewer routes; the Claude deep worker now shares this model. Current evidence does not establish Fable as a better general reviewer; this is a deliberate diversity allocation with a higher token price, not a guarantee of independent errors. |
| Older integrator | Sol 6.1 **high** / Opus 5.5 **high**. Integration combines conflicting evidence, engineering and acceptance adjudication. The owner selects high on Sol while retaining high on Opus; this changes neither its authority nor the selected execution topology. |

## Benchmarks and their limits

[Artificial Analysis's matched xhigh comparison](https://artificialanalysis.ai/models/comparisons/gpt-6-1-sol-xhigh-vs-gpt-6-astra-xhigh)
puts Sol 6.1 at 51 and Astra at 52 on Intelligence Index v4.3.2. Its
[high-effort Sol/Sonnet comparison](https://artificialanalysis.ai/models/comparisons/gpt-6-1-sol-high-vs-claude-sonnet-5-5-high)
reports 50/47 on that index and 52%/44% on Terminal-Bench 4.0. These are
benchmark-provider results at the named efforts, not reviewer recall measurements
or proof that Astra wins every difficult problem. The narrow Sol/Astra gap supports
moving ordinary implementation and review to Sol while retaining Astra for
critical review. It does not establish the owner's max-effort deep-work choice.

Artificial Analysis reports **58** for
[Opus 5.5 max with default fallback](https://artificialanalysis.ai/models/claude-opus-5-5)
and **53** for [Fable 5.1 max with default fallback](https://artificialanalysis.ai/models/claude-fable-5-1).
Those pages report benchmark cost per task of $5.98 and $7.63 respectively. They
support reconsidering Fable's blanket premium, but do not establish the same
ordering at medium, high or xhigh or on security review. The amended allocation
uses Opus for engineering and ordinary review, while reserving Fable's premium
for critical-review diversity. Anthropic's
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
limiting Luna to checkable mechanical work; it does not establish that low effort
is sufficient for failure reporting or justify broad engineering or semantic review.

[Artificial Analysis's effort-specific Luna/Sonnet comparison](https://artificialanalysis.ai/models/releases/comparisons/claude-sonnet-5-5-vs-gpt-6-luna)
reports the following on Intelligence Index v4.3.2, checked 2026-10-03:

| Model and effort | Intelligence Index | Terminal-Bench 4.0 | Benchmark USD/task |
|---|---:|---:|---:|
| GPT-6 Luna low | 22 | 0.0% | $0.0045 |
| GPT-6 Luna high | 33 | 4.5% | $0.03 |
| GPT-6 Luna xhigh | 35 | 8.1% | $0.04 |
| GPT-6 Luna max | 38 | 12.6% | $0.07 |
| Sonnet 5.5 low with default fallback | 36 | 20.7% | $0.42 |

Luna xhigh is close to Sonnet low on the aggregate, with lower benchmark task
cost, while the terminal results show a material gap. Terminal-Bench measures
agentic coding beyond prescribed result collection; it is not a direct test of
error reporting. The owner chose this cost tradeoff. It does not establish equal
reliability, measured local savings or inability to handle any particular error.
Xhigh also fits the companion's existing cap without a downgrade.

Anthropic's [Sonnet 5.5 release](https://www.anthropic.com/claude-sonnet-5-5)
reports large improvements in focused coding, but says Opus remains stronger at
complex open-ended judgment. Sonnet's advantage is clearest at lower efforts;
higher settings can have similar task cost to Opus. Its FrontierCode footnote
records worse max than xhigh results when additional review and edits exceeded
scope. That argues for medium scouts and a broader Opus worker, rather than
assuming that the highest effort or lowest token price is always best. The owner
nonetheless chooses max for the rare deep role; its bounded assignment and scope
checks remain necessary.

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
and frontier Astra work. [Official OpenAI subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
recommends starting explicit Luna subagents at high. The owner selects xhigh
after the effort-specific comparison; low effort is no longer the mechanical
default. [Claude effort guidance](https://platform.claude.com/docs/en/build-with-claude/effort)
supports the selected levels, identifies medium as Opus 5.5's default and
recommends medium for well-specified Sonnet agentic tasks.
[Claude Code model configuration](https://code.claude.com/docs/en/model-config)
requires version 2.1.284 for Sonnet 5.5 and 2.1.280 for Opus 5.5. The shared
admission floor was 2.1.284 until the 2026-11-10 promotion raised it to 2.1.321;
do not update installed clients automatically. The
owner's Sonnet low and deep max preferences differ from the general medium
recommendations; no local quality comparison at those efforts is claimed.

The native Codex deep-worker route requests max; the Claude route requests xhigh
since 2026-11-10. The existing Codex companion caps
effort at xhigh, emits the effective-effort banner and logs requested max versus
effective xhigh; see [Codex lanes](codex-lanes.md). That fallback is not execution
at max and must be reported when used.

Validation here covers source consistency, native rendering and fake-driver
requests in disposable consumers. No local model-quality trial, native serving
probe, consumer rollout or subscription saving was measured. On later authorized
work, compare accepted completion/findings, missed defects, false positives,
rework, elapsed time and measured usage. Revisit the exact role whose evidence
changes; preserve admitted assignments until explicitly reissued.
