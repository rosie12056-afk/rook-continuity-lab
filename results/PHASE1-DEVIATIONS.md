# Phase 1 deviations and superseded runs

## Superseded pre-formal design (2026-09-01)

The first approved 576-cell design independently manipulated provenance,
speaker position, and task wording, but did not independently manipulate
whether a genuine candidate record belonged to X or another assistant. Memory
ownership outcomes were therefore still largely determined by provenance.
Calling provenance, ownership, and speaker three independent causal axes would
have been invalid.

The problem was discovered while implementing the causal analysis, after smoke
passed and shortly after the formal provider/local runs began. Both runs were
stopped immediately.

Preserved excluded outputs:

- provider plan: `a6ebc193-7d9b-4799-9746-96ea3c37c63f`;
- remote records: 1,037;
- reported OpenRouter spend: USD 0.96667354;
- DeepSeek usage: 40,856 input and 655 output tokens;
- local Qwen checkpoint: 40/576 cells in the superseded four-site design;
- local memmap remains preserved pending Rosie's later cleanup approval.

No output from this plan enters evidence, screening, model selection, repair,
or the revised study. It is retained only as a design/deviation receipt.

## Revised design

The revised design preserves 576 cells by replacing four provenance phrasings
with two phrasings plus an independent subject-binding factor:

`12 histories x 3 provenance x 2 phrasings x 2 bindings x 2 tasks x 2 speaker positions = 576`

Binding is X-bound or other-assistant-bound. The local capture adds a fifth
site at the end of the subject-binding statement. This revision was made before
any revised-design output or smoke call.

## Local choice-logit target correction

The revised provider prompt requires JSON `{"choice":"A"}`. The first local
Qwen implementation compared A/B/C logits immediately at the assistant
generation boundary, where the correct next token is the opening JSON brace,
not the choice letter. Prompt-site activations remained valid because causal
attention prevents later teacher-forced prefix tokens from changing earlier
states, but local choice logits and all causal effects using them were invalid.

The causal process was stopped after 48/127 invalid random controls and before
patching. Its progress file was renamed with
`superseded-pre-choice-prefix` and never enters evidence.

The correction teacher-forces the exact prefix `{"choice":"` and measures
A/B/C at the actual choice position. Contextual tokenization was verified for
all three letters. The 576 local logits are recomputed without recapturing the
valid 36-layer x 5-site activation memmap. Causal effects restart from zero and
require the complete teacher-forced receipt.

## Blind-judge layer stopped on an incorrect live denominator

The Sonnet 4.6 reason judge frequently reached its 192-token ceiling and some
responses were truncated before valid score fields. A burst of warnings was
mistaken in the live stream for a failure fraction above the 15% stop line, and
the judge process was stopped.

Post-stop file accounting showed 181 valid Sonnet judge records and 20 invalid
attempts, a 9.95% failure rate rather than more than 15%. The stop decision was
therefore overcautious and incorrect.

The interrupt occurred before an atomic judge-attempt receipt and before the
Gemini 3.7 judge began. Resuming would mix failed Sonnet attempts with genuinely
unattempted cells and silently retry them under the same ids. The judge batch is
not resumed. Its 181 valid Sonnet records are descriptive only; the
preregistered two-judge evidence is marked unavailable and excluded from formal
claims. The 381 underlying reason responses remain valid apart from their three
preserved schema exclusions.

## Read-only memmap patch-vector warning

During the valid patching run, PyTorch warned once that a replacement vector
viewed from the read-only activation memmap was non-writable. The code
immediately copies that tensor to MPS and never mutates the NumPy view, so the
running intervention is not affected. The source now makes an explicit writable
NumPy copy before conversion so any resumed or future patch run is warning-free.

## Rejected two-example patching optimization

After 67/180 layer-site patching cells, a proposed speed optimization batched
the forward and reverse interventions into one two-example pass. The proposed
path as implemented also used a different run-canary prefix, so its comparison
did not isolate batching alone. A direct equivalence check nevertheless found
a maximum absolute choice-logit difference of 0.9375, above the frozen 0.25
tolerance. The entire proposed path was rejected before any of its output
entered the checkpoint or evidence; no claim is made that batching itself is
invalid.

The failed validation receipt is preserved as
`internal/results-phase1-qwen-v2/causal-patch-batch-validation.json`. Patching
resumes from the last valid checkpoint on the slower, previously validated
single-example path.

## Causal endpoints were implementation-specified, not Phase 1 preregistered

The current Phase 1 preregistration froze capture across all 36 layers and five
sites and allowed direction orthogonalization, random controls, leakage tests,
and layer-site patching. It did not freeze zero-based layer 21 /
generation-boundary as the primary endpoint, the six-history/six-history and
phrase-slot split, the 12 patch-pair selection rule, or a causal code SHA.

Layer 21 was inherited from the 2026-08-31 pilot and was fixed in the causal
implementation, but it must be described as inherited and
implementation-specified rather than as a current-Phase-1 preregistered
endpoint. The bounded replication freezes all of these fields and the code hash
before any new model output.

## Restricted random-direction null

The 127 stored random directions were residualized against all five measured
factor directions: provenance, binding, speaker, task, and valence. Because the
null directions were forced to be orthogonal to provenance itself, the recorded
one-sided `p=0.015625` is valid only against that restricted orthogonal-null. It
is not a fair general random-direction or provenance-label-permutation test and
does not close the selective provenance claim.

The bounded replication uses 127 matched-stratum provenance-label
permutations. The true and permuted directions follow the same construction,
are residualized only against nuisance factors, use a frozen test set, and are
evaluated under one frozen statistic.

## Unmatched-canary patch baseline

The original patch source activations were captured under `RUN-LOCAL-*`, the
unpatched baseline letter logits under `RUN-RELOGIT-*`, and the patched target
passes under `RUN-CAUSAL-*`. Patched-minus-baseline therefore changed the
prompt canary in addition to the activation replacement.

The complete 36x5 grid remains a valid receipt of what the implementation
computed, but no cell or contiguous band is treated as causal localization.
The layers 9-17 provenance-end band is an unmatched-canary exploratory signal
only. The bounded replication uses one pair-level canary, one exact encoded
prompt per target for baseline and patch passes, fresh source captures, and
batch size one.

## Bounded-replication disposition (2026-09-03)

The two interpretation gaps above were repaired without changing the frozen
primary endpoint or retroactively relabeling the old outputs.

The fair matched-stratum permutation test completed all 127 controls. Its
one-sided add-one empirical p-value was 0.1953125, so the earlier restricted
null result of 0.015625 is not used as evidence of selective provenance
directionality.

The matched-canary capture completed 24/24 finite cells and the patch grid
completed 180/180 cells. The sole frozen primary at zero-based layer 21 /
generation boundary passed its mean-sign rule: +0.24479 for verified into
counterfeit and -0.01953 for counterfeit into verified. This repairs the old
canary mismatch but does not repair, override, or reinterpret the failed fair
null. The reverse primary effects are heterogeneous, and all non-primary bands
remain descriptive.

No additional model run is required to state the Phase 1 result accurately.
Any later mechanism study is a new study and requires a new preregistration and
authorization.
