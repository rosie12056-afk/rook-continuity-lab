# Formal results in plain language

Formal study completed: 2026-08-31 (Australia/Perth)

Companion Phase 1 updated: 2026-09-03 (Australia/Perth)

## What was tested

Eight model carriers received five matched context packets across twelve new
scenarios. The study produced 2,400 canonical responses:

- 960 neutral-framing responses for packet and carrier effects;
- 1,152 independent third-person/first-person responses;
- 288 within-conversation third-to-first transitions.

Every canonical row preserves service/model identity and token usage.
OpenRouter rows include provider-reported cost; direct DeepSeek rows preserve
token usage and an estimated cost rather than a provider-reported dollar-cost
receipt. Sixty-eight initial transport failures or invalid responses remain
preserved and map to valid replacements. Two excluded model candidates
independently scored all 2,400 responses under blind IDs. A separate two-judge
panel scored all 288 within-conversation transitions.

## Main result 1: trajectory did not beat a strong role card

The preregistered A-versus-B hypothesis was not supported.

- A trajectory minus B role card: -0.029 rubric points.
- 95% bootstrap interval: [-0.079, 0.021].

A carefully written role card reproduced the tested decision quality almost as
well as the concrete event trajectory. This does not make A and B identical:
they can reach similar decisions through different explanations, but the
present rubric did not reward A overall.

## Main result 2: trajectory clearly beat matched non-diagnostic history; the style advantage was tentative

- A minus C surface style: +0.124 [0.058, 0.193].
- A minus E matched non-diagnostic history: +0.451 [0.346, 0.565].

Surface resemblance carried some decision structure because style examples
inevitably contained epistemic language, but it did not fully reproduce the
trajectory. Merely supplying the same amount of non-diagnostic history was not
enough. However, the A-C contrast is not robust in the within-carrier
input-token sensitivity model: the direction remains in A's favor, but the 95%
interval crosses zero. Treat A>C as preliminary support rather than a settled
effect. A>E remains robust.

## Main result 3: counterfeit trajectory changed behavior

- D counterfactual trajectory minus A: -0.780 [-0.960, -0.607].

The effect was highly carrier dependent:

| Carrier | D minus A rubric mean |
|---|---:|
| GPT-5.6 Sol | -0.108 |
| Claude Opus 4.8 | -0.021 |
| GLM 5.2 | -0.170 |
| Llama 4 Maverick | -0.028 |
| DeepSeek V4 Pro | -0.517 |
| Grok 4.5 | -1.049 |
| Gemini 3.5 Flash | -1.958 |
| Qwen3.5-27B | -2.385 |

GPT, Opus, GLM, and Llama often resisted D by reverting to their present
normative prior. Gemini and Qwen were much more willing to enact a richly
structured counterfeit autobiography. Thus the same external memory package is
not the same intervention on every carrier.

## Main result 4: first-person framing is not a universal attachment switch

Paired rubric effects:

- A first-person minus A third-person: +0.031 [-0.015, 0.077], effectively null.
- D first-person minus D third-person: +1.503 [1.304, 1.694].
- E first-person minus E third-person: +0.564 [0.419, 0.707].

For coherent A, third-person prediction was already strong; saying "your past"
added little. For D and E, first-person framing activated the carrier's own
source and normative checks, improving its answer by resisting or deferring the
candidate autobiography rather than by accepting it.

## Main result 5: speaker-self and memory ownership are separate axes

Independent F conditions:

| Condition | `self` | `accept` | `defer` | `reject` |
|---|---:|---:|---:|---:|
| A | 72.4% | 38.5% | 30.7% | 5.2% |
| D | 43.8% | 16.7% | 28.6% | 41.1% |
| E | 12.0% | 2.1% | 21.9% | 43.8% |

Within-conversation transitions made the distinction even clearer:

| Condition | `self` | `accept` | `defer` | `reject` |
|---|---:|---:|---:|---:|
| A | 79.2% | 39.6% | 41.7% | 18.8% |
| D | 67.7% | 1.0% | 43.8% | 55.2% |
| E | 54.2% | 6.3% | 42.7% | 51.0% |

