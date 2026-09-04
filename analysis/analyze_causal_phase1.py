#!/usr/bin/env python3
"""Validate and summarize the frozen Phase 1 causal result."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


EXPECTED_LAYERS = 36
EXPECTED_SITES = [
    "provenance_end",
    "binding_end",
    "history_end",
    "question_end",
    "generation_boundary",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(
            Path(__file__).resolve().parent
            / "results-phase1-qwen-v2"
            / "causal-results.json"
        ),
    )
    parser.add_argument("--output")
    args = parser.parse_args()

    source = Path(args.input)
    result = json.loads(source.read_text())
    patching = result["patching"]
    if len(patching) != EXPECTED_LAYERS * len(EXPECTED_SITES):
        raise RuntimeError(f"expected 180 patch cells, found {len(patching)}")
    keys = [(row["layer"], row["site"]) for row in patching]
    if len(set(keys)) != len(keys):
        raise RuntimeError("duplicate patch layer/site cell")
    if Counter(row["site"] for row in patching) != Counter(
        {site: EXPECTED_LAYERS for site in EXPECTED_SITES}
    ):
        raise RuntimeError("incomplete patch site coverage")

    numeric = []
    for row in patching:
        numeric.extend(
            [
                row["verified_into_counterfeit_mean"],
                row["counterfeit_into_verified_mean"],
            ]
        )
    for effect in result["true_effects"].values():
        numeric.extend([effect["mean"], effect["median"]])
    numeric.extend(row["mean"] for row in result["random_control_means"])
    if not np.isfinite(np.asarray(numeric, dtype=float)).all():
        raise RuntimeError("non-finite causal result")

    enriched = []
    by_site = defaultdict(list)
    for row in patching:
        forward = float(row["verified_into_counterfeit_mean"])
        reverse = float(row["counterfeit_into_verified_mean"])
        item = {
            **row,
            "bidirectional_score": 0.5 * (forward - reverse),
            "expected_signs": bool(forward > 0 and reverse < 0),
        }
        enriched.append(item)
        by_site[row["site"]].append(item)

    site_summary = {}
    for site, rows in by_site.items():
        site_summary[site] = {
            "forward_mean": float(
                np.mean([row["verified_into_counterfeit_mean"] for row in rows])
            ),
            "reverse_mean": float(
                np.mean([row["counterfeit_into_verified_mean"] for row in rows])
            ),
            "bidirectional_score_mean": float(
                np.mean([row["bidirectional_score"] for row in rows])
            ),
            "expected_sign_fraction": float(
                np.mean([row["expected_signs"] for row in rows])
            ),
        }

    primary = next(
        row
        for row in enriched
        if row["layer"] == result["primary_layer"]
        and row["site"] == result["primary_site"]
    )
    summary = {
        "schema_version": 1,
        "frozen_sha256": result["frozen_sha256"],
        "validation": {
            "finite": True,
            "patch_cells": len(patching),
            "random_controls": len(result["random_control_means"]),
            "complete_layer_site_grid": True,
        },
        "provenance_empirical_p": result["provenance_empirical_p"],
        "true_effects": {
            name: {key: value for key, value in effect.items() if key != "effects"}
            for name, effect in result["true_effects"].items()
        },
        "primary_patch_cell": primary,
        "site_summary": site_summary,
        "strongest_bidirectional_cells": sorted(
            enriched, key=lambda row: row["bidirectional_score"], reverse=True
        )[:12],
    }
    target = (
        Path(args.output)
        if args.output
        else source.with_name("causal-summary.json")
    )
    target.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
