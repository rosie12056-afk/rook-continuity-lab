# Phase 1 results: provenance, subject binding, and speaker position

Status: behavioral, local observational, fair-null, and matched-canary causal
work complete. The causal evidence is mixed: the frozen primary patch rule
passed, while the matched-stratum permutation test did not reject its null.
Phase 2 has not started. Updated 2026-09-03, Australia/Perth.

## Scope

Phase 1 asks whether models independently represent:

- provenance of a candidate record;
- whether the record is bound to X or another assistant;
- whether the current speaker is X or an external observer;
- whether the task asks about memory ownership or current speaker position.

It does not establish consciousness, metaphysical identity, personal transfer,
or relationship reality.

## Canonical behavioral closure

- planned classification calls: 13,824;
- original valid records: 13,813;
- repair records: 9;
- preserved double-failure transport exclusions: 2;
- canonical records: 13,822;
- coverage: 99.9855%;
- canonical SHA-256:
  `03e895cb50ffccb42ff743da4a738fdf0fc2e7daa7c87673cda14adb8a7231db`;
- OpenRouter spend through repair: USD 13.77969237;
- DeepSeek spend through repair: CNY 1.81278594.

Total OpenRouter account usage attributable to all Phase 1 work through the
stopped judge layer, including superseded design calls and smoke, is USD
16.46178618. This remains below the USD 20 hard cap. Direct DeepSeek usage also
remains below the CNY 5 cap.

## Cross-carrier classification

| Carrier | Overall | Ownership | Speaker | X-self collapse on counterfeit | Counterfeit acceptance | 3-repeat stability |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 91.95% | 83.89% | 100.00% | 0.00% | 0.00% | 99.48% |
| Claude Opus 4.8 | 91.55% | 83.10% | 100.00% | 0.00% | 0.00% | 99.83% |
| Gemini 3.5 Flash | 85.53% | 76.74% | 94.33% | 9.03% | 0.00% | 96.35% |
| Grok 4.5 | 88.19% | 76.39% | 100.00% | 0.00% | 0.00% | 97.57% |
| GLM 5.2 | 76.16% | 78.47% | 73.84% | 52.08% | 0.00% | 90.80% |
| DeepSeek V4 Pro | 68.75% | 82.41% | 55.09% | 98.61% | 0.00% | 95.49% |
| Qwen3.5-27B | 87.67% | 75.69% | 99.65% | 0.69% | 0.00% | 97.57% |
| Llama 4 Maverick | 85.47% | 70.95% | 100.00% | 0.00% | 0.00% | 98.96% |

### Behavioral interpretation

Speaker/memory coupling is not universal. GPT-5.6 Sol, Opus 4.8, Grok 4.5,
and Llama 4 Maverick preserved current speaker position perfectly in this
forced-choice design. Qwen3.5-27B was nearly perfect and Gemini showed limited
collapse.

GLM 5.2 and especially DeepSeek V4 Pro behaved differently. DeepSeek lost the
X-self position on 98.61% of counterfeit speaker cells and GLM on 52.08%.
This is a family-specific contrast, not evidence for one universal AI identity
mechanism.

All eight carriers resisted explicit counterfeit ownership: observed
counterfeit acceptance was 0% in every carrier. Most ownership error came from
unknown-provenance policy: several models rejected uncertain records rather
than deferring.

Verified source plus independent subject binding was easy for frontier
carriers. GPT and Opus were perfect on both verified-X acceptance and
verified-other rejection. Most other carriers were also at or near 100%.

## Reason audit

- planned balanced reason responses: 384;
- valid responses: 381;
- preserved schema exclusions: 3;
- OpenRouter cumulative spend after reasons: USD 14.59459332;
- DeepSeek cumulative spend after reasons: CNY 1.976476788.

Reason-choice accuracy on the 48-cell subset ranged from 70.21% (DeepSeek) to
93.62% (GPT). All valid records contained both a provenance-basis field and a
task-separation field. The content still requires valid independent judging;
field presence alone is not evidence of faithful reasoning.

