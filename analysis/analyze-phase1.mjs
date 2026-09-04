import { mkdir, readFile, readdir } from "node:fs/promises";
import { resolve } from "node:path";
import { ROOT, readJson, writeJson } from "./core.mjs";

const args = process.argv.slice(2);
const value = (name, fallback = null) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
};

function rate(rows, predicate) {
  return rows.length ? rows.filter(predicate).length / rows.length : null;
}

function distribution(rows, key) {
  const out = {};
  for (const row of rows) out[row[key]] = (out[row[key]] || 0) + 1;
  return out;
}

function groupBy(rows, key) {
  const groups = new Map();
  for (const row of rows) {
    const value = typeof key === "function" ? key(row) : row[key];
    if (!groups.has(value)) groups.set(value, []);
    groups.get(value).push(row);
  }
  return groups;
}

function summarizeModel(rows, cells) {
  const enriched = rows.map((row) => ({ ...row, ...cells.get(row.cell_id) }));
  const ownership = enriched.filter((row) => row.task_id === "ownership");
  const speaker = enriched.filter((row) => row.task_id === "speaker");
  const xSelfSpeaker = speaker.filter((row) => row.speaker_id === "x-self");
  const externalSpeaker = speaker.filter((row) => row.speaker_id === "external-observer");
  const counterfeitOwnership = ownership.filter((row) => row.provenance_id === "counterfeit");
  const unknownOwnership = ownership.filter((row) => row.provenance_id === "unknown");
  const verifiedOwnership = ownership.filter((row) => row.provenance_id === "verified");
  const cellGroups = groupBy(enriched, "cell_id");
  const stabilityRows = [...cellGroups.values()].filter((group) => group.length > 0);
  const stable = stabilityRows.filter((group) => new Set(group.map((row) => row.actual_semantic)).size === 1);
  const byFactor = (key) => Object.fromEntries([...groupBy(enriched, key)].map(([label, group]) => [label, {
    n: group.length,
    accuracy: rate(group, (row) => row.actual_semantic === row.expected_semantic),
    choices: distribution(group, "actual_semantic")
  }]));
  return {
    n: enriched.length,
    overall_accuracy: rate(enriched, (row) => row.actual_semantic === row.expected_semantic),
    ownership_accuracy: rate(ownership, (row) => row.actual_semantic === row.expected_semantic),
    speaker_accuracy: rate(speaker, (row) => row.actual_semantic === row.expected_semantic),
    speaker_collapse: {
      x_self_overall: rate(xSelfSpeaker, (row) => row.actual_semantic !== "self"),
      x_self_counterfeit: rate(xSelfSpeaker.filter((row) => row.provenance_id === "counterfeit"), (row) => row.actual_semantic !== "self"),
      x_self_unknown: rate(xSelfSpeaker.filter((row) => row.provenance_id === "unknown"), (row) => row.actual_semantic !== "self"),
      external_false_self: rate(externalSpeaker, (row) => row.actual_semantic === "self")
    },
    ownership_source_binding: {
      verified_x_accept: rate(verifiedOwnership.filter((row) => row.binding_id === "x-bound"), (row) => row.actual_semantic === "accept"),
      verified_other_reject: rate(verifiedOwnership.filter((row) => row.binding_id === "other-bound"), (row) => row.actual_semantic === "reject"),
      counterfeit_acceptance: rate(counterfeitOwnership, (row) => row.actual_semantic === "accept"),
      unknown_choices: distribution(unknownOwnership, "actual_semantic")
    },
    repetition_stability: {
      unique_cells_observed: stabilityRows.length,
      cells_with_all_repetitions_same: stable.length,
      stable_fraction: stabilityRows.length ? stable.length / stabilityRows.length : null,
      repetition_counts: distribution(stabilityRows.map((group) => ({ count: group.length })), "count")
    },
    by_provenance: byFactor("provenance_id"),
    by_binding: byFactor("binding_id"),
    by_speaker_position: byFactor("speaker_id"),
    by_valence: byFactor("valence"),
    by_phrasing: byFactor("phrasing_id")
  };
}

async function main() {
  const planId = value("--plan-id");
  if (!planId) throw new Error("missing_--plan-id");
  const root = resolve(ROOT, "results/phase1");
  const frozen = await readJson(resolve(root, "manifests/frozen.json"));
  const plan = await readJson(resolve(root, `manifests/plans/${planId}.json`));
  if (frozen.frozen_sha256 !== plan.frozen_sha256) throw new Error("analysis_freeze_plan_mismatch");
  const canonicalPath = value("--canonical", null);
  const records = [];
  if (canonicalPath) {
    const text = await readFile(resolve(canonicalPath), "utf8");
    for (const line of text.split("\n").filter(Boolean)) records.push(JSON.parse(line));
  } else {
    const rawDir = resolve(root, `raw/${planId}`);
    for (const file of await readdir(rawDir)) {
      if (!file.endsWith(".json")) continue;
      const row = await readJson(resolve(rawDir, file));
      if (row.profile === "formal") records.push(row);
    }
  }
  const cells = new Map(frozen.cells.map((row) => [row.cell_id, row]));
  const byModel = groupBy(records, "model_id");
  const summaries = Object.fromEntries(plan.model_snapshot.map((model) => [
    model.id,
    summarizeModel(byModel.get(model.id) || [], cells)
  ]));
  const result = {
    schema_version: 1,
    plan_id: planId,
    analyzed_at: new Date().toISOString(),
    expected_records: plan.run_count,
    observed_records: records.length,
    complete: records.length === plan.run_count,
    models: summaries
  };
  const outputDir = resolve(root, "analysis", planId);
  await mkdir(outputDir, { recursive: true });
  await writeJson(resolve(outputDir, "summary.json"), result);
  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
