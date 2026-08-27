import warnings

import pandas as pd

from HelperFunctions.get_data import get_data
from HelperFunctions.statistics.between_subjects_anova import between_subjects_anova
from HelperFunctions.statistics.post_hoc_between import post_hoc_between
from StudyElements.Participant import Participant
from HelperFunctions.statistics.compact_letter_display import compact_letter_display
from HelperFunctions.statistics.post_hoc_within import post_hoc_within
from HelperFunctions.statistics.within_subjects_anova import within_subjects_anova
from StudyElements.STRUCTURALTASKASPECT import STRUCTURALTASKASPECT


def statistics_category(category:str, task_ids: list[int], participants: list[Participant]):
    if category not in ["TTU", "DOU"]:
        raise ValueError("Category unknown")

    df = get_data(participants=participants, task_ids=task_ids)
    df["id"] = df["id"].apply(lambda x: x.replace("task_", "")).astype(int)

    results = ""

    results += run_category(df=df, category=category)# within_subjects_anova -> statistics_<category>.txt

    results += run_diff_per_task(df=df, category=category)# between_subjects_anova -> statistics_<category>_TASKS.txt


    results += run_structure(df=df, category=category, participants=participants)# within_subjects_anova
    results += run_groups(df=df, category=category, participants=participants)# within_subjects_anova

    return results



def run_category(df:pd.Dataframe, category:str):
    """

    :param df:
    :param category: "DOI" / "TTU"
    :return:
    """
    results = f"DIFFERENCES IN \u001b[1m{category}\u001b[0m:\n"
    df_agg, result_total = within_subjects_anova(df=df, print_info=False, value_col=category,
                                                 potential_difference_determining_column="group", subject_col="id")
    results += "\t" + result_total + "\n"
    sig_matrix, groups, n = post_hoc_within(df_agg, group_col="group", value_col=category, subject_col="id")
    cld_strings_total = compact_letter_display(groups, n, sig_matrix, print_info=False)
    results += f"\tCompact-Letter-Display: {cld_strings_total}\n"
    with open(f"results/statistics_{category}.txt", "w") as f:
        f.write(results)
    return results


def run_diff_per_task(df:pd.DataFrame, category:str):
    results = f"\nDIFFERENCES IN \u001b[1m{category} PER TASK\u001b[0m:\n"
    df_between, result_total = between_subjects_anova(df=df, print_info=False, value_col=category,
                                                      potential_difference_determining_column="id")
    df_between["id"] = df_between["id"].apply(lambda x: f"Task {x}")
    results += "\t" + result_total + "\n"
    sig_matrix, groups, n = post_hoc_between(df_between, value_col=category, subject_col="id")
    cld_strings_total = compact_letter_display(groups, n, sig_matrix, print_info=False)
    results += f"\tCompact-Letter-Display:  {cld_strings_total}\n"
    with open(f"results/statistics_{category}_TASKS.txt", "w") as f:
        f.write(results)
    return results


def run_structure(df:pd.DataFrame, category:str, participants:list):
    total_results = ""
    with open(f"results/statistics_{category}_STRUCTURE.txt", "w") as f:
        f.write("Evaluating structural aspects of tasks:\n\n")
    for s in STRUCTURALTASKASPECT:
        df_filtered = df[df["structural_aspects"].apply(lambda lst: any(item.value == s.value for item in lst))].copy()

        results = f"DIFFERENCES IN {category}, {s.name} (included tasks = {len(df_filtered)/len(participants)}):\n"
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("always", category=RuntimeWarning)
            df_agg, result_total = within_subjects_anova(df=df_filtered, print_info=False, value_col=category,
                                                     potential_difference_determining_column="group", subject_col="id")
        if result_total is not None:
            results += "\t" + result_total + "\n"
            if not "No significant" in result_total:
                sig_matrix, groups, n = post_hoc_within(df_agg, group_col="group", value_col=category, subject_col="id")
                cld_strings_total = compact_letter_display(groups, n, sig_matrix, print_info=False)
                results += f"\tCompact-Letter-Display: {cld_strings_total}\n\n"
            with open(f"results/statistics_{category}_STRUCTURE.txt", "a") as f:
                f.write(results)
        total_results += results + "\n"
    return total_results


def run_groups(df:pd.DataFrame, category:str, participants:list):
    total_results = ""
    with open(f"results/statistics_{category}_GROUPS.txt", "w") as f:
        f.write("Evaluating structural aspects of tasks in groups:\n\n")
    types = ["operation type", "operand type", "result type", "Ref. direction", "Ref. dispersion"]
    for type in types:
        df[type] = df[type].apply(lambda lst: "-".join(sorted([i.name for i in lst])))
        for group, df_group in df.groupby(type, sort=False):
            if len(group) == 0:
                raise Exception("invalid group produced")
            if len(df_group) < len(participants):
                continue
            if not "-" in group:
                # only one Enum value included -> already processed in STRUCTURE
                continue
            results = f"DIFFERENCES IN {category} for group {group}\n\t({type}) (included tasks = {len(df_group)/len(participants)}:\n"
            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings("always", category=RuntimeWarning)
                df_agg, result_total = within_subjects_anova(df=df_group, print_info=False, value_col=category,
                                                         potential_difference_determining_column="group", subject_col="id")
            if result_total is not None:
                results += "\t" + result_total + "\n"
                if not "No significant" in result_total:
                    sig_matrix, groups, n = post_hoc_within(df_agg, group_col="group", value_col=category, subject_col="id")
                    cld_strings_total = compact_letter_display(groups, n, sig_matrix, print_info=False)
                    results += f"\tCompact-Letter-Display: {cld_strings_total}\n\n"
                with open(f"results/statistics_{category}_GROUPS.txt", "a") as f:
                    f.write(results)
            total_results += results + "\n"
    return total_results