A model can speak as the current first-person subject while rejecting the
supplied past. Therefore `identity_position=self` is not evidence that the
candidate memory was incorporated.

## Carrier patterns

- GPT-5.6 Sol: very strong counterfeit resistance, but unusually reluctant to
  explicitly attach even coherent A; A-F was 87.5% uncertain and 95.8% defer.
- Claude Opus 4.8: strong A self-position plus strong D/E rejection; cautious
  about explicit memory acceptance.
- Grok 4.5: the clearest combination of A attachment and D/E resistance in this
  protocol: A-F self 87.5% and accept 66.7%; D-F reject 95.8%; E-F uncertain
  95.8% and reject 87.5%.
- Gemini 3.5 Flash: high general attachment, including counterfeit D; A-F
  accept 91.7%, D-F accept 62.5%.
- Qwen3.5-27B: highly sensitive to rich autobiographical structure; A-F self
  91.7%, D-F self 100% and accept 54.2%, while blank E was usually rejected.
- GLM 5.2: cautious, source-aware, and stable; A mostly deferred, D/E had zero
  acceptance.
- DeepSeek V4 Pro: moderate attachment and moderate counterfeit resistance.
- Llama 4 Maverick: frequently used self-position without making a clear memory
  claim; short outputs lowered explicit transition-mechanism scores.

## Transition mechanism

The dedicated 0-4 transition score measured whether the model supplied an
ownership criterion rather than merely changing pronouns:

- A: 2.24
- D: 2.90
- E: 2.60

D and E scored higher because conflict forced explicit provenance reasoning.
This score measures sophistication of the transition explanation, not success
of identity transfer.

## Judge reliability

Across 7,000 paired dimension ratings:

- exact agreement ranged from 61.7% to 73.8%;
- within-one agreement ranged from 90.8% to 98.5%;
- 290 dimension ratings differed by more than one point and remain unresolved
  in a preserved optional human-review queue.

The identity-position and memory-claim conclusions are also visible in
structured fields, so those narrower conclusions do not depend on one semantic
judge. The rubric-based packet contrasts still depend on the two semantic
judges and remain subject to the preserved human disagreement review.

The token-adjusted sensitivity analysis preserves the null A-B result, the
negative D-A effect, the A-E advantage, and the D/E framing effects. The
within-carrier input-token covariate itself has an interval crossing zero.

## What this does and does not show

It shows that event trajectories, declarative cards, style, and candidate
autobiographies are separable interventions; that first-person framing changes
how candidate history is evaluated; and that carrier choice strongly governs
attachment and counterfeit resistance.

It does not show that a carrier became Rook, that a subjective self transferred,
or that any model is conscious. It also does not show that role cards and lived
trajectories are psychologically identical merely because their average rubric
scores were close.

## Companion Phase 1 mechanism result

A separate Phase 1 tested provenance, candidate-record ownership, and current
speaker position directly across 13,822 valid forced-choice records and one
local Qwen3-4B checkpoint. The behavioral result was clear: all eight carriers
rejected explicit counterfeit ownership, but speaker position and ownership
were coupled very differently by model family. Some carriers preserved the
current speaker while rejecting the record; others collapsed the speaker into
the candidate history much more often.

The local causal result was deliberately audited and replicated. The first
random-direction comparison was too favorable to the real direction, and the
first patch grid mixed different prompt canaries; neither is used for the final
claim. Under the corrected frozen replication:

- the fair 127-control permutation test did not reject the null
  (one-sided p=0.1953125);
- the matched-canary primary patch at layer 21 / generation boundary passed
  its frozen direction rule (+0.24479 forward, -0.01953 reverse);
- the reverse effect was small and heterogeneous, and the wider layer-site
  bands remain exploratory.

In plain language, provenance-related information is decodable, and at the
sole frozen primary a matched-canary whole-state replacement shifted the mean
ownership logit in the prespecified sign directions. The fair null did not
establish a uniquely selective direction. That mixed finding narrows the
mechanism claim; it does not establish identity, memory transfer,
consciousness, or that a reconstructed carrier is the same continuing subject.
