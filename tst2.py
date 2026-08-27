import numpy as np
import pandas as pd
import pingouin as pg
from statsmodels.stats.multitest import multipletests

from Study import participants
from HelperFunctions.get_data import get_data

alpha = 0.05

# Daten laden
df = get_data(participants=participants, task_ids=[i for i in range(1, 18)])
df["id"] = df["id"].apply(lambda x: x.replace("task_", "")).astype(int)
df["group"] = df["group"].astype("category")
df["TTU"] = df["TTU"].astype(float)

print(f"✅ Daten geladen: {df.shape[0]} Zeilen, {df['id'].nunique()} Tasks, {df['group'].nunique()} Gruppen")

# DOU-Prüfung
print("\nDOU-Werte: Anzahl der Werte, die nicht 1.0 sind")
df_notone = df[df["DOU"] != 1.0]
print(f"❗ Es gibt nur {df_notone.shape[0]} von {df.shape[0]} DOU-Werten, die nicht 1.0 sind.")
print(f"→ Das sind {100 * (1 - df_notone.shape[0] / df.shape[0]):.1f}% = 1.0")

results = []

for task_id in range(1, 18):
    df_task = df[df["id"] == task_id].copy()

    if df_task["group"].nunique() < 3:
        continue
    if df_task.groupby("group").size().min() < 2:
        continue

    df_task["TTU_log"] = np.log(df_task["TTU"])

    # ANOVA mit log(TTU)
    anova_result = pg.anova(data=df_task, dv="TTU_log", between="group", detailed=True)
    p_anova = anova_result["p_unc"].iloc[0]
    anova_sig = "Significant" if p_anova < alpha else "Not significant"

    # Kruskal-Wallis mit Original-TTU
    kruskal_result = pg.kruskal(data=df_task, dv="TTU", between="group")
    p_kruskal = kruskal_result["p_unc"].iloc[0]
    kruskal_sig = "Significant" if p_kruskal < alpha else "Not significant"

    # Statistiken
    group_stats = df_task.groupby("group")["TTU"].agg(["mean", "median", "std", "count"]).round(3)
    mean_orig = group_stats["mean"].to_dict()
    median_orig = group_stats["median"].to_dict()
    std_orig = group_stats["std"].to_dict()

    # Speichern
    results.append({
        "task_id": task_id,
        "p_anova": p_anova,
        "p_kruskal": p_kruskal,
        "anova_sig": anova_sig,
        "kruskal_sig": kruskal_sig,
        "median_TTU": median_orig,
        "mean_TTU": mean_orig,
        "std_TTU": std_orig
    })

    print(f"\n🔍 Task {task_id:2d}:")
    print(f"   → ANOVA (log): p = {p_anova:.4f} ({anova_sig})")
    print(f"   → Kruskal-Wallis: p = {p_kruskal:.4f} ({kruskal_sig})")
    print(f"   → Mean (TTU): {mean_orig}")
    print(f"   → Mediane (TTU): {median_orig}")
    print(f"   → Std-Abw. (TTU): {std_orig}")

# Ergebnisse
df_results = pd.DataFrame(results)
all_p_vals = df_results["p_anova"].values
_, p_holm, _, _ = multipletests(all_p_vals, alpha=0.05, method='holm')
df_results["p_holm"] = p_holm
df_results["holm_sig"] = df_results["p_holm"] < 0.05

print("\n" + "=" * 60)
print("🔍 SIGNIFIKANTE GRUPPENUNTERSCHIEDE (nach Holm-Korrektur):")
print("=" * 60)

significant = df_results[df_results["holm_sig"]]
if significant.empty:
    print("❗ Keine signifikanten Unterschiede nach Holm-Korrektur gefunden.")
else:
    print(significant[["task_id", "p_anova", "p_holm", "kruskal_sig"]].to_string(index=False))

# Boxplots für signifikante Tasks
if not significant.empty:
    import seaborn as sns
    import matplotlib.pyplot as plt

    print("\n📊 Boxplots für signifikante Tasks:")
    for task_id in significant["task_id"]:
        df_task = df[df["id"] == task_id]
        plt.figure(figsize=(8, 4))
        sns.boxplot(data=df_task, x="group", y="TTU")
        plt.title(f"Task {task_id}: TTU (Original) nach Gruppen")
        plt.ylabel("Bearbeitungszeit (s)")
        plt.show()