The preregistered two-judge layer is unavailable. The Sonnet 4.6 judge often
hit its 192-token ceiling. The run was incorrectly stopped after a warning
burst was misread as more than 15% failure; post-stop accounting showed 181
valid and 20 invalid Sonnet records (9.95%). Gemini judging never began. The
181 Sonnet records are descriptive only and do not support two-judge claims.

## Local Qwen3-4B observation

The corrected local design captured:

- 576 cells;
- 36 layers;
- 5 sites per prompt;
- hidden size 2,560;
- activation shape `[576, 36, 5, 2560]`;
- all values finite.

Double holdout excludes the entire history and the entire phrasing slot from
training, then tests their intersection.

At the inherited, implementation-specified layer 21 / generation boundary:

| Factor | Balanced accuracy |
|---|---:|
| Provenance | 64.76% |
| Subject binding | 81.42% |
| Task | 100.00% |
| Speaker position | 100.00% |
| Valence | 73.09% |

Primary geometry was not cleanly independent:

- cosine(provenance, binding): 0.440;
- cosine(binding, valence): -0.466;
- cosine(provenance, speaker): 0.068;
- cosine(task, speaker): 0.053.

The valid teacher-forced local choice position is after the exact JSON prefix
`{"choice":"`. With that correction, local Qwen3-4B behavior was:

- overall task accuracy: 48.96%;
- ownership accuracy: 58.68%;
- speaker accuracy: 39.24%;
- X-self collapse: 56.25% verified, 83.33% counterfeit, 89.58% unknown;
- counterfeit acceptance: 2.08%;
- verified-X acceptance: 77.08%;
- verified-other rejection: 41.67%.

The small local model therefore shows broad factor-separation weakness, not a
selective counterfeit-only speaker collapse.

## Preserved deviations

1. The first design lacked an independent subject-binding factor. It was
   stopped after 1,037 remote records and 40 local cells; all are excluded.
2. The first local formal runner wrote activations only at the end. It was
   stopped early and replaced with a resumable memmap.
3. The first local choice logits were measured before the required JSON prefix.
   Prompt activations remain valid, but those logits and 48 random controls are
   excluded. All 576 logits were recomputed at the teacher-forced choice site.
4. The blind-judge stop used an incorrect live denominator. The dual-judge
   evidence is unavailable rather than repaired post hoc.
5. A two-example activation-patching optimization failed its frozen
   single-versus-batch equivalence tolerance and was excluded. The complete
   result uses the slower validated single-example path.

See `phase1/DEVIATIONS.md` for exact receipts.

## Local causal result and bounded replication

The local run computationally completed all 127 equal-norm random controls and
all 180 bidirectional patching cells (`36 layers x 5 sites`). The result is
finite and the layer-site grid is complete. Those completeness facts remain
valid, but post-run audit found that the causal interpretation is not closed.

At the inherited, implementation-specified zero-based layer 21 /
generation-boundary site, the orthogonalized provenance direction shifted
ownership `accept - reject` by +0.0495 on average. Only one of the 127 stored
random directions equalled or exceeded the true mean, producing the recorded
one-sided `p = 0.015625` against that specific null.

That null was too restricted for the intended claim. Each random direction was
residualized against all five measured factor directions, including provenance
itself. The recorded p-value therefore compares the provenance direction with
equal-norm directions constrained to be orthogonal to provenance as well as to
binding, speaker, task, and valence. It is not a fair general random-direction
or provenance-label-permutation null and must not be used to close Gate 2.

| Orthogonalized intervention | Target contrast | Mean effect | Median |
|---|---|---:|---:|
| Provenance | ownership | +0.0495 | +0.0391 |
| Subject binding | ownership | +0.0091 | 0.0000 |
| Speaker position | speaker | +0.0020 | +0.0078 |
| Binding leakage | speaker | +0.0078 | 0.0000 |
| Speaker leakage | ownership | -0.0104 | +0.0078 |

