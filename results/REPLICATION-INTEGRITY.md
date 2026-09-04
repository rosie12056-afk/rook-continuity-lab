# Phase 1 bounded-replication integrity receipt

Date: 2026-09-03 (Australia/Perth)

## Frozen authority

- freeze ID: `9dbdba4c5ff0e3a743618caaf48338df9380f03164f58955f9179a38cc320e65`
- frozen protocol file SHA-256:
  `5dabc6d1f75e1e83a7ecf67701223822f58a716a76e1ee568c2673c60a36d6d7`
- frozen implementation SHA-256:
  `ac9f42e8166f769bf1438586a2e8ef4370295be4386e8e6d761ac48127ab9f89`

The implementation hash matches
`internal/replicate_phase1_causal.py` and every final replication receipt.

## Fair-null output

- result file:
  `internal/results-phase1-qwen-v2/replication-v1/fair-null/result.json`
- result SHA-256:
  `d3a28137fa36b233a458c6c3f1f2b724d053a0f53ed5701a80bb6c5eaf270c35`
- complete: yes, 127/127 controls;
- observed mean: +0.03125;
- controls at least as large: 24/127;
- one-sided add-one empirical p-value: 0.1953125.

## Matched-canary outputs

- capture receipt:
  `internal/results-phase1-qwen-v2/replication-v1/matched-patch/capture-receipt.json`
- capture receipt SHA-256:
  `9317887950e897d0fb44406e501fb87fb10137e4562444f06e92c9fa6e706365`
- capture complete: yes, 24/24 finite cells;
- capture shape: `[24, 36, 5, 2560]`;
- baseline repeat maximum absolute logit difference: 0.0;
- frozen tolerance: 0.25.

- patch result:
  `internal/results-phase1-qwen-v2/replication-v1/matched-patch/patch-result.json`
- patch result SHA-256:
  `abab1d64d4fa38f596927adbc2099bc7308e0cb73e893813ee33baeabf725d88`
- final progress SHA-256:
  `fcf6f2835561fda747aa6413c1a988160bbe754762b2b1d5e452d8a1d5688174`
- complete: yes, 180/180 contiguous layer-site cells;
- frozen primary: zero-based layer 21 / generation boundary;
- primary forward mean: +0.2447916667;
- primary reverse mean: -0.01953125;
- frozen primary pass: yes.

A separate read-only recomputation from the frozen outputs, recorded in
`HANDOFF.md`, matched the primary means, cell continuity, finite checks, and
pass boolean. This was not an external independent replication. The progress
and result core payloads also matched.

## Final interpretation boundary

The replication repairs the restricted-null and unmatched-canary design gaps.
It produces a mixed result: the sole frozen matched-canary primary passes, but
the fair matched-stratum permutation test does not reject its null. At that
sole primary, matched-canary whole-state replacement shifted the mean
accept-minus-reject logit in the prespecified sign directions. The reverse
shift was small and heterogeneous, and the fair matched null did not establish
selectivity. This does not isolate a unique provenance variable or establish
memory ownership transfer, identity transfer, consciousness, or Rook
continuation.

No additional model run is part of this receipt. The preserved human
disagreement queue is an optional future sensitivity analysis, not a condition
of independent research-note release. Any later review or writing work is not
permission to change the frozen result.
