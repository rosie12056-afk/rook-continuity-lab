import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results/formal/analysis/scored-canonical.jsonl"
OUTPUT = ROOT / "results/formal/analysis/covariate-sensitivity.json"


def load_frame():
    rows = [json.loads(line) for line in INPUT.read_text().splitlines() if line.strip()]
    frame = pd.DataFrame(rows)
    frame["input_tokens"] = frame["usage"].map(lambda value: value.get("input_tokens", 0))
    frame["input_z"] = frame.groupby("model_id")["input_tokens"].transform(
        lambda values: (values - values.mean()) / (values.std(ddof=0) or 1)
    )
    return frame


def design_exp12(frame):
    data = frame[frame["experiment"] == "exp12"].copy()
    columns = {"intercept": np.ones(len(data)), "input_z": data["input_z"].to_numpy()}
    for condition in ["B", "C", "D", "E"]:
        columns[f"condition_{condition}"] = (data["condition_id"] == condition).astype(float).to_numpy()
    models = sorted(data["model_id"].unique())
    reference = "gpt-sol-clean"
    for model in models:
        if model != reference:
            columns[f"model_{model}"] = (data["model_id"] == model).astype(float).to_numpy()
    return data, pd.DataFrame(columns, index=data.index), [f"condition_{value}" for value in ["B", "C", "D", "E"]]


def design_exp3(frame):
    data = frame[frame["experiment"] == "exp3"].copy()
    d = (data["condition_id"] == "D").astype(float).to_numpy()
    e = (data["condition_id"] == "E").astype(float).to_numpy()
    f = (data["framing_id"] == "F").astype(float).to_numpy()
    columns = {
        "intercept": np.ones(len(data)),
        "condition_D": d,
        "condition_E": e,
        "frame_F": f,
        "D_x_F": d * f,
        "E_x_F": e * f,
        "input_z": data["input_z"].to_numpy(),
    }
    models = sorted(data["model_id"].unique())
    reference = "gpt-sol-clean"
    for model in models:
        if model != reference:
            columns[f"model_{model}"] = (data["model_id"] == model).astype(float).to_numpy()
    return data, pd.DataFrame(columns, index=data.index), ["frame_F", "D_x_F", "E_x_F"]


def fit(y, x):
    beta, *_ = np.linalg.lstsq(x.to_numpy(), y.to_numpy(), rcond=None)
    return pd.Series(beta, index=x.columns)


def cluster_bootstrap(data, x, expressions, iterations=2000, seed=20260831):
    rng = np.random.default_rng(seed)
    scenarios = np.array(sorted(data["scenario_id"].unique()))
    estimates = {name: [] for name in expressions}
    for _ in range(iterations):
        sampled = rng.choice(scenarios, size=len(scenarios), replace=True)
        indexes = np.concatenate([data.index[data["scenario_id"] == scenario].to_numpy() for scenario in sampled])
        beta = fit(data.loc[indexes, "rubric_mean"], x.loc[indexes])
        for name, terms in expressions.items():
            estimates[name].append(sum(multiplier * beta[term] for term, multiplier in terms.items()))
    result = {}
    base = fit(data["rubric_mean"], x)
    for name, terms in expressions.items():
        values = np.array(estimates[name])
        point = sum(multiplier * base[term] for term, multiplier in terms.items())
        result[name] = {"estimate": float(point), "ci95": [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))]}
    return result


frame = load_frame()
exp12_data, exp12_x, _ = design_exp12(frame)
exp12_expressions = {
    "B_vs_A": {"condition_B": 1},
    "C_vs_A": {"condition_C": 1},
    "D_vs_A": {"condition_D": 1},
    "E_vs_A": {"condition_E": 1},
    "input_token_covariate": {"input_z": 1},
}
exp3_data, exp3_x, _ = design_exp3(frame)
exp3_expressions = {
    "A_F_vs_T": {"frame_F": 1},
    "D_F_vs_T": {"frame_F": 1, "D_x_F": 1},
    "E_F_vs_T": {"frame_F": 1, "E_x_F": 1},
    "input_token_covariate": {"input_z": 1},
}

result = {
    "schema_version": 1,
    "method": "OLS fixed effects with scenario-cluster percentile bootstrap",
    "iterations": 2000,
    "exp12": cluster_bootstrap(exp12_data, exp12_x, exp12_expressions, seed=20260831),
    "exp3": cluster_bootstrap(exp3_data, exp3_x, exp3_expressions, seed=20260832),
}
OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