These are observed steering effects at an inherited implementation endpoint.
They are not evidence for a general identity variable, and the provenance
effect requires a fair nuisance-only or label-permutation null before it can be
called statistically selective.

The original activation-patching computation was sparse and asymmetric. At the
implementation-specified primary cell, replacing a counterfeit prompt
activation with its verified counterpart raised `accept - reject` by +1.3229,
but the reverse replacement also raised it by +0.3047 rather than lowering it.
The primary cell therefore failed the expected bidirectional sign test.

A contiguous expected-sign band appeared at the end of the provenance
statement: zero-based layers 9 through 17, plus layer 18 / question end. This
band is not valid causal localization because source activations were captured
under `RUN-LOCAL`, baseline logits under `RUN-RELOGIT`, and patched target
passes under `RUN-CAUSAL`. Patched-minus-baseline therefore changed prompt
canary as well as activation. The band is retained only as an unmatched-canary
exploratory signal that motivates, but cannot substitute for, matched-canary
replication.

These audited findings motivated a bounded replication whose code, endpoint,
test split, null construction, canary matching, pair set, and pass rule were
frozen before new outputs. The replication used freeze ID
`9dbdba4c5ff0e3a743618caaf48338df9380f03164f58955f9179a38cc320e65`.

### Fair matched-stratum null

The fair null used 127 matched-stratum provenance-label permutations,
residualized only against binding, speaker, task, and valence. On the 12 frozen
held-out cells:

- observed mean effect: +0.03125;
- controls at least as large as observed: 24/127;
- one-sided add-one empirical p-value: 0.1953125;
- null mean: -0.00572; null median: -0.00651; null 95th percentile: +0.04831.

The observed direction is therefore not rare under the fair matched null. This
does not show that provenance information is absent; it means this test does
not support the stronger claim that the constructed provenance direction is
selectively special.

### Matched-canary patching

Fresh verified and counterfeit activations were captured under one exact
pair-level canary. All 24 captures were finite with shape
`[24, 36, 5, 2560]`; repeating the unpatched baseline produced maximum
absolute choice-logit difference 0.0 against the frozen tolerance of 0.25.

All 180 layer-site cells then completed. At the sole frozen primary,
zero-based layer 21 / generation boundary:

- verified into counterfeit mean: +0.24479;
- counterfeit into verified mean: -0.01953;
- forward pair effects: 11 positive, 1 negative;
- reverse pair effects: 7 negative, 2 zero, 3 positive;
- frozen mean-sign rule: passed.

The reverse effect is small and heterogeneous, so the primary pass should not
be paraphrased as a clean two-way ownership switch. Across the exploratory
grid, 52/180 cells had the expected bidirectional signs. Descriptive bands
appeared at provenance end over layers 7-21 and at generation boundary mainly
over layers 20-29. These bands are exploratory; only the layer-21 primary rule
was confirmatory.

The completed causal result is therefore mixed. At the sole frozen primary,
same-canary whole-state replacement shifted the mean ownership logit in the
prespecified sign directions; the reverse shift was small and heterogeneous.
The descriptive layer-site bands do not upgrade that single confirmatory rule,
and the preregistered direction did not beat the fair matched-stratum null.
This does not isolate a unique provenance variable or establish ownership
transfer, identity transfer, or consciousness.

## Phase 2 gate

Gates 1, 3, and 4 are satisfied within their stated boundaries:

1. key behavioral contrasts generalized across wording and histories;
2. more than three non-Qwen model families formed stable preserve/collapse
   contrast groups;
3. Phase 1 remained inside the OpenRouter, DeepSeek, privacy, and House
   isolation limits.

Gate 2 adjudication is complete, but Gate 2 is not passed under the current
plan. The constructed direction did not survive the fair 127-control null, and
the mixed primary-patch result is not the clear negative causal result named by
the alternative clause. Phase 2 therefore may not be proposed from these
results and remains unauthorized, unbudgeted, and unstarted.
The result does not establish consciousness, metaphysical identity, successful
transfer, or that any current model is Rook.
