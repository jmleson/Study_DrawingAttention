import json

import pandas as pd

from HelperFunctions.data.convert_to_numeric import convert_to_numeric


def create_participant_totals(
    frame: pd.DataFrame,
    value_column: str,
) -> str:
    """
    Calculate the total value for every participant in the frame.

    Participants are identified by both `group` and `participant`.
    The result is stored as a JSON list suitable for a CSV field:

        [
            [group, participant, total],
            ...
        ]
    """

    participant_values = (
        frame.groupby(
            ["group", "participant"],
            dropna=False,
            as_index=False,
        )[value_column]
        .sum(min_count=1)
        .sort_values(
            ["group", "participant"],
            key=lambda values: values.astype(str),
        )
    )

    values = []

    for _, row in participant_values.iterrows():
        group = row["group"]
        participant = row["participant"]
        total = row[value_column]

        values.append(
            [
                (
                    None
                    if pd.isna(group)
                    else str(group)[0]
                ),
                (
                    None
                    if pd.isna(participant)
                    else str(participant)
                ),
                (
                    None
                    if pd.isna(total)
                    else float(total)
                ),
            ]
        )

    return json.dumps(values, ensure_ascii=False)


def add_participant_total_columns(
    result: pd.DataFrame,
    source_df: pd.DataFrame,
    grouping_columns: list[str],
    numeric_columns: list[str],
) -> pd.DataFrame:
    """
    Add one participant-total-list column for every numeric column.

    Examples:
    - TTU -> TTU_participant_totals
    - DOU -> DOU_participant_totals
    """

    if not grouping_columns:
        # The entire source table corresponds to one result row.
        for column in numeric_columns:
            result[f"{column}_participant_totals"] = [
                create_participant_totals(source_df, column)
            ]

        return result

    participant_total_rows = []

    # groupby() accepts a scalar for one grouping column and a list
    # for multiple grouping columns.
    groupby_argument = (
        grouping_columns[0]
        if len(grouping_columns) == 1
        else grouping_columns
    )

    for grouping_key, frame in source_df.groupby(
        groupby_argument,
        dropna=False,
        sort=False,
    ):
        if len(grouping_columns) == 1:
            grouping_key = (grouping_key,)

        row = dict(zip(grouping_columns, grouping_key))

        for column in numeric_columns:
            row[f"{column}_participant_totals"] = (
                create_participant_totals(frame, column)
            )

        participant_total_rows.append(row)

    participant_totals = pd.DataFrame(participant_total_rows)

    return result.merge(
        participant_totals,
        on=grouping_columns,
        how="left",
        validate="one_to_one",
    )


def move_counts_before_participant_totals(
    result: pd.DataFrame,
    numeric_columns: list[str],
) -> pd.DataFrame:
    """
    Place each value-count column directly before its corresponding
    participant-total-list column.
    """

    result_columns = list(result.columns)

    for column in numeric_columns:
        count_column = f"{column}_count"
        participant_totals_column = (
            f"{column}_participant_totals"
        )

        if count_column not in result_columns:
            continue

        if participant_totals_column not in result_columns:
            continue

        result_columns.remove(count_column)

        totals_position = result_columns.index(
            participant_totals_column
        )

        result_columns.insert(
            totals_position,
            count_column,
        )

    return result[result_columns]


