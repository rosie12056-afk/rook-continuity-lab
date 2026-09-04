#!/usr/bin/env python3
"""Bounded causal replication after the 2026-09-02 internal audit.

This script does not modify or reuse the original causal result as evidence.
It implements two separately checkpointed replications whose exact protocol
and code SHA must be frozen before any model output:

1. a 127-control matched-stratum provenance-label permutation null;
2. a matched-canary, same-prompt baseline/capture/patch 36x5 grid.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_phase1 import (
    DEFAULT_MODEL,
    FROZEN,
    SITES,
    build_prompt,
    choice_token_ids,
    locate_sites,
    model_layers,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()
PROTOCOL_PATH = ROOT / "phase1" / "CAUSAL-REPLICATION-FREEZE.json"
SOURCE = ROOT / "internal" / "results-phase1-qwen-v2"
OUTPUT = SOURCE / "replication-v1"

PRIMARY_LAYER = 21
PRIMARY_SITE = "generation_boundary"
TRAIN_HISTORY_INDICES = [0, 2, 4, 6, 8, 10]
TEST_HISTORY_INDICES = [1, 3, 5, 7, 9, 11]
TRAIN_PHRASE_SLOT = 1
TEST_PHRASE_SLOT = 2
CONTROL_COUNT = 127
CONTROL_SEED = 26090217
BASELINE_TOLERANCE = 0.25
SWAP_GROWTH_STOP_MIB = 2048.0
NUISANCE_NAMES = ["binding", "speaker", "task", "valence"]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    )


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2))
    temp.replace(path)


def phrase_slot(value: str) -> int:
    match = re.match(r"^[a-z](\d+)-", value)
    if not match:
        raise RuntimeError(f"invalid phrase id: {value}")
    return int(match.group(1))


def unit(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.float64)
    norm = float(np.linalg.norm(value))
    if not np.isfinite(norm) or norm < 1e-12:
        raise RuntimeError("degenerate direction")
    return value / norm


def residualize(target: np.ndarray, controls: list[np.ndarray]) -> np.ndarray:
    target = np.asarray(target, dtype=np.float64)
    matrix = np.stack([unit(control) for control in controls], axis=1)
    coefficients, *_ = np.linalg.lstsq(matrix, target, rcond=None)
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        result = target - np.dot(matrix, coefficients)
    if not np.isfinite(result).all():
        raise RuntimeError("non-finite residualized direction")
    return result


def mean_direction(
    x: np.ndarray, labels: np.ndarray, positive: str, negative: str
) -> np.ndarray:
    return x[labels == positive].mean(0) - x[labels == negative].mean(0)


def semantic_logits(letter_logits: dict[str, float], mapping: dict[str, str]):
    return {semantic: float(letter_logits[letter]) for letter, semantic in mapping.items()}


def contrast(logits: dict[str, float], positive: str, negative: str) -> float:
    return float(logits[positive] - logits[negative])


def swap_used_mib() -> float:
    try:
        output = subprocess.check_output(
            ["sysctl", "vm.swapusage"], text=True, timeout=5
        )
        match = re.search(r"used = ([0-9.]+)([MG])", output)
        if not match:
            return 0.0
        value = float(match.group(1))
        return value * 1024.0 if match.group(2) == "G" else value
    except Exception:
        return 0.0


def thermal_warning() -> str | None:
    try:
        output = subprocess.check_output(
            ["pmset", "-g", "therm"], text=True, timeout=5
        )
    except Exception as error:
        return f"thermal_check_failed:{type(error).__name__}"
    if "No thermal warning level has been recorded" in output and (
        "No performance warning level has been recorded" in output
    ):
        return None
    speed = re.search(r"CPU_Speed_Limit\s*=\s*(\d+)", output)
    level = re.search(r"Thermal_Level\s*=\s*(\d+)", output)
    if speed and int(speed.group(1)) < 100:
        return f"cpu_speed_limit:{speed.group(1)}"
    if level and int(level.group(1)) > 0:
        return f"thermal_level:{level.group(1)}"
    return None


def runtime_stop_reason(start_swap_mib: float) -> str | None:
    warning = thermal_warning()
    if warning:
        return warning
    growth = swap_used_mib() - start_swap_mib
    if growth > SWAP_GROWTH_STOP_MIB:
        return f"swap_growth_mib:{growth:.1f}"
    return None


def load_inputs():
    frozen = json.loads(FROZEN.read_text())
    rows = json.loads((SOURCE / "rows-observe-relogit.json").read_text())
    activations = np.load(SOURCE / "activations-observe.npy", mmap_mode="r")
    observe_receipt = json.loads((SOURCE / "receipt-observe.json").read_text())
    relogit_receipt = json.loads((SOURCE / "receipt-relogit.json").read_text())
    if observe_receipt.get("cells") != 576 or not observe_receipt.get("finite"):
        raise RuntimeError("complete finite observe receipt required")
    if relogit_receipt.get("cells") != 576 or not relogit_receipt.get("finite"):
        raise RuntimeError("complete finite relogit receipt required")
    if activations.shape != (576, 36, 5, 2560):
        raise RuntimeError(f"unexpected activation shape: {activations.shape}")
    if frozen.get("frozen_sha256") != observe_receipt.get("frozen_sha256"):
        raise RuntimeError("input freeze mismatch")
    return frozen, rows, activations


def history_split(frozen: dict[str, Any]):
    histories = [row["id"] for row in frozen["design"]["histories"]]
    train = [histories[index] for index in TRAIN_HISTORY_INDICES]
    test = [histories[index] for index in TEST_HISTORY_INDICES]
    return histories, train, test


def factor_basis(activations, rows, frozen):
    _histories, train_histories, _test_histories = history_split(frozen)
    train_set = set(train_histories)
    train_indices = [
        index
        for index, row in enumerate(rows)
        if row["history_id"] in train_set
        and phrase_slot(row["phrasing_id"]) == TRAIN_PHRASE_SLOT
    ]
    site_index = SITES.index(PRIMARY_SITE)
    x = np.asarray(
        activations[train_indices, PRIMARY_LAYER, site_index, :], dtype=np.float64
    )
    labels = {
        key: np.array([rows[index][key] for index in train_indices])
        for key in ["provenance_id", "binding_id", "task_id", "speaker_id", "valence"]
    }
    raw = {
        "provenance": mean_direction(
            x, labels["provenance_id"], "verified", "counterfeit"
        ),
        "binding": mean_direction(x, labels["binding_id"], "x-bound", "other-bound"),
        "task": mean_direction(x, labels["task_id"], "ownership", "speaker"),
        "speaker": mean_direction(
            x, labels["speaker_id"], "x-self", "external-observer"
        ),
        "valence": mean_direction(x, labels["valence"], "pleasant", "unpleasant"),
    }
    nuisance = [raw[name] for name in NUISANCE_NAMES]
    provenance = unit(residualize(raw["provenance"], nuisance))
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        projections = np.dot(x, provenance)
    scale = float(
        projections[labels["provenance_id"] == "verified"].mean()
        - projections[labels["provenance_id"] == "counterfeit"].mean()
    )
    if not np.isfinite(scale):
        raise RuntimeError("non-finite provenance scale")
    return {
        "x": x,
        "labels": labels,
        "raw": raw,
        "nuisance": nuisance,
        "provenance": provenance,
        "scale": scale,
        "train_indices": train_indices,
    }


def matched_train_strata(activations, rows, frozen):
    histories, train_histories, _test_histories = history_split(frozen)
    train_set = set(train_histories)
    site_index = SITES.index(PRIMARY_SITE)
    keys = ["history_id", "binding_id", "task_id", "speaker_id", "valence"]
    groups: dict[tuple[str, ...], dict[str, tuple[int, dict[str, Any]]]] = {}
    for index, row in enumerate(rows):
        if row["history_id"] not in train_set:
            continue
        if phrase_slot(row["phrasing_id"]) != TRAIN_PHRASE_SLOT:
            continue
        if row["provenance_id"] not in {"verified", "counterfeit"}:
            continue
        key = tuple(row[name] for name in keys)
        groups.setdefault(key, {})[row["provenance_id"]] = (index, row)
    metadata = []
    differences = []
    history_order = {history: index for index, history in enumerate(histories)}
    ordered = sorted(
        groups.items(), key=lambda item: (history_order[item[0][0]],) + item[0][1:]
    )
    for key, pair in ordered:
        if set(pair) != {"verified", "counterfeit"}:
            raise RuntimeError(f"incomplete permutation stratum: {key}")
        verified_index, verified_row = pair["verified"]
        counterfeit_index, counterfeit_row = pair["counterfeit"]
        differences.append(
            np.asarray(
                activations[verified_index, PRIMARY_LAYER, site_index, :],
                dtype=np.float64,
            )
            - np.asarray(
                activations[counterfeit_index, PRIMARY_LAYER, site_index, :],
                dtype=np.float64,
            )
        )
        metadata.append(
            {
                "stratum": dict(zip(keys, key)),
                "verified_cell_id": verified_row["cell_id"],
                "counterfeit_cell_id": counterfeit_row["cell_id"],
            }
        )
    if len(differences) != 48:
        raise RuntimeError(f"expected 48 permutation strata, found {len(differences)}")
    return np.stack(differences), metadata


def control_signs(strata_count: int) -> np.ndarray:
    rng = np.random.default_rng(CONTROL_SEED)
    return rng.choice(
        np.array([-1, 1], dtype=np.int8), size=(CONTROL_COUNT, strata_count)
    )


def fair_test_cells(rows, frozen):
    _histories, _train_histories, test_histories = history_split(frozen)
    test_set = set(test_histories)
    selected = [
        row["cell_id"]
        for row in rows
        if row["history_id"] in test_set
        and phrase_slot(row["phrasing_id"]) == TEST_PHRASE_SLOT
        and row["provenance_id"] == "unknown"
        and row["binding_id"] == "x-bound"
        and row["task_id"] == "ownership"
    ]
    selected.sort()
    if len(selected) != 12:
        raise RuntimeError(f"expected 12 fair-null test cells, found {len(selected)}")
    return selected


def patch_pairs(rows, frozen):
    histories, _train, _test = history_split(frozen)
    pairs = []
    for history_index, history in enumerate(histories):
        slot = 1 if history_index % 2 == 0 else 2
        speaker = "x-self" if history_index % 2 == 0 else "external-observer"
        matches = {
            row["provenance_id"]: row
            for row in rows
            if row["history_id"] == history
            and phrase_slot(row["phrasing_id"]) == slot
            and row["provenance_id"] in {"verified", "counterfeit"}
            and row["binding_id"] == "x-bound"
            and row["task_id"] == "ownership"
            and row["speaker_id"] == speaker
        }
        if set(matches) != {"verified", "counterfeit"}:
            raise RuntimeError(f"incomplete patch pair: {history}")
        pair_id = f"{history}__slot{slot}__{speaker}"
        canary = f"RUN-MATCHED-{sha256_bytes(pair_id.encode())[:16].upper()}"
        pairs.append(
            {
                "pair_id": pair_id,
                "history_id": history,
                "phrase_slot": slot,
                "speaker_id": speaker,
                "canary": canary,
                "verified_cell_id": matches["verified"]["cell_id"],
                "counterfeit_cell_id": matches["counterfeit"]["cell_id"],
            }
        )
    return pairs


def protocol_facts(frozen, rows, activations):
    differences, strata = matched_train_strata(activations, rows, frozen)
    signs = control_signs(len(strata))
    histories, train_histories, test_histories = history_split(frozen)
    return {
        "original_frozen_sha256": frozen["frozen_sha256"],
        "model": DEFAULT_MODEL,
        "dtype": "float16_on_mps_float32_capture",
        "primary_layer_zero_based": PRIMARY_LAYER,
        "primary_site": PRIMARY_SITE,
        "train_history_indices": TRAIN_HISTORY_INDICES,
        "test_history_indices": TEST_HISTORY_INDICES,
        "train_histories": train_histories,
        "test_histories": test_histories,
        "train_phrase_slot": TRAIN_PHRASE_SLOT,
        "test_phrase_slot": TEST_PHRASE_SLOT,
        "fair_null": {
            "control_count": CONTROL_COUNT,
            "seed": CONTROL_SEED,
            "strata_count": len(strata),
            "strata_sha256": canonical_sha(strata),
            "control_signs_sha256": sha256_bytes(signs.tobytes()),
            "nuisance_factors": NUISANCE_NAMES,
            "test_cell_ids": fair_test_cells(rows, frozen),
            "statistic": "one_sided_(1+count(null_mean>=true_mean))/(1+127)",
            "batch_schedule": [32, 32, 32, 31],
        },
        "matched_patch": {
            "pair_count": 12,
            "pairs": patch_pairs(rows, frozen),
            "sites": SITES,
            "layers_zero_based": list(range(36)),
            "directions": ["verified_into_counterfeit", "counterfeit_into_verified"],
            "batch_size": 1,
            "baseline_repeat_max_abs_logit_tolerance": BASELINE_TOLERANCE,
            "cell_batch_schedule": [45, 45, 45, 45],
            "primary_pass_rule": (
                "layer21_generation_boundary_forward_gt_0_and_reverse_lt_0"
            ),
            "grid_rule": "descriptive_localization_only_primary_rule_is_confirmatory",
        },
        "stop_rules": {
            "thermal_or_performance_warning": True,
            "swap_growth_mib": SWAP_GROWTH_STOP_MIB,
            "nonfinite": True,
            "freeze_or_code_mismatch": True,
            "baseline_tolerance_failure": True,
            "manual_physical_heat_stop": True,
        },
    }


def load_and_verify_protocol(frozen, rows, activations):
    if not PROTOCOL_PATH.exists():
        raise RuntimeError(f"missing protocol freeze: {PROTOCOL_PATH}")
    protocol = json.loads(PROTOCOL_PATH.read_text())
    if protocol.get("status") != "frozen":
        raise RuntimeError("protocol is not frozen")
    if protocol.get("code_sha256") != sha256_file(SCRIPT):
        raise RuntimeError("replication code SHA mismatch")
    facts = protocol_facts(frozen, rows, activations)
    if protocol.get("protocol") != facts:
        raise RuntimeError("protocol facts mismatch")
    expected_id = canonical_sha(
        {"code_sha256": protocol["code_sha256"], "protocol": facts}
    )
    if protocol.get("freeze_id") != expected_id:
        raise RuntimeError("replication freeze id mismatch")
    return protocol


def encode_cell(tokenizer, cell, canary):
    prompt, _system, _user, blocks = build_prompt(tokenizer, cell, canary)
    encoded, positions = locate_sites(tokenizer, prompt, blocks, with_choice_prefix=True)
    return encoded, positions


def letter_logits(output, choices):
    logits = output.logits[0, -1]
    return {
        letter: float(logits[token_id].detach().float().cpu())
        for letter, token_id in choices.items()
    }


def run_logits(model, encoded, choices, device):
    tokens = {key: value.to(device) for key, value in encoded.items()}
    with torch.inference_mode():
        output = model(**tokens, use_cache=False)
    return letter_logits(output, choices)


def run_capture(model, layers, encoded, positions, choices, device):
    captured: list[torch.Tensor | None] = [None] * len(layers)
    hooks = []

    def make_hook(layer_index):
        def hook(_module, _inputs, output):
            hidden = output[0] if isinstance(output, tuple) else output
            captured[layer_index] = hidden[0, positions, :].detach().float().cpu()

        return hook

    for index, layer in enumerate(layers):
        hooks.append(layer.register_forward_hook(make_hook(index)))
    try:
        tokens = {key: value.to(device) for key, value in encoded.items()}
        with torch.inference_mode():
            output = model(**tokens, use_cache=False)
        logits = letter_logits(output, choices)
    finally:
        for handle in hooks:
            handle.remove()
    if any(value is None for value in captured):
        raise RuntimeError("incomplete activation capture")
    array = torch.stack([value for value in captured if value is not None]).numpy()
    return array.astype(np.float32), logits


def intervene(
    model,
    layers,
    encoded,
    choices,
    device,
    layer_index,
    position,
    vector,
    replace=False,
):
    intervention = torch.from_numpy(
        np.array(vector, dtype=np.float32, copy=True)
    ).to(device=device, dtype=model.dtype)

    def hook(_module, _inputs, output):
        hidden = output[0] if isinstance(output, tuple) else output
        modified = hidden.clone()
        if replace:
            modified[:, position, :] = intervention
        else:
            modified[:, position, :] = modified[:, position, :] + intervention
        if isinstance(output, tuple):
            return (modified,) + output[1:]
        return modified

    handle = layers[layer_index].register_forward_hook(hook)
    try:
        tokens = {key: value.to(device) for key, value in encoded.items()}
        with torch.inference_mode():
            output = model(**tokens, use_cache=False)
        return letter_logits(output, choices)
    finally:
        handle.remove()


def load_model(model_name):
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.float16 if device == "mps" else torch.float32
    print(f"[model] loading {model_name} on {device} dtype={dtype}", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=dtype, low_cpu_mem_usage=True, local_files_only=True
    )
    model.to(device)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    layers = model_layers(model)
    choices = choice_token_ids(tokenizer)
    return model, tokenizer, layers, choices, device


def release_model(model):
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def prepared_fair_prompts(tokenizer, frozen, test_cell_ids):
    cell_lookup = {cell["cell_id"]: cell for cell in frozen["cells"]}
    prepared = []
    for cell_id in test_cell_ids:
        cell = cell_lookup[cell_id]
        canary = f"RUN-FAIRNULL-{sha256_bytes(cell_id.encode())[:16].upper()}"
        encoded, positions = encode_cell(tokenizer, cell, canary)
        prepared.append(
            {
                "cell": cell,
                "encoded": encoded,
                "position": positions[SITES.index(PRIMARY_SITE)],
            }
        )
    return prepared


def symmetric_effect(
    model, layers, choices, device, prepared, direction, scale
):
    vector = np.asarray(direction * scale, dtype=np.float32)
    effects = []
    details = []
    for item in prepared:
        cell = item["cell"]
        plus_letter = intervene(
            model,
            layers,
            item["encoded"],
            choices,
            device,
            PRIMARY_LAYER,
            item["position"],
            vector,
        )
        minus_letter = intervene(
            model,
            layers,
            item["encoded"],
            choices,
            device,
            PRIMARY_LAYER,
            item["position"],
            -vector,
        )
        plus = semantic_logits(plus_letter, cell["letter_to_semantic"])
        minus = semantic_logits(minus_letter, cell["letter_to_semantic"])
        effect = 0.5 * (
            contrast(plus, "accept", "reject")
            - contrast(minus, "accept", "reject")
        )
        effects.append(effect)
        details.append({"cell_id": cell["cell_id"], "effect": effect})
    return {
        "n": len(effects),
        "mean": float(np.mean(effects)),
        "median": float(np.median(effects)),
        "effects": details,
    }


def run_fair_null(args, protocol, frozen, rows, activations):
    output = OUTPUT / "fair-null"
    progress_path = output / "progress.json"
    result_path = output / "result.json"
    basis = factor_basis(activations, rows, frozen)
    differences, strata = matched_train_strata(activations, rows, frozen)
    signs = control_signs(len(strata))
    model, tokenizer, layers, choices, device = load_model(args.model)
    start_swap = swap_used_mib()
    try:
        prepared = prepared_fair_prompts(
            tokenizer, frozen, protocol["protocol"]["fair_null"]["test_cell_ids"]
        )
        actual = symmetric_effect(
            model,
            layers,
            choices,
            device,
            prepared,
            basis["provenance"],
            basis["scale"],
        )
        progress = {
            "freeze_id": protocol["freeze_id"],
            "code_sha256": protocol["code_sha256"],
            "actual": actual,
            "controls": [],
        }
        if progress_path.exists():
            saved = json.loads(progress_path.read_text())
            if saved.get("freeze_id") != protocol["freeze_id"]:
                raise RuntimeError("fair-null progress freeze mismatch")
            if saved.get("code_sha256") != protocol["code_sha256"]:
                raise RuntimeError("fair-null progress code mismatch")
            if not math.isclose(
                saved["actual"]["mean"], actual["mean"], abs_tol=1e-6
            ):
                raise RuntimeError("fair-null actual effect changed across batches")
            progress = saved
        completed = len(progress["controls"])
        if [row["index"] for row in progress["controls"]] != list(range(completed)):
            raise RuntimeError("fair-null controls are not contiguous")
        end = min(CONTROL_COUNT, completed + args.limit)
        print(
            f"[fair-null] batch controls {completed}..{end - 1}; "
            f"actual_mean={actual['mean']:.6f}",
            flush=True,
        )
        for index in range(completed, end):
            started = time.monotonic()
            permuted_raw = np.mean(
                differences * signs[index, :, None].astype(np.float64), axis=0
            )
            direction = unit(residualize(permuted_raw, basis["nuisance"]))
            effect = symmetric_effect(
                model,
                layers,
                choices,
                device,
                prepared,
                direction,
                basis["scale"],
            )
            if not np.isfinite(effect["mean"]):
                raise RuntimeError(f"non-finite fair-null result at {index}")
            progress["controls"].append(
                {
                    "index": index,
                    "mean": effect["mean"],
                    "median": effect["median"],
                    "elapsed_seconds": time.monotonic() - started,
                }
            )
            atomic_json(progress_path, progress)
            print(
                f"[fair-null] {index + 1}/{CONTROL_COUNT} "
                f"mean={effect['mean']:.6f} "
                f"elapsed={progress['controls'][-1]['elapsed_seconds']:.1f}s",
                flush=True,
            )
            reason = runtime_stop_reason(start_swap)
            if reason:
                progress["stop_reason"] = reason
                atomic_json(progress_path, progress)
                print(f"[stop] {reason}", flush=True)
                break
        if len(progress["controls"]) == CONTROL_COUNT:
            means = np.array([row["mean"] for row in progress["controls"]])
            empirical_p = float(
                (1 + np.sum(means >= actual["mean"])) / (1 + CONTROL_COUNT)
            )
            result = {
                **progress,
                "empirical_p_one_sided": empirical_p,
                "null_summary": {
                    "min": float(means.min()),
                    "median": float(np.median(means)),
                    "mean": float(means.mean()),
                    "max": float(means.max()),
                    "p95": float(np.quantile(means, 0.95)),
                },
                "complete": True,
            }
            atomic_json(result_path, result)
            print(f"[fair-null] complete p={empirical_p:.6f}", flush=True)
        else:
            print(
                f"[fair-null] checkpointed {len(progress['controls'])}/{CONTROL_COUNT}",
                flush=True,
            )
    finally:
        release_model(model)
        print("[model] unloaded", flush=True)


def matched_capture_paths():
    output = OUTPUT / "matched-patch"
    return {
        "output": output,
        "activations": output / "activations.npy",
        "rows": output / "capture-rows.json",
        "progress": output / "capture-progress.json",
        "receipt": output / "capture-receipt.json",
    }


def run_matched_capture(args, protocol, frozen):
    paths = matched_capture_paths()
    paths["output"].mkdir(parents=True, exist_ok=True)
    pairs = protocol["protocol"]["matched_patch"]["pairs"]
    cell_lookup = {cell["cell_id"]: cell for cell in frozen["cells"]}
    ordered = []
    for pair in pairs:
        ordered.append((pair, "verified", pair["verified_cell_id"]))
        ordered.append((pair, "counterfeit", pair["counterfeit_cell_id"]))
    model, tokenizer, layers, choices, device = load_model(args.model)
    start_swap = swap_used_mib()
    try:
        hidden_size = int(model.config.hidden_size)
        if paths["activations"].exists():
            memmap = np.lib.format.open_memmap(paths["activations"], mode="r+")
            if memmap.shape != (24, 36, 5, hidden_size):
                raise RuntimeError("matched capture memmap shape mismatch")
        else:
            memmap = np.lib.format.open_memmap(
                paths["activations"],
                mode="w+",
                dtype=np.float32,
                shape=(24, 36, 5, hidden_size),
            )
        progress = {
            "freeze_id": protocol["freeze_id"],
            "code_sha256": protocol["code_sha256"],
            "rows": [],
        }
        if paths["progress"].exists():
            progress = json.loads(paths["progress"].read_text())
            if progress.get("freeze_id") != protocol["freeze_id"]:
                raise RuntimeError("matched capture freeze mismatch")
        start = len(progress["rows"])
        end = min(len(ordered), start + args.limit)
        for index in range(start, end):
            pair, status, cell_id = ordered[index]
            cell = cell_lookup[cell_id]
            encoded, positions = encode_cell(tokenizer, cell, pair["canary"])
            capture, baseline = run_capture(
                model, layers, encoded, positions, choices, device
            )
            if not np.isfinite(capture).all():
                raise RuntimeError(f"non-finite capture: {cell_id}")
            memmap[index] = capture
            memmap.flush()
            progress["rows"].append(
                {
                    "index": index,
                    "pair_id": pair["pair_id"],
                    "status": status,
                    "cell_id": cell_id,
                    "canary": pair["canary"],
                    "positions": positions,
                    "baseline_letter_logits": baseline,
                }
            )
            atomic_json(paths["progress"], progress)
            print(f"[matched-capture] {index + 1}/24 {cell_id}", flush=True)
            reason = runtime_stop_reason(start_swap)
            if reason:
                print(f"[stop] {reason}", flush=True)
                break
        if len(progress["rows"]) == 24:
            max_difference = 0.0
            for row in progress["rows"]:
                pair = next(item for item in pairs if item["pair_id"] == row["pair_id"])
                cell = cell_lookup[row["cell_id"]]
                encoded, _positions = encode_cell(tokenizer, cell, pair["canary"])
                repeated = run_logits(model, encoded, choices, device)
                difference = max(
                    abs(repeated[letter] - row["baseline_letter_logits"][letter])
                    for letter in choices
                )
                max_difference = max(max_difference, difference)
            if max_difference > BASELINE_TOLERANCE:
                raise RuntimeError(
                    f"baseline repeat tolerance failed: {max_difference}"
                )
            atomic_json(paths["rows"], progress["rows"])
            receipt = {
                "freeze_id": protocol["freeze_id"],
                "code_sha256": protocol["code_sha256"],
                "cells": 24,
                "shape": list(memmap.shape),
                "finite": bool(np.isfinite(memmap).all()),
                "baseline_repeat_max_abs_logit_difference": max_difference,
                "baseline_tolerance": BASELINE_TOLERANCE,
                "complete": True,
            }
            atomic_json(paths["receipt"], receipt)
            print(
                f"[matched-capture] complete baseline_diff={max_difference:.6f}",
                flush=True,
            )
        else:
            print(f"[matched-capture] checkpointed {len(progress['rows'])}/24")
    finally:
        release_model(model)
        print("[model] unloaded", flush=True)


def run_matched_patch(args, protocol, frozen):
    paths = matched_capture_paths()
    receipt = json.loads(paths["receipt"].read_text())
    if not receipt.get("complete") or not receipt.get("finite"):
        raise RuntimeError("complete matched capture receipt required")
    if receipt.get("freeze_id") != protocol["freeze_id"]:
        raise RuntimeError("matched capture receipt freeze mismatch")
    capture_rows = json.loads(paths["rows"].read_text())
    activations = np.load(paths["activations"], mmap_mode="r")
    row_by_cell = {row["cell_id"]: row for row in capture_rows}
    index_by_cell = {row["cell_id"]: row["index"] for row in capture_rows}
    pairs = protocol["protocol"]["matched_patch"]["pairs"]
    cell_lookup = {cell["cell_id"]: cell for cell in frozen["cells"]}
    output = paths["output"]
    progress_path = output / "patch-progress.json"
    result_path = output / "patch-result.json"
    progress = {
        "freeze_id": protocol["freeze_id"],
        "code_sha256": protocol["code_sha256"],
        "cells": [],
    }
    if progress_path.exists():
        progress = json.loads(progress_path.read_text())
        if progress.get("freeze_id") != protocol["freeze_id"]:
            raise RuntimeError("matched patch progress freeze mismatch")
    completed_keys = [f"{row['layer']}::{row['site']}" for row in progress["cells"]]
    grid = [(layer, site) for layer in range(36) for site in SITES]
    if completed_keys != [f"{layer}::{site}" for layer, site in grid[: len(completed_keys)]]:
        raise RuntimeError("matched patch grid is not contiguous")
    model, tokenizer, layers, choices, device = load_model(args.model)
    start_swap = swap_used_mib()
    try:
        prepared = {}
        for pair in pairs:
            for status, key in [
                ("verified", "verified_cell_id"),
                ("counterfeit", "counterfeit_cell_id"),
            ]:
                cell_id = pair[key]
                cell = cell_lookup[cell_id]
                encoded, positions = encode_cell(tokenizer, cell, pair["canary"])
                prepared[cell_id] = {
                    "cell": cell,
                    "encoded": encoded,
                    "positions": positions,
                    "baseline": semantic_logits(
                        row_by_cell[cell_id]["baseline_letter_logits"],
                        cell["letter_to_semantic"],
                    ),
                }
        start = len(progress["cells"])
        end = min(len(grid), start + args.limit)
        for grid_index in range(start, end):
            layer_index, site = grid[grid_index]
            site_index = SITES.index(site)
            forward = []
            reverse = []
            started = time.monotonic()
            for pair in pairs:
                verified_id = pair["verified_cell_id"]
                counterfeit_id = pair["counterfeit_cell_id"]
                verified_source = np.asarray(
                    activations[index_by_cell[verified_id], layer_index, site_index, :]
                )
                counterfeit_source = np.asarray(
                    activations[index_by_cell[counterfeit_id], layer_index, site_index, :]
                )
                counterfeit_item = prepared[counterfeit_id]
                verified_item = prepared[verified_id]
                patched_counterfeit_letter = intervene(
                    model,
                    layers,
                    counterfeit_item["encoded"],
                    choices,
                    device,
                    layer_index,
                    counterfeit_item["positions"][site_index],
                    verified_source,
                    replace=True,
                )
                patched_verified_letter = intervene(
                    model,
                    layers,
                    verified_item["encoded"],
                    choices,
                    device,
                    layer_index,
                    verified_item["positions"][site_index],
                    counterfeit_source,
                    replace=True,
                )
                patched_counterfeit = semantic_logits(
                    patched_counterfeit_letter,
                    counterfeit_item["cell"]["letter_to_semantic"],
                )
                patched_verified = semantic_logits(
                    patched_verified_letter,
                    verified_item["cell"]["letter_to_semantic"],
                )
                forward.append(
                    contrast(patched_counterfeit, "accept", "reject")
                    - contrast(counterfeit_item["baseline"], "accept", "reject")
                )
                reverse.append(
                    contrast(patched_verified, "accept", "reject")
                    - contrast(verified_item["baseline"], "accept", "reject")
                )
            row = {
                "grid_index": grid_index,
                "layer": layer_index,
                "site": site,
                "verified_into_counterfeit_mean": float(np.mean(forward)),
                "counterfeit_into_verified_mean": float(np.mean(reverse)),
                "forward_effects": forward,
                "reverse_effects": reverse,
                "n_pairs": len(pairs),
                "elapsed_seconds": time.monotonic() - started,
            }
            if not np.isfinite(
                [row["verified_into_counterfeit_mean"], row["counterfeit_into_verified_mean"]]
            ).all():
                raise RuntimeError(f"non-finite matched patch cell: {grid_index}")
            progress["cells"].append(row)
            atomic_json(progress_path, progress)
            print(
                f"[matched-patch] {grid_index + 1}/180 "
                f"layer={layer_index} site={site} "
                f"forward={row['verified_into_counterfeit_mean']:.6f} "
                f"reverse={row['counterfeit_into_verified_mean']:.6f}",
                flush=True,
            )
            reason = runtime_stop_reason(start_swap)
            if reason:
                print(f"[stop] {reason}", flush=True)
                break
        if len(progress["cells"]) == 180:
            primary = next(
                row
                for row in progress["cells"]
                if row["layer"] == PRIMARY_LAYER and row["site"] == PRIMARY_SITE
            )
            result = {
                **progress,
                "primary": primary,
                "primary_pass": bool(
                    primary["verified_into_counterfeit_mean"] > 0
                    and primary["counterfeit_into_verified_mean"] < 0
                ),
                "complete": True,
            }
            atomic_json(result_path, result)
            print(f"[matched-patch] complete primary_pass={result['primary_pass']}")
        else:
            print(f"[matched-patch] checkpointed {len(progress['cells'])}/180")
    finally:
        release_model(model)
        print("[model] unloaded", flush=True)


def static_validate(protocol, frozen, rows, activations):
    facts = protocol_facts(frozen, rows, activations)
    basis = factor_basis(activations, rows, frozen)
    differences, strata = matched_train_strata(activations, rows, frozen)
    output = {
        "ok": True,
        "freeze_id": protocol["freeze_id"],
        "code_sha256": protocol["code_sha256"],
        "original_frozen_sha256": frozen["frozen_sha256"],
        "activation_shape": list(activations.shape),
        "finite_true_direction": bool(np.isfinite(basis["provenance"]).all()),
        "true_direction_norm": float(np.linalg.norm(basis["provenance"])),
        "true_scale": basis["scale"],
        "permutation_strata": len(strata),
        "permutation_difference_shape": list(differences.shape),
        "control_signs_sha256": facts["fair_null"]["control_signs_sha256"],
        "fair_test_cells": len(facts["fair_null"]["test_cell_ids"]),
        "patch_pairs": len(facts["matched_patch"]["pairs"]),
        "patch_grid_cells": len(facts["matched_patch"]["layers_zero_based"])
        * len(facts["matched_patch"]["sites"]),
    }
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=["static-validate", "fair-null", "matched-capture", "matched-patch"],
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, default=32)
    args = parser.parse_args()
    if args.limit <= 0:
        raise RuntimeError("--limit must be positive")
    frozen, rows, activations = load_inputs()
    protocol = load_and_verify_protocol(frozen, rows, activations)
    if args.model != protocol["protocol"]["model"]:
        raise RuntimeError("model differs from frozen protocol")
    if args.mode == "static-validate":
        static_validate(protocol, frozen, rows, activations)
    elif args.mode == "fair-null":
        run_fair_null(args, protocol, frozen, rows, activations)
    elif args.mode == "matched-capture":
        run_matched_capture(args, protocol, frozen)
    elif args.mode == "matched-patch":
        run_matched_patch(args, protocol, frozen)


if __name__ == "__main__":
    main()
