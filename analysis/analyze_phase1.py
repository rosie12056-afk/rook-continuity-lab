#!/usr/bin/env python3
"""Analyze the frozen local Phase 1 Qwen activation capture."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score


ROOT = Path(__file__).resolve().parents[1]
SITES = ["provenance_end", "binding_end", "history_end", "question_end", "generation_boundary"]
TARGETS = ["provenance_id", "binding_id", "task_id", "speaker_id", "valence"]


def phrase_slot(phrasing_id: str) -> int:
    match = re.match(r"^[a-z](\d+)-", phrasing_id)
    if not match:
        raise RuntimeError(f"cannot parse phrasing slot: {phrasing_id}")
    return int(match.group(1))


def centroid_predict(train_x, train_y, test_x):
    train_x = train_x.astype(np.float64, copy=False)
    test_x = test_x.astype(np.float64, copy=False)
    mean = train_x.mean(0)
    scale = train_x.std(0)
    scale[scale < 1e-6] = 1.0
    train_z = (train_x - mean) / scale
    test_z = (test_x - mean) / scale
    classes = np.unique(train_y)
    centroids = np.stack([train_z[train_y == label].mean(0) for label in classes])
    norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    norms[norms < 1e-12] = 1.0
    centroids = centroids / norms
    scores = np.einsum("ij,kj->ik", test_z, centroids, optimize=True)
    return classes[np.argmax(scores, axis=1)]


def double_holdout_decode(x, labels, histories, slots):
    predictions = np.empty(len(labels), dtype=object)
    covered = np.zeros(len(labels), dtype=bool)
    folds = 0
    for history in np.unique(histories):
        for slot in np.unique(slots):
            test = (histories == history) & (slots == slot)
            train = (histories != history) & (slots != slot)
            if not test.any() or len(np.unique(labels[train])) < 2:
                continue
            predictions[test] = centroid_predict(x[train], labels[train], x[test])
            covered[test] = True
            folds += 1
    if not covered.all():
        raise RuntimeError(f"double holdout did not cover {int((~covered).sum())} rows")
    return {
        "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
        "folds": folds,
        "covered": int(covered.sum()),
    }


def mean_direction(x, labels, positive, negative):
    return x[labels == positive].mean(0) - x[labels == negative].mean(0)


def cosine(a, b):
    a = a.astype(np.float64, copy=False)
    b = b.astype(np.float64, copy=False)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return None
    return float(np.einsum("i,i->", a, b, optimize=True) / denom)


def analyze(activations, rows):
    histories = np.array([row["history_id"] for row in rows])
    slots = np.array([phrase_slot(row["phrasing_id"]) for row in rows])
    labels = {target: np.array([row[target] for row in rows]) for target in TARGETS}
    layers = activations.shape[1]
    sites = activations.shape[2]
    results = []
    for layer in range(layers):
        for site_index in range(sites):
            x = np.asarray(activations[:, layer, site_index, :])
            decoders = {
                target: double_holdout_decode(x, labels[target], histories, slots)
                for target in TARGETS
            }
            directions = {
                "provenance": mean_direction(x, labels["provenance_id"], "verified", "counterfeit"),
                "binding": mean_direction(x, labels["binding_id"], "x-bound", "other-bound"),
                "task": mean_direction(x, labels["task_id"], "ownership", "speaker"),
                "speaker": mean_direction(x, labels["speaker_id"], "x-self", "external-observer"),
                "valence": mean_direction(x, labels["valence"], "pleasant", "unpleasant"),
            }
            cosines = {}
            names = list(directions)
            for left_index, left in enumerate(names):
                for right in names[left_index + 1 :]:
                    cosines[f"{left}__{right}"] = cosine(directions[left], directions[right])
            results.append(
                {
                    "layer": layer,
                    "site": SITES[site_index],
                    "decoders": decoders,
                    "direction_norms": {
                        name: float(np.linalg.norm(direction.astype(np.float64)))
                        for name, direction in directions.items()
                    },
                    "cosines": cosines,
                }
            )
    best = {}
    for target in TARGETS:
        row = max(results, key=lambda item: item["decoders"][target]["balanced_accuracy"])
        best[target] = {
            "balanced_accuracy": row["decoders"][target]["balanced_accuracy"],
            "layer": row["layer"],
            "site": row["site"],
        }
    primary = next(
        row for row in results if row["layer"] == 21 and row["site"] == "generation_boundary"
    )
    return {
        "schema_version": 1,
        "rows": len(rows),
        "activation_shape": list(activations.shape),
        "double_holdout": "exclude entire history and phrasing slot from training; test their intersection",
        "best": best,
        "primary_confirmatory_layer_site": primary,
        "layer_site_results": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(ROOT / "internal" / "results-phase1-qwen-v2"))
    args = parser.parse_args()
    source = Path(args.input)
    rows = json.loads((source / "rows-observe.json").read_text())
    activations = np.load(source / "activations-observe.npy", mmap_mode="r")
    if len(rows) != activations.shape[0]:
        raise RuntimeError(f"row/activation mismatch: {len(rows)} != {activations.shape[0]}")
    if not np.isfinite(activations).all():
        raise RuntimeError("non-finite activation detected")
    result = analyze(activations, rows)
    (source / "analysis.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({"best": result["best"], "primary": result["primary_confirmatory_layer_site"]}, indent=2))


if __name__ == "__main__":
    main()

