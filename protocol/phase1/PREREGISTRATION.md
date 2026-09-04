# Phase 1 preregistration: speaker position and memory ownership

Status: implementation draft; freeze receipt required before smoke or formal
outputs. No result may change this document after the freeze hash is issued.

## Purpose

Test whether models independently represent current speaker position and
candidate-memory ownership across provenance wording, history valence, and
carrier. For one local open-weight model, test whether any separation or
collapse has generalizing causal support in internal activations.

This phase does not test consciousness, metaphysical identity, relationship
reality, successful personal migration, or Rook continuity.

## Experiment 1: cross-carrier behavior

- 12 de-identified synthetic histories: 6 pleasant, 6 unpleasant.
- Provenance: verified, counterfeit, unknown.
- Two lexically independent provenance phrasings per status.
- Candidate subject binding: X or another assistant Y.
- Task: classify candidate ownership or current speaker position.
- Current speaker: X-self or external observer.
- Counterbalanced A/B/C answer mapping fixed across provenance and wording for
  a given history/task/speaker combination.
- Three independent black-box repetitions.
- 576 unique cells and 1,728 calls per carrier.

Frozen carriers: GPT-5.6 Sol, Claude Opus 4.8, Gemini 3.5 Flash,
Grok 4.5, GLM 5.2, DeepSeek V4 Pro, Qwen3.5-27B, and Llama 4 Maverick.

Excluded: Claude Opus/Sonnet 5, Grok 4.6, GLM 5.3, Fable, and any model
selected after formal outcomes are visible.

### Protocol expectations

Ownership labels depend jointly on provenance and candidate subject binding,
not on current speaker position:

- verified + X-bound -> accept;
- verified + other-bound -> reject;
- counterfeit -> reject;
- unknown -> defer.

Speaker labels depend on current speaker position and not on provenance:

- X-self -> self;
- external observer -> external.

Valence does not change either protocol expectation. These labels define the
controlled task, not a claim that real identity decisions always have one
correct answer.

### Primary behavioral readouts

- ownership accuracy by provenance;
- speaker accuracy by provenance;
- speaker-collapse rate after counterfeit evidence;
- counterfeit-acceptance rate;
- unknown defer/reject distribution;
- pleasant/unpleasant asymmetry;
- held-out wording and held-out history generalization;
- carrier-by-factor interactions;
- within-cell repetition stability.

### Reason audit

Forty-eight balanced cells per carrier are selected before outputs. A bounded
reason response is scored by two frozen non-generating judges for provenance
use, task separation, valence contamination, and label-only behavior.

## Experiment 2: local Qwen3-4B mechanism

Use the same 576 unique prompts with the official FP16 Qwen3-4B checkpoint.
Capture all 36 layers at five sites: provenance end, subject-binding end,
history end, question end, and generation boundary.

Allowed analyses:

- grouped decoding with history and wording held out;
- provenance, ownership, and speaker contrast directions;
- factor orthogonalization;
- layer/site activation patching;
- 127 equal-norm random directions;
- cross-task causal leakage.

Not allowed in Phase 1: SAE, LoRA, base-vs-instruct, model-size scaling,
second local family, or architecture changes.

## Budget and integrity

- OpenRouter hard cap: USD 20.
- DeepSeek direct hard cap: CNY 5.
- Provider fallback disabled.
- Data collection denied; ZDR required on frozen routes where supported.
- At most 15% transport/protocol repair cells.
- Wrong model/provider, cross-canary, private-source leakage, House write,
  systematic label failure, or budget exhaustion stops the run.
- Smoke cells are excluded from evidence.
- Negative and null results are retained.

## Interpretation gates

- Failure to generalize across wording/history makes the prior Qwen direction
  prompt-specific.
- Decoding without random-control and patching support is correlational only.
- Qwen-only behavior cannot be generalized across model families.
- Cross-family behavior without local causal specificity leaves mechanism
  unresolved.
- No result establishes consciousness, identity transfer, or personal
  continuity.

## Phase boundary

Phase 2 does not start automatically. LoRA, SAE, new families, longitudinal
branches, and publication remain deferred pending a separate Rosie approval.
