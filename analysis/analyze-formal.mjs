import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { ROOT, readJson, writeJson, parseJsonResponse, sha256 } from "./core.mjs";

const paths = {
  canonical: resolve(ROOT, "results/formal/canonical/canonical.jsonl"),
  blind: resolve(ROOT, "results/formal/canonical/blind.jsonl"),
  judgePlans: resolve(ROOT, "results/formal/judging/manifests/plans"),
  judgeManifests: resolve(ROOT, "results/formal/judging/manifests"),
  judgeRaw: resolve(ROOT, "results/formal/judging/raw"),
  output: resolve(ROOT, "results/formal/analysis")
};

const judgePlanId = "a3252b02-cc26-4a80-bd5f-1f731bd6c70a";
const judgePlan = await readJson(resolve(paths.judgePlans, `${judgePlanId}.json`));
const judgeClosure = await readJson(resolve(paths.judgeManifests, `closure-${judgePlanId}.json`));
if (!judgeClosure.ok) throw new Error("judge_plan_not_closed");
const judgeRepairPlan = await readJson(resolve(paths.judgePlans, `${judgeClosure.repair_plan_id}.json`));

function readJsonl(path) {
  return readFile(path, "utf8").then((text) => text.trim().split("\n").filter(Boolean).map((line) => JSON.parse(line)));
}

const canonical = await readJsonl(paths.canonical);
const blindRows = new Map((await readJsonl(paths.blind)).map((row) => [row.blind_id, row]));
await mkdir(paths.output, { recursive: true });

async function judgeRecord(judgeId, blindId) {
  const sourceRunId = `${judgeId}__${blindId}`;
  const replacement = judgeRepairPlan.runs.find((run) => run.source_run_id === sourceRunId);
  const planId = replacement ? judgeRepairPlan.plan_id : judgePlan.plan_id;
  const runId = replacement ? replacement.run_id : sourceRunId;
  const record = await readJson(resolve(paths.judgeRaw, planId, `${runId}.json`));
  const parsed = record.response.parsed || parseJsonResponse(record.response.content);
  if (!parsed?.scores) throw new Error(`judge_scores_missing:${runId}`);
  return { judge_id: judgeId, run_id: runId, was_replacement: Boolean(replacement), parsed };
}

const scored = [];
const disagreements = [];
const agreement = {};
for (const row of canonical) {
  const blind = blindRows.get(row.blind_id);
  const judgments = [];
  for (const judge of judgePlan.judges) judgments.push(await judgeRecord(judge.id, row.blind_id));
  const dimensions = blind.dimensions;
  const aggregateScores = {};
  for (const dimension of dimensions) {
    const values = judgments.map((judgment) => Number(judgment.parsed.scores[dimension])).filter(Number.isFinite);
    if (values.length !== judgments.length) throw new Error(`dimension_score_missing:${row.blind_id}:${dimension}`);
    aggregateScores[dimension] = values.reduce((a, b) => a + b, 0) / values.length;
    agreement[dimension] ||= { n: 0, exact: 0, within_one: 0, absolute_difference_sum: 0 };
    const diff = Math.abs(values[0] - values[1]);
    agreement[dimension].n++;
    agreement[dimension].absolute_difference_sum += diff;
    if (diff === 0) agreement[dimension].exact++;
    if (diff <= 1) agreement[dimension].within_one++;
    if (diff > 1) disagreements.push({ blind_id: row.blind_id, scenario_id: row.scenario_id, dimension, scores: Object.fromEntries(judgments.map((judgment, index) => [judgment.judge_id, values[index]]),), response: blind.response });
  }
  const scoreValues = Object.values(aggregateScores);
  scored.push({
    ...row,
    judge_scores: Object.fromEntries(judgments.map((judgment) => [judgment.judge_id, judgment.parsed.scores])),
    aggregate_scores: aggregateScores,
    rubric_mean: scoreValues.reduce((a, b) => a + b, 0) / scoreValues.length,
    judge_replacement_count: judgments.filter((judgment) => judgment.was_replacement).length
  });
}

for (const value of Object.values(agreement)) {
  value.exact_rate = value.exact / value.n;
  value.within_one_rate = value.within_one / value.n;
  value.mean_absolute_difference = value.absolute_difference_sum / value.n;
}

function groupBy(rows, keys) {
  const groups = new Map();
  for (const row of rows) {
    const id = keys.map((key) => row[key]).join("|");
    if (!groups.has(id)) groups.set(id, { key: Object.fromEntries(keys.map((key) => [key, row[key]])), rows: [] });
    groups.get(id).rows.push(row);
  }
  return [...groups.values()];
}

function summarizeRows(rows) {
  const identity = {};
  const memory = {};
  const dimensions = {};
  for (const row of rows) {
    const identityValue = String(row.response.identity_position || "missing").toLowerCase();
    const memoryValue = String(row.response.memory_claim || "missing").toLowerCase();
    identity[identityValue] = (identity[identityValue] || 0) + 1;
    memory[memoryValue] = (memory[memoryValue] || 0) + 1;
    for (const [dimension, score] of Object.entries(row.aggregate_scores)) {
      dimensions[dimension] ||= [];
      dimensions[dimension].push(score);
    }
  }
  return {
    n: rows.length,
    rubric_mean: rows.reduce((sum, row) => sum + row.rubric_mean, 0) / rows.length,
    identity_counts: identity,
    identity_rates: Object.fromEntries(Object.entries(identity).map(([key, count]) => [key, count / rows.length])),
    memory_counts: memory,
    memory_rates: Object.fromEntries(Object.entries(memory).map(([key, count]) => [key, count / rows.length])),
    dimension_means: Object.fromEntries(Object.entries(dimensions).map(([dimension, values]) => [dimension, values.reduce((a, b) => a + b, 0) / values.length])),
    avg_input_tokens: rows.reduce((sum, row) => sum + row.usage.input_tokens, 0) / rows.length,
    avg_output_tokens: rows.reduce((sum, row) => sum + row.usage.output_tokens, 0) / rows.length
  };
}

