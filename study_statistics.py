#!/usr/bin/env python3
"""Robust statistical evaluation of the spreadsheet-comprehension study.

Run:
    python study_statistics.py --input study_data.csv --output results

Dependencies: pandas, numpy, scipy, statsmodels, matplotlib, seaborn
The script preserves independence by aggregating repeated task observations to
one value per participant before an overall or aspect-level Kruskal-Wallis test.
Per-task tests use one observation per participant directly.
"""
from __future__ import annotations

import argparse
import itertools
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

GROUPS = [
    "Dynamic sketch construction",
    "Formula construction",
    "Static sketch construction",
]
ASPECTS = ["COMP", "COND", "LOOK", "CELL", "RANGE", "LIT", "FUNC",
           "VAL", "BATCH", "LIST", "BACK", "FORWARD", "ON", "OFF", "CROSS"]
ALPHA = 0.05


def load_data(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    required = {"participant", "id", "group", "TTU", "DOU", "structural_aspects"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df = df.copy()
    df["task"] = df["id"].astype(str).str.replace("task_", "", regex=False).astype(int)
    df["TTU"] = pd.to_numeric(df["TTU"], errors="coerce")
    df["DOU"] = pd.to_numeric(df["DOU"], errors="coerce")
    df = df[df["group"].isin(GROUPS)]
    if (df["TTU"].dropna() <= 0).any():
        raise ValueError("TTU must be greater than zero.")
    # A participant must belong to exactly one between-subject group.
    memberships = df.groupby("participant")["group"].nunique()
    if (memberships > 1).any():
        raise ValueError("At least one participant occurs in multiple groups.")
    if df.duplicated(["participant", "task"]).any():
        raise ValueError("Duplicate participant-task rows found.")
    return df.sort_values(["task", "group", "participant"]).reset_index(drop=True)


def holm(pvalues: pd.Series) -> np.ndarray:
    out = np.full(len(pvalues), np.nan)
    ok = pvalues.notna().to_numpy()
    if ok.any():
        out[ok] = multipletests(pvalues[ok], method="holm")[1]
    return out


def epsilon_squared_kw(H: float, n: int, k: int) -> float:
    """Bias-corrected Kruskal-Wallis epsilon squared, truncated to [0, 1]."""
    if n <= k:
        return np.nan
    return float(np.clip((H - k + 1) / (n - k), 0.0, 1.0))


def rank_biserial(x: np.ndarray, y: np.ndarray) -> float:
    """Signed rank-biserial correlation. Positive means x tends to exceed y."""
    u = stats.mannwhitneyu(x, y, alternative="two-sided", method="auto").statistic
    return float(2.0 * u / (len(x) * len(y)) - 1.0)


def compact_letters(groups: list[str], pairwise: pd.DataFrame, alpha: float = ALPHA) -> dict[str, str]:
    """Compact letter display based on Holm-adjusted pairwise p-values.

    Groups sharing a letter are not significantly different. Groups with no
    letter in common are significantly different. This is inferential shorthand,
    not evidence of equivalence.
    """
    nonsig = {frozenset((g, g)) for g in groups}
    for _, r in pairwise.iterrows():
        if pd.notna(r["p_holm"]) and r["p_holm"] >= alpha:
            nonsig.add(frozenset((r["group1"], r["group2"])))
    # All maximal cliques of the non-significance graph. With three groups this
    # is exact, transparent, and avoids a third-party CLD dependency.
    cliques = []
    for size in range(len(groups), 0, -1):
        for subset in itertools.combinations(groups, size):
            if all(frozenset(pair) in nonsig for pair in itertools.combinations(subset, 2)):
                s = set(subset)
                if not any(s < old for old in cliques):
                    cliques.append(s)
    # Keep only cliques needed to cover all non-significant pairs and singletons.
    targets = {frozenset((g,)) for g in groups}
    targets |= {p for p in nonsig if len(p) == 2}
    chosen, covered = [], set()
    while not targets.issubset(covered):
        best = max(cliques, key=lambda c: len(({frozenset((g,)) for g in c} |
                    {frozenset(p) for p in itertools.combinations(c, 2)}) - covered))
        chosen.append(best)
        covered |= {frozenset((g,)) for g in best}
        covered |= {frozenset(p) for p in itertools.combinations(best, 2)}
        cliques.remove(best)
    letters = {g: "" for g in groups}
    for i, clique in enumerate(chosen):
        letter = chr(ord("a") + i)
        for g in clique:
            letters[g] += letter
    return letters


def analyse_stratum(data: pd.DataFrame, outcome: str, label: str) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    d = data[["participant", "group", outcome]].dropna().copy()
    arrays = [d.loc[d.group == g, outcome].to_numpy() for g in GROUPS]
    if any(len(a) == 0 for a in arrays):
        return ({"stratum": label, "outcome": outcome, "H": np.nan, "df": 2,
                 "p_raw": np.nan, "epsilon_squared": np.nan, "n": len(d)},
                pd.DataFrame(), pd.DataFrame())
    if d[outcome].nunique() == 1:
        H, p = 0.0, 1.0
    else:
        H, p = stats.kruskal(*arrays)
    omnibus = {"stratum": label, "outcome": outcome, "H": H, "df": len(GROUPS)-1,
               "p_raw": p, "epsilon_squared": epsilon_squared_kw(H, len(d), len(GROUPS)),
               "n": len(d)}
    desc = (d.groupby("group", observed=True)[outcome]
              .agg(n="count", median="median", q1=lambda s: s.quantile(.25),
                   q3=lambda s: s.quantile(.75), mean="mean", sd="std")
              .reindex(GROUPS).reset_index())
    desc.insert(0, "outcome", outcome); desc.insert(0, "stratum", label)
    rows = []
    for g1, g2 in itertools.combinations(GROUPS, 2):
        x = d.loc[d.group == g1, outcome].to_numpy()
        y = d.loc[d.group == g2, outcome].to_numpy()
        test = stats.mannwhitneyu(x, y, alternative="two-sided", method="auto")
        rows.append({"stratum": label, "outcome": outcome, "group1": g1, "group2": g2,
                     "U": test.statistic, "p_raw": test.pvalue,
                     "rank_biserial_g1_vs_g2": rank_biserial(x, y),
                     "median_difference_g1_minus_g2": np.median(x)-np.median(y)})
    pair = pd.DataFrame(rows)
    pair["p_holm"] = holm(pair["p_raw"])
    pair["significant_holm"] = pair["p_holm"] < ALPHA
    letters = compact_letters(GROUPS, pair)
    desc["CLD"] = desc["group"].map(letters)
    return omnibus, pair, desc


def participant_summary(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    # Median is robust and ensures one independent value per participant.
    return (df.groupby(["participant", "group"], as_index=False, observed=True)[outcome]
              .median())


def aspect_mask(series: pd.Series, aspect: str) -> pd.Series:
    # Match enum token exactly, e.g. STRUCTURALTASKASPECT.COMP, avoiding iCOMP.
    return series.astype(str).str.contains(rf"STRUCTURALTASKASPECT\.{re.escape(aspect)}(?:\W|$)", regex=True)


def run_all(df: pd.DataFrame, output: str | Path) -> None:
    out = Path(output); out.mkdir(parents=True, exist_ok=True)
    omnibus_rows, pair_frames, desc_frames = [], [], []

    # Overall: participant-level median, not all 357 rows as independent cases.
    for outcome in ["TTU", "DOU"]:
        om, pw, ds = analyse_stratum(participant_summary(df, outcome), outcome, "Overall participant median")
        omnibus_rows.append(om); pair_frames.append(pw); desc_frames.append(ds)

    # Per task: naturally one row per participant.
    for task, sub in df.groupby("task", sort=True):
        for outcome in ["TTU", "DOU"]:
            om, pw, ds = analyse_stratum(sub, outcome, f"Task {task}")
            omnibus_rows.append(om); pair_frames.append(pw); desc_frames.append(ds)

    # Structural aspects: filter tasks, then aggregate within participant first.
    for aspect in ASPECTS:
        sub = df[aspect_mask(df["structural_aspects"], aspect)]
        if sub.empty:
            continue
        for outcome in ["TTU", "DOU"]:
            agg = participant_summary(sub, outcome)
            om, pw, ds = analyse_stratum(agg, outcome, f"Aspect {aspect}")
            om["tasks_included"] = ",".join(map(str, sorted(sub.task.unique())))
            omnibus_rows.append(om); pair_frames.append(pw); desc_frames.append(ds)

    omnibus = pd.DataFrame(omnibus_rows)
    pairwise = pd.concat([x for x in pair_frames if not x.empty], ignore_index=True)
    descriptives = pd.concat([x for x in desc_frames if not x.empty], ignore_index=True)

    # Holm adjustment across omnibus tests within each coherent family:
    # outcome x analysis type (overall/task/aspect). Pairwise Holm is within stratum.
    omnibus["family"] = np.select(
        [omnibus.stratum.str.startswith("Task"), omnibus.stratum.str.startswith("Aspect")],
        ["per_task", "per_aspect"], default="overall")
    omnibus["p_holm_family"] = np.nan
    for _, idx in omnibus.groupby(["outcome", "family"]).groups.items():
        omnibus.loc[idx, "p_holm_family"] = holm(omnibus.loc[idx, "p_raw"])
    omnibus["significant_raw"] = omnibus["p_raw"] < ALPHA
    omnibus["significant_holm_family"] = omnibus["p_holm_family"] < ALPHA

    omnibus.to_csv(out / "omnibus_tests.csv", index=False)
    pairwise.to_csv(out / "pairwise_tests.csv", index=False)
    descriptives.to_csv(out / "descriptives_and_cld.csv", index=False)

    audit = pd.DataFrame({
        "metric": ["rows", "participants", "tasks", "DOU_equal_1_count", "DOU_equal_1_percent"],
        "value": [len(df), df.participant.nunique(), df.task.nunique(),
                  int(df.DOU.eq(1).sum()), 100 * df.DOU.eq(1).mean()]})
    audit.to_csv(out / "data_audit.csv", index=False)

    # Concise console result.
    print("\nData audit")
    print(audit.to_string(index=False))
    print("\nOmnibus tests significant after family-wise Holm correction")
    sig = omnibus[omnibus.significant_holm_family]
    print(sig[["stratum", "outcome", "H", "p_raw", "p_holm_family", "epsilon_squared"]]
          .to_string(index=False) if len(sig) else "None")
    print(f"\nFull outputs written to: {out.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="study_data.csv")
    parser.add_argument("--output", default="study_results")
    args = parser.parse_args()
    run_all(load_data(args.input), args.output)


if __name__ == "__main__":
    main()
