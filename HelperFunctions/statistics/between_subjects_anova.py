from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols
from SETTINGS import alpha


def between_subjects_anova(df, potential_difference_determining_column: str, value_col="measured_value",
                           print_info: bool = True):
    """
    One-way between-subjects ANOVA for independent groups.
    Returns:
        - df_agg: aggregated DataFrame (median per group)
        - result_string: formatted result string (including p-value, eta-squared, medians)
    Compatible with post_hoc_within and compact_letter_display.
    """
    if df.empty:
        print("⚠️ DataFrame ist leer – keine ANOVA möglich.")
        return None, None

    # Bereite Daten für OLS vor
    # Formel: value_col ~ potential_difference_determining_column
    model = ols(f"{value_col} ~ C({potential_difference_determining_column})", data=df).fit()
    aov_table = anova_lm(model, typ=2)

    # Extrahiere p-Wert und Partial Eta-Squared
    p_val = aov_table["PR(>F)"].iloc[0]
    partial_eta_squared = "??"# TODO
    # partial_eta_squared = f"{partial_eta_squared:.4g}"

    # Erstelle Ergebnis-String
    if p_val < alpha:
        result = f"→ Significant difference between groups (p = {p_val:.4g}, eta = {partial_eta_squared})"
        # Medians der Gruppen
        medians = df.groupby(potential_difference_determining_column)[value_col].median()
        sorted_medians = medians.sort_index()  # sortiert nach Gruppennamen
        result += "\n\t\t\u001b[1m→ Median Values of all Groups:\u001b[0m"
        for group_name, median_val in sorted_medians.items():
            if value_col == "TTU":
                precision = 0  # only int precision TUU (s)
            else:
                precision = 3
            result += f"\n\t\t  - Task {group_name} → {median_val:.{precision}f}"
    else:
        result = f"→ No significant difference (p = {p_val:.4g}, eta = {partial_eta_squared})"

    if print_info:
        print("\n\t=== Between-Subjects ANOVA ===")
        print("\t", str(aov_table).replace("\n", "\n\t"), sep="")

    return df, result