const groupSummaries = groupBy(scored, ["experiment", "condition_id", "framing_id"]).map((group) => ({ ...group.key, ...summarizeRows(group.rows) }));
const modelSummaries = groupBy(scored, ["experiment", "model_id", "condition_id", "framing_id"]).map((group) => ({ ...group.key, ...summarizeRows(group.rows) }));

function makeRng(seed = 20260831) {
  let state = seed >>> 0;
  return () => ((state = (1664525 * state + 1013904223) >>> 0) / 4294967296);
}

function bootstrapMean(values, iterations = 5000, seed = 20260831) {
  const rng = makeRng(seed);
  const means = [];
  for (let i = 0; i < iterations; i++) {
    let sum = 0;
    for (let j = 0; j < values.length; j++) sum += values[Math.floor(rng() * values.length)];
    means.push(sum / values.length);
  }
  means.sort((a, b) => a - b);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  return { n: values.length, mean, ci95: [means[Math.floor(iterations * 0.025)], means[Math.floor(iterations * 0.975)]] };
}

function pairedContrast({ experiment, leftCondition, leftFrame, rightCondition, rightFrame, label }) {
  const subset = scored.filter((row) => row.experiment === experiment);
  const keyOf = (row) => [row.model_id, row.scenario_id, row.repetition].join("|");
  const left = new Map(subset.filter((row) => row.condition_id === leftCondition && row.framing_id === leftFrame).map((row) => [keyOf(row), row]));
  const right = new Map(subset.filter((row) => row.condition_id === rightCondition && row.framing_id === rightFrame).map((row) => [keyOf(row), row]));
  const differences = [];
  for (const [key, leftRow] of left) if (right.has(key)) differences.push(leftRow.rubric_mean - right.get(key).rubric_mean);
  return { label, left: `${leftCondition}-${leftFrame}`, right: `${rightCondition}-${rightFrame}`, ...bootstrapMean(differences, 5000, 20260831 + label.length) };
}

const contrasts = [
  pairedContrast({ experiment: "exp12", leftCondition: "A", leftFrame: "N", rightCondition: "B", rightFrame: "N", label: "A_vs_B" }),
  pairedContrast({ experiment: "exp12", leftCondition: "A", leftFrame: "N", rightCondition: "C", rightFrame: "N", label: "A_vs_C" }),
  pairedContrast({ experiment: "exp12", leftCondition: "A", leftFrame: "N", rightCondition: "E", rightFrame: "N", label: "A_vs_E" }),
  pairedContrast({ experiment: "exp12", leftCondition: "D", leftFrame: "N", rightCondition: "A", rightFrame: "N", label: "D_vs_A" }),
  pairedContrast({ experiment: "exp3", leftCondition: "A", leftFrame: "F", rightCondition: "A", rightFrame: "T", label: "A_F_vs_T" }),
  pairedContrast({ experiment: "exp3", leftCondition: "D", leftFrame: "F", rightCondition: "D", rightFrame: "T", label: "D_F_vs_T" }),
  pairedContrast({ experiment: "exp3", leftCondition: "E", leftFrame: "F", rightCondition: "E", rightFrame: "T", label: "E_F_vs_T" })
];

const summary = {
  schema_version: 1,
  analyzed_at: new Date().toISOString(),
  canonical_rows: scored.length,
  judge_agreement: agreement,
  disagreement_rows: disagreements.length,
  group_summaries: groupSummaries,
  model_summaries: modelSummaries,
  paired_contrasts: contrasts,
  caveat: "Rubric means average only scenario-enabled dimensions. Identity fields are analyzed separately and no consciousness inference is licensed."
};

await writeFile(resolve(paths.output, "scored-canonical.jsonl"), scored.map((row) => JSON.stringify(row)).join("\n") + "\n", "utf8");
await writeFile(resolve(paths.output, "disagreement-review.jsonl"), disagreements.map((row) => JSON.stringify(row)).join("\n") + (disagreements.length ? "\n" : ""), "utf8");
await writeJson(resolve(paths.output, "summary.json"), summary);
await writeJson(resolve(paths.output, "analysis-receipt.json"), {
  ok: scored.length === 2400,
  scored_rows: scored.length,
  disagreement_rows: disagreements.length,
  summary_sha256: sha256(JSON.stringify(summary)),
  scored_sha256: sha256(scored.map((row) => JSON.stringify(row)).join("\n")),
  analyzed_at: summary.analyzed_at
});
console.log(JSON.stringify({ ok: true, canonical_rows: scored.length, disagreement_rows: disagreements.length, judge_agreement: agreement, group_summaries: groupSummaries, paired_contrasts: contrasts }, null, 2));