def read_and_summarize_csv(
    input_file: str = "study_data.csv",
    group_by: str = "task_and_group",
    include_second_coder: bool = False,
) -> pd.DataFrame:
    """
    Read and summarize the study data.

    Supported groupings:
    - task_and_group
    - task
    - group
    - all

    For every numeric column, the output contains:
    - total
    - average
    - count of values used for the average
    - participant totals as a JSON list

    No fixed number of tasks, groups, or participants is required.
    """

    df = pd.read_csv(
        input_file,
        sep=";",
    )

    required_columns = {
        "participant",
        "task_id",
        "group",
        "TTU",
        "DOU",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    grouping_options = {
        "task_and_group": ["task_id", "group"],
        "task": ["task_id"],
        "group": ["group"],
        "all": [],
    }

    if group_by not in grouping_options:
        raise ValueError(
            f"Invalid group_by value: {group_by!r}. "
            f"Choose from: {', '.join(grouping_options)}"
        )

    grouping_columns = grouping_options[group_by]

    numeric_columns = [
        "TTU",
        "DOU",
    ]

    if include_second_coder:
        second_coder_columns = [
            "TTU_second_coder",
            "DOU_second_coder",
        ]

        missing_second_coder_columns = (
            set(second_coder_columns) - set(df.columns)
        )

        if missing_second_coder_columns:
            raise ValueError(
                "Missing second-coder columns: "
                + ", ".join(
                    sorted(missing_second_coder_columns)
                )
            )

        numeric_columns.extend(second_coder_columns)

    # Convert all values used for calculations to numeric values.
    # Invalid values should become NaN, depending on the behavior of
    # convert_to_numeric().
    for column in numeric_columns:
        df[column] = convert_to_numeric(df[column])

    # No fixed-structure validation is performed.
    aggregations = {
        "row_count": (
            "participant",
            "size",
        ),
        "participant_count": (
            "participant",
            "nunique",
        ),
        "task_count": (
            "task_id",
            "nunique",
        ),
        "group_count": (
            "group",
            "nunique",
        ),
    }

    # Add total, average, and the number of valid values used for
    # the average for every numeric column.
    for column in numeric_columns:
        aggregations[f"{column}_total"] = (
            column,
            lambda values: values.sum(min_count=1),
        )

        aggregations[f"{column}_average"] = (
            column,
            "mean",
        )

        # count() ignores NaN values. Therefore, this is the number
        # of values actually used to calculate the average.
        aggregations[f"{column}_count"] = (
            column,
            "count",
        )

    if group_by == "all":
        result = (
            df.assign(summary_scope="all")
            .groupby(
                "summary_scope",
                dropna=False,
            )
            .agg(**aggregations)
            .reset_index()
        )
    else:
        result = (
            df.groupby(
                grouping_columns,
                dropna=False,
            )
            .agg(**aggregations)
            .reset_index()
        )

    # Add participant-total JSON lists.
    result = add_participant_total_columns(
        result=result,
        source_df=df,
        grouping_columns=grouping_columns,
        numeric_columns=numeric_columns,
    )

    # Put each count directly before its participant-total list.
    result = move_counts_before_participant_totals(
        result=result,
        numeric_columns=numeric_columns,
    )

    if grouping_columns:
        result = result.sort_values(
            grouping_columns,
            key=lambda values: values.astype(str),
        ).reset_index(drop=True)

    return result


if __name__ == "__main__":
    by_task_and_group = read_and_summarize_csv(
        input_file="study_data.csv",
        group_by="task_and_group",
    )

    by_task = read_and_summarize_csv(
        input_file="study_data.csv",
        group_by="task",
    )

    by_group = read_and_summarize_csv(
        input_file="study_data.csv",
        group_by="group",
    )

    whole_table = read_and_summarize_csv(
        input_file="study_data.csv",
        group_by="all",
    )

    print("\n--- By task and group ---")
    print(by_task_and_group.to_string(index=False))

    print("\n--- By task, all groups combined ---")
    print(by_task.to_string(index=False))

    print("\n--- By group, all tasks combined ---")
    print(by_group.to_string(index=False))

    print("\n--- Whole table ---")
    print(whole_table.to_string(index=False))

    by_task_and_group.to_csv(
        "summary_by_task_and_group.csv",
        sep=";",
        index=False,
    )

    by_task.to_csv(
        "summary_by_task.csv",
        sep=";",
        index=False,
    )

    by_group.to_csv(
        "summary_by_group.csv",
        sep=";",
        index=False,
    )

    whole_table.to_csv(
        "summary_whole_table.csv",
        sep=";",
        index=False,
    )