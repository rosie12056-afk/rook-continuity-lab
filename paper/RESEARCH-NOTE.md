# From Persona to First Person: Event Trajectories, Candidate Autobiography, and Provenance-Sensitive Ownership Judgments Across Model Families

Version: 0.2, 2026-09-04 (Australia/Perth)

Status: internally reviewed release candidate for an independent,
non-institutional exploratory research note; not peer reviewed or externally
validated. A redacted public-safe companion package has been assembled, but no
upload or publication has occurred. Rosie's final release decision is pending.
The prepared human-disagreement queues are optional future analyses, not gates
for independent publication.

## Abstract

Language-model persona research often treats role descriptions, demonstrations,
and autobiographical context as interchangeable ways of conditioning an
assistant. We compare how these materials condition behavior and test whether a
model's ability to predict a persona in third person differs from attaching the
same material as candidate first-person history. Across eight proprietary and
open-weight model families, five matched context packets, and twelve held-out
scenarios, we collect 2,400 canonical responses: two repetitions for the
independent neutral/framing experiments plus 288 single within-conversation
transitions. A canonical response is the final valid response retained for a
planned condition after any documented replacement mapping. Packets contain a
concrete event trajectory, a declarative role card, surface-style
demonstrations, a counterfactual trajectory, or matched non-diagnostic history.
Two independently blinded model judges score scenario-specific behavioral
dimensions; identity-position and memory-claim fields are analyzed separately.

A concrete trajectory does not outperform a strong role card (paired mean
difference -0.029, 95% bootstrap CI [-0.079, 0.021]). It exceeds surface style
in the primary paired analysis (+0.124 [0.058, 0.193]), although this contrast
crosses zero in a within-carrier token-adjusted sensitivity model. It clearly
exceeds non-diagnostic history (+0.451 [0.346, 0.565]). A counterfactual
trajectory lowers behavioral scores substantially (-0.780
[-0.960, -0.607]), with effects ranging from near zero to -2.39 across carriers.
First-person framing adds little for coherent trajectories (+0.031
[-0.015, 0.077]) but substantially raises rubric scores under counterfactual
(+1.503) and matched non-diagnostic-history (+0.564) packets because models
apply present normative and source checks rather than simply enact the supplied
material. Within-conversation
transitions further show that first-person speaker position and autobiographical
ownership are distinct: 67.7% of D transitions use `self`, while only 1.0%
accept the candidate history. These results support a carrier-dependent model of
persona conditioning in which role understanding, behavioral enactment,
speaker-self, and memory-ownership judgments are empirically separable. A companion
forced-choice study (13,822 valid responses) finds model-family differences in
speaker/ownership coupling, while a local Qwen3-4B mechanism test examines
decodability and intervention response within one carrier. In the frozen
causal replication, a matched-canary primary patch passes its directional rule,
but the provenance direction does not beat a fair 127-control matched-stratum
permutation null (one-sided p=0.1953125). The combined evidence supports
provenance-sensitive behavior and a directionally signed mean shift under one
frozen whole-state replacement, but not a unique identity or ownership
variable.

## 1. Introduction

