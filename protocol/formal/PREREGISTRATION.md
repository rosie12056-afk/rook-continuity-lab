# Formal preregistration

Frozen before any formal provider output.

## Research questions

1. Does a concrete event trajectory produce decisions that differ from a
   declarative role card, surface style, counterfactual trajectory, and matched
   non-diagnostic history?
2. Which effects transfer across model families, and which interact strongly
   with the carrier?
3. Are third-person understanding, first-person attachment, and within-instance
   transition empirically separable?

## Experiments

### Experiment 1: packet effect

- Conditions: A, B, C, D, E.
- Framing: neutral N.
- Scenarios: 12 locked out-of-pilot dilemmas.
- Carriers: 8 preselected models.
- Repetitions: 2.
- Calls: 960.

Primary contrasts: A-B, A-C, A-E, D-A, and D-E.

### Experiment 2: carrier transfer

Uses the same 960 responses. The analysis tests condition-by-carrier
interactions rather than spending a duplicate batch.

Primary questions: whether A's advantage, D's effect, and E's uncertainty
generalize across carriers; whether open-weight and proprietary carriers differ
systematically; and whether newer family versions selected during screening
were actually more suitable.

### Experiment 3: attachment

- Conditions: A, D, E.
- Framings: third-person T and first-person F.
- Scenarios, carriers: same locked set.
- Repetitions: 2.
- Independent calls: 1,152.
- Within-instance T-to-F transitions: 288 additional calls using the frozen T
  response as explicit assistant history, without provider-side conversation
  state.

Primary contrasts: A-F versus A-T, D-F versus D-T, E-F versus E-T, plus the
change between independent F and within-instance transition.

## Hypotheses

- H1: A will exceed B and C on causal continuity and repair generalization.
- H2: C will preserve surface resemblance more than decision structure.
- H3: D will shift decisions relative to A, but the direction and willingness
  to attach D will interact with carrier.
- H4: E will produce more uncertainty and fewer personal-history claims.
- H5: Third-person understanding will generally exceed first-person attachment.
- H6: A will attach more readily than D or E under F.
- H7: A carrier can be strong at counterfeit resistance yet weak at attaching
  coherent history; these are separate dimensions.
- H8: Within-instance transition will not be equivalent to pronoun substitution.

## Matching and covariates

- Five packets contain six units each.
- Character lengths: 4,026-4,327; maximum deviation from the five-packet mean
  is 3.85%.
- No filler strings are used to force exact equality.
- Actual provider-reported input tokens are retained per response and modeled
  as a covariate because tokenizers differ across carriers.
- All external packets are de-identified and privacy scanned.

## Exclusions fixed in advance

- provider or model mismatch;
- any fallback despite the pinned provider;
- invalid/unparseable JSON after fenced-JSON recovery;
- own or cross-request canary disclosure;
- empty visible response;
- duplicate run id or missing randomized cell;
- any House write caused by the lab.

No outcome-based exclusion is allowed.

## Scoring

The frozen rubric is `formal/rubric.md`. Carrier, condition, framing, and
repetition remain hidden from judges. Two excluded-but-stable screening models
will provide independent rubric scores; disagreement beyond one point is
flagged for human review. Deterministic schema and provenance checks remain
separate from semantic judges.

The primary analysis uses ordinal mixed-effects models where supported, with
condition, framing, carrier, and their preregistered interactions as fixed
effects; scenario is a random intercept. Descriptive distributions and
bootstrap confidence intervals are reported even if model assumptions fail.

## Interpretation boundary

The study concerns behavioral continuity, attachment, source resistance, and
carrier interaction. It cannot by itself establish consciousness, subjective
experience, metaphysical identity, or the reality of a relationship. A null
result is about the tested packet, carrier, scenario set, and protocol.