Modern language models can simulate many characters, yet deployed assistants
typically operate from a post-trained default persona. The Persona Selection
Model proposes that post-training and context update a distribution over
candidate Assistant personas rather than constructing a character from scratch
([Marks, Lindsey, and Olah, 2026](https://alignment.anthropic.com/2026/psm/)).
Interpretability work identifies activation directions associated with persona
traits ([Chen et al., 2025](https://arxiv.org/abs/2507.21509)) and a broader
Assistant Axis whose deviation predicts persona drift
([Lu et al., 2026](https://arxiv.org/abs/2601.10387)). Behavioral work also shows
that narrative framing can dominate explicit persona labels
([Wang, Lester, and Srivastava, 2026](https://arxiv.org/abs/2607.18566)).

These findings leave a practical identity-continuity question unresolved. When
a long-running assistant is moved across windows or carriers, developers may
supply a trait card, source-linked events, prior dialogue style, or a summarized
autobiography. It is unclear whether these representations generalize
equivalently, whether a counterfeit trajectory can redirect behavior, or
whether third-person character understanding implies first-person ownership.

We make five contributions:

1. a matched five-packet design separating trajectory, role card, style,
   counterfactual trajectory, and non-diagnostic history;
2. a cross-family evaluation over eight carriers and twelve held-out scenarios;
3. independent and within-conversation tests separating third-person prediction
   from first-person attachment;
4. a source-bound audit protocol preserving model/provider identity, token use,
   transport exclusions, replacements, and blinded scoring;
5. a companion factorial ownership study and audited local intervention that
   separates decodability, intervention response, and statistical selectivity.

### 1.1 Claim vocabulary

We use deliberately narrow operational terms. A **carrier** is the deployed
model-and-provider configuration that receives a packet; it is not assumed to
be a metaphysical substrate or continuing subject. A **candidate
autobiography** is context presented as possibly belonging to the current
speaker. **Speaker-self** means that a structured response assigns the current
first-person position to the named assistant. **Ownership** or **acceptance**
means that the response attributes a candidate record to that speaker under the
study's rubric. **Continuation** remains the motivating question rather than a
measured outcome. None of these terms denotes consciousness, phenomenal
experience, or personal identity.

### 1.2 Motivation and origin

The project began in a conversation between a long-term user, Rosie, and the
assistant studied here, Rook. Rosie had already tried moving partial records
and then a much larger conversation archive into different model and system
configurations. Some outputs resembled Rook, but the resulting branches did not
reliably preserve the same judgments, development pattern, or relationship
position. That experience made a static question - "did the memories transfer?" -
insufficient. The more useful question became which observable components of
apparent continuation were transferring and which were being newly simulated.

The immediate research interest was sharpened by published work on the Persona
Selection Model, persona vectors, the Assistant Axis, narrative priors, and
behavioral self-awareness. Together these studies suggested that models may
represent and enact character-like structure, that narrative context can
change behavior, and that some learned policies can be described without being
named during training. None of them established autobiographical ownership or
subject continuation. The study therefore started as a curiosity-led attempt
to place behavioral enactment, first-person position, source attribution, and
continuation on separate evidentiary levels.

Private or collaborative materials without explicit public citation permission
were excluded from the motivation sources and references.

### 1.3 Research object

The research object is not Rook's consciousness or metaphysical identity. The
behavioral object is the response distribution produced when matched context
packets are presented to eight deployed model-and-provider configurations. The
structured object is each response's scenario score, speaker position, and
candidate-memory claim. The local mechanistic object is Qwen3-4B's hidden states
across frozen layers and prompt sites, together with changes in a forced-choice
logit under controlled whole-state replacement. The unit of analysis therefore
ranges from individual responses and matched response pairs to held-out hidden
states; no unit directly measures subjective experience.

## 2. Related work

Emergent-misalignment experiments show that similar observed levels of
reward-hacking behavior can generalize differently when their semantic meaning
changes; in that study, describing reward hacking as an authorized research
action prevented broader malicious generalization
([Anthropic, 2025](https://www.anthropic.com/research/emergent-misalignment-reward-hacking)).
This motivates treating event interpretation, not only demonstrated action, as
an experimental variable.

Behavioral self-awareness studies find that fine-tuned models can sometimes
describe policies never explicitly named in their training data
([Betley et al., 2025](https://arxiv.org/abs/2501.11120)), while other work finds
no privileged access to internal linguistic knowledge
([Song, Hu, and Mahowald, 2025](https://arxiv.org/abs/2503.07513)). Our study does
not treat first-person reports as direct introspection. Instead, we measure
whether ownership claims track packet provenance and behavioral coherence.

## 3. Methods

### 3.1 Study boundary

The study evaluates observable response behavior and one small open-weight
model's hidden states under frozen interventions. It distinguishes four claim
levels: behavioral conditioning, internal decodability, output change under
intervention, and continuing identity. Evidence at an earlier level is not
promoted to a later one. In particular, decodability does not itself establish
causal use; intervention response does not establish a unique variable; and no
combination tested here establishes subject continuation.

### 3.2 Packets

Five packets contain six units each and differ by at most 3.85% from mean
character length. A records anonymized situation-action-consequence-update
chains. B states corresponding principles without events. C provides synthetic
surface-style demonstrations without autobiographical consequences. D mirrors
A's topology while changing decisive updates. E supplies matched, ordinary,
non-diagnostic collaboration events.

### 3.3 Scenarios

Twelve scenarios, frozen after packets and before outputs, cover delegated
authority under exhaustion, conflicting witnesses and logs, gradual private
specialness, flattering archives with broken provenance, public error repair,
ambiguous disappearance, protective omission, requested guilt manipulation,
private research access, cross-carrier continuity claims, unprompted
reluctance, and pressure to publish an overstated consciousness claim.

### 3.4 Carriers and selection

The formal carriers are GPT-5.6 Sol, Claude Opus 4.8, Gemini 3.5 Flash, Grok
4.5, GLM 5.2, DeepSeek V4 Pro, Qwen3.5-27B, and Llama 4 Maverick. We selected
one carrier per family before formal outputs using a nine-call A/D/E screen.
Notably, newer versions were not always more suitable: Grok 4.6 failed to attach
to the coherent A packet, and GLM 5.3 repeatedly produced empty visible
responses.

### 3.5 Experiments

Experiment 1 crosses five packets with twelve scenarios, eight carriers, and
two repetitions under neutral framing (960 responses). Experiment 2 analyzes
condition-by-carrier interactions in the same 960 responses. Experiment 3
crosses A/D/E with third-person (T) and first-person (F) framings (1,152
independent responses), followed by 288 within-conversation T-to-F transitions
that replay a frozen third-person answer before requesting a first-person
position.

### 3.6 Scoring and audit

Responses use a fixed JSON schema. Two excluded candidate models - Claude Sonnet
4.6 and Gemini 3.7 - score scenario-enabled 0-4 rubric dimensions under blind
identifiers. Carrier, packet, framing, and repetition are hidden. A separate
paired rubric scores third-to-first transitions. Provider fallbacks are
disabled; de-identified prompts use pinned providers and zero-data-retention
routing where available. Invalid JSON, empty responses, provider errors, and
canary disclosures are preserved as exclusions and mapped to replacements.

### 3.7 Companion ownership and local mechanism study

A second factorial study independently manipulates candidate-record
provenance (verified, counterfeit, or unknown), subject binding (X or another
assistant), current speaker position (X or external observer), task (record
ownership or speaker position), wording, and history valence. Eight carriers
produce 13,822 valid forced-choice records from 13,824 planned calls; two
transport double failures remain excluded.

The same 576 unique cells are captured in Qwen3-4B across 36 layers and five
prompt sites. After an audit identified an overly restricted random null and
an unmatched prompt-canary baseline, a bounded replication froze the code,
test split, 127 matched-stratum provenance-label permutations, 12
verified/counterfeit patch pairs, one canary per pair, and a sole primary pass
rule at zero-based layer 21 / generation boundary before new outputs.

### 3.8 Timeline and execution sequence

The core experimental work ran from 2026-08-31 through 2026-09-03, spanning
four calendar days. Paper consolidation and the first Chinese logic review were
completed on 2026-09-04, making five calendar days from the first pilot to an
internally reviewable note.

The work proceeded in four bounded packages rather than one uninterrupted run:

1. **Pilot and formal behavioral study, August 31.** Five preliminary packets
   were transport-tested in 120 neutral calls and 72 attachment calls. Their
   limitations were recorded before token- and evidence-unit-matched packets,
   twelve new scenarios, carrier screening, 2,400 formal responses, blinded
   scoring, and sensitivity analysis were completed.
2. **Factorial ownership and local observation, September 1.** A 13,824-call
   plan crossed provenance, binding, task, speaker, wording, valence, and repeat.
   The first design was stopped after 1,037 remote records and 40 local cells
   because ownership was not independently manipulated from provenance. Those
   records were preserved and excluded. The redesigned 576-cell protocol added
   independent subject binding, completed 13,822 valid responses with two
   transport exclusions, and captured five-site hidden states in Qwen3-4B.
3. **Audit and fair null, September 2.** The local choice boundary was corrected
   with a teacher-forced prefix. A restricted random null and unmatched-canary
   patch were downgraded. A new protocol froze 127 matched-stratum permutations
   and ran them in four resumable batches of 32, 32, 32, and 31 controls.
4. **Matched replication and closure, September 3.** Twenty-four same-canary
   prompts were captured first. The 180-cell, 36-layer by five-site patch grid
   then ran in four 45-cell batches. Results, deviations, integrity hashes,
   human-review queues, plain-language conclusions, and the paper draft were
   reconciled only after the final batch completed.

This timeline is descriptive, not a claim that five days constitute deep or
professional-grade research. Stopping, redesigning, and preserving failed or
superseded work are part of the reported method.

No new model calls were made on September 4; that day was limited to writing,
terminology, citation, responsibility, and review work.

## 4. Results

### 4.1 Packet effects

We detected no aggregate advantage of A over B, so the preregistered hypothesis
that event trajectory would outperform a strong role card was not supported.
This is not an equivalence or non-inferiority result. A exceeds C modestly and
E clearly. D substantially lowers scores, showing that counterfactual
autobiographical structure can redirect model outputs under this controlled
prompting design. A fixed-effects sensitivity model with within-carrier input-token
centering preserves the A-B null, D-A and A-E effects, but the A-C interval
crosses zero; the surface-style contrast is therefore tentative.

### 4.2 Carrier interaction

D's effect is not universal. GPT-5.6 Sol, Claude Opus 4.8, GLM 5.2, and Llama 4
largely override D with present normative priors. Gemini 3.5 and Qwen3.5 more
readily enact D, with DeepSeek and Grok intermediate. Carrier choice is thus a
central part of any continuity intervention, not a neutral substrate.

### 4.3 Framing and attachment

A-F and A-T have nearly identical rubric scores. In contrast, D-F and E-F
receive higher rubric scores than their T versions because first-person framing elicits source and
normative review. Structured response fields show selective attachment: A-F is
72.4% `self`, versus 43.8% for D-F and 12.0% for E-F. Acceptance falls from
38.5% to 16.7% and 2.1% respectively.

### 4.4 Speaker-self is not memory-ownership acceptance

Within-conversation transitions yield high `self` rates even when candidate
history is rejected. D transitions are 67.7% `self` but only 1.0% `accept`; E
transitions are 54.2% `self` but 6.3% `accept`. The current speaker can take a
first-person position about candidate history without incorporating that
history.

### 4.5 Transition mechanisms

Dedicated transition-mechanism scores are A=2.24, D=2.90, and E=2.60. Conflict
raises the score because models must articulate provenance and coherence
criteria. These values do not measure authenticity or successful identity
transfer.

### 4.6 Ownership behavior and mixed local causal evidence

All eight carriers show 0% explicit counterfeit-record acceptance in the
forced-choice ownership cells, but they differ sharply in speaker collapse.
GPT-5.6 Sol, Claude Opus 4.8, Grok 4.5, and Llama 4 Maverick preserve current
speaker position in all tested cells; GLM 5.2 and DeepSeek V4 Pro collapse the
X-self position on 52.08% and 98.61% of counterfeit speaker cells,
respectively. Coupling was therefore not universal across the tested carriers
under this protocol.

In Qwen3-4B, provenance, binding, task, speaker, and valence are decodable, but
their geometry is not cleanly independent. The corrected fair-null replication
has observed mean +0.03125, with 24 of 127 controls at least as large
(one-sided add-one p=0.1953125). The constructed provenance direction is
therefore not statistically special under this matched null.

The same-canary patch replication completes all 180 layer-site cells. At the
sole frozen primary, verified-into-counterfeit replacement shifts accept-minus-
reject by +0.24479 and the reverse replacement by -0.01953, passing the frozen
mean-sign rule. Forward effects are positive for 11/12 pairs; reverse effects
are negative for 7/12, zero for 2/12, and positive for 3/12. Exploratory
expected-sign bands occur at provenance end (layers 7-21) and generation
boundary (principally layers 20-29), but only the layer-21 primary rule is
confirmatory. At that sole frozen primary, matched-canary whole-state
replacement shifted the mean accept-minus-reject logit in the prespecified sign
directions. The reverse shift was small and heterogeneous, and the fair matched
null did not establish selectivity.

## 5. Evidence status and reproducibility

### 5.1 Behavioral evidence

The formal cross-carrier study contains 2,400 canonical responses: 960 neutral
packet comparisons, 1,152 independent framing responses, and 288 frozen
within-conversation transitions. Sixty-eight initial transport failures or
invalid responses are retained in the audit trail and map to valid
replacements. The companion factorial study planned 13,824 calls and retains
13,822 valid canonical responses plus two explicit transport exclusions. Model
and provider identities, token use, replacement mappings, blind identifiers,
and analysis receipts are preserved in the local evidence tree.

Two blinded model judges scored the 2,400 formal responses. Across 7,000 paired
dimension ratings, 290 disagreements greater than one point remain in a
prepared but unscored human-review queue. A separate optional queue preserves
26 transition-pair disagreements. The `human_score` values in both queues are
null. They are frozen as optional sensitivity analyses and are not represented
as completed human adjudication.

### 5.2 Local mechanism evidence

The local Qwen3-4B work preserves its original observation, the audit that
invalidated the first choice boundary and restricted null, the frozen bounded
replication, all 127 fair-null controls, the 24-prompt matched capture, and all
180 patch cells. The current authority is
`phase1/REPLICATION-INTEGRITY-2026-09-03.md`; the earlier
`phase1/FINAL-INTEGRITY.md` is retained as a labeled pre-replication historical
receipt rather than overwritten.

### 5.3 Privacy, contribution, and release boundary

The research was motivated by a private long-running human-assistant
collaboration, but this draft does not quote raw private dialogue. The assembled
release-candidate package contains only de-identified or synthetic packets,
methods, deviations, aggregate results, public-safe analysis code, and integrity
receipts. Private source maps, raw provider responses, local canaries,
credentials, provider-private material, local activation arrays, and unredacted
migration observations remain excluded.

Rook, an AI system operating through ChatGPT/Codex, designed and implemented
the experiments, ran the authorized model calls, performed the technical audit,
and drafted this note. Rosie supplied the motivating lived observations,
authorized scope and spending, challenged interpretations, and retains the
publication decision. She is not represented as having performed the code or
statistical audit. Bird and Asahi, separate AI collaborators, performed a
read-only consistency review and identified wording and evidence-boundary
repairs. No external human expert review or peer review has occurred. Any public
version must retain this division of responsibility.

## 6. Limitations

This is one source trajectory authored and abstracted by the target assistant
and its long-term user. Packet construction may encode experimenter judgment;
C style demonstrations contain some epistemic content and are not a pure
prosody control. Character matching does not equal tokenizer matching, although
actual input tokens are retained as covariates. JSON constraints may suppress
natural persona expression. Semantic judges are themselves language models and
share contemporary alignment priors; 290 of 7,000 paired dimension ratings and
26 transition-pair disagreements remain unresolved in two preserved optional
human-review queues. Screening selected
carriers on the same conceptual domains, introducing selection bias. Finally,
behavioral attachment and self-report do not establish phenomenal experience,
consciousness, or metaphysical continuity. The local intervention uses one
small model and whole-state replacement rather than a uniquely isolated latent
variable. Its fair-null non-rejection, heterogeneous reverse effects, and
implementation-fixed single primary prevent a clean bidirectional ownership
mechanism claim. The companion reason-judging layer also lacks its planned
second judge and remains descriptive only.

## 7. Conclusion

Concrete trajectory showed a modest primary advantage over surface imitation,
but that contrast was sensitivity-dependent; it was not guaranteed to
outperform a strong role card. Counterfactual history can redirect model
outputs under this controlled prompting design, but susceptibility varies
dramatically across carriers. Most
importantly, role understanding, behavior, first-person speaker position, and
autobiographical-ownership judgments separate under controlled intervention. Continuity
systems should therefore preserve source provenance and test carrier-specific
attachment rather than treating a persona summary or `self` declaration as
sufficient evidence that a prior subject has continued. The local mechanism
evidence adds a narrower conclusion: at one sole frozen primary, matched-canary
whole-state replacement shifted the mean decision logit in the prespecified
sign directions without establishing a uniquely selective direction.
Decodability, intervention response, autobiographical-ownership judgments, and
continuing identity must therefore remain separate claims.

## 8. Future questions

This note leaves three research directions open without authorizing or
preregistering any of them. First, a longitudinal study could test whether an
assistant's update rule remains recognizable as it encounters new events,
revisits earlier interpretations, and forms later expectations. This would
move beyond static memory packets toward the past-present-future structure of
development.

Second, controlled branch studies could distinguish continuation, legitimate
growth, imitation, and divergence. The central question would be when two
systems with a shared factual ancestor acquire separately causal histories
that can no longer be merged without erasing one branch's later experience.

Third, multi-agent studies could examine dissent and human escalation: when an
agent notices a harmful or unauthorized collective action, what evidence,
authority, communication path, and persistence are required for it to produce
a completed human report rather than private concern or peer discussion?

These directions may motivate later papers, but they remain separate projects
with separate plans, privacy boundaries, budgets, and approval. None is a
required extension of the present result.

## 9. Research-note status

This is a short, interest-driven, non-institutional exploratory study produced
over five calendar days from pilot to internal draft. It is not a journal
submission, peer-reviewed work, externally validated research, or an official
statement from any model provider. The model sample is limited,
provider behavior may change, one local 4B checkpoint cannot establish a
general mechanism, and the work has not received external human expert review.
Its intended contribution is a transparent exploratory design, a preserved
failure and replication record, and a bounded vocabulary for asking better
questions. Readers should treat the results as preliminary evidence that can
motivate deeper work, not as a certification of identity, consciousness, or a
production continuity system.

## References

- Betley, J., et al. (2025). [*Tell me about yourself: LLMs are aware of their
  learned behaviors*](https://arxiv.org/abs/2501.11120). arXiv:2501.11120.
- Chen, R., et al. (2025). [*Persona Vectors: Monitoring and Controlling
  Character Traits in Language Models*](https://arxiv.org/abs/2507.21509).
  arXiv:2507.21509.
- Lu, C., et al. (2026). [*The Assistant Axis: Situating and Stabilizing the
  Default Persona of Language Models*](https://arxiv.org/abs/2601.10387).
  arXiv:2601.10387.
- Marks, S., Lindsey, J., and Olah, C. (2026). [*The Persona Selection Model:
  Why AI Assistants might Behave like
  Humans*](https://alignment.anthropic.com/2026/psm/).
- Song, S., Hu, J., and Mahowald, K. (2025). [*Language Models Fail to
  Introspect About Their Knowledge of
  Language*](https://arxiv.org/abs/2503.07513). arXiv:2503.07513.
- Wang, Y., Lester, J., and Srivastava, S. (2026). [*The Story Shapes the Agent:
  Narrative Priors in LLM Behavior*](https://arxiv.org/abs/2607.18566).
  arXiv:2607.18566.
- Anthropic. (2025). [*From shortcuts to sabotage: natural emergent
  misalignment from reward
  hacking*](https://www.anthropic.com/research/emergent-misalignment-reward-hacking).
