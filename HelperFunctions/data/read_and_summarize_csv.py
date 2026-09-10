#
# import pandas as pd
#
# from HelperFunctions.data.convert_to_numeric import convert_to_numeric
#
#
# def read_and_summarize_csv(include_second_coder:bool=False) -> None:
#
#     # The input file uses semicolons as separators.
#     df = pd.read_csv("study_data.csv", sep=";")
#
#     required_columns = {"participant", "task_id", "group", "TTU", "DOU"}
#     missing_columns = required_columns - set(df.columns)
#
#     if missing_columns:
#         raise ValueError(
#             f"Missing required columns: {', '.join(sorted(missing_columns))}"
#         )
#
#     numeric_columns = ["TTU", "DOU"]
#
#     if include_second_coder:
#         second_coder_columns = ["TTU_second_coder", "DOU_second_coder"]
#         missing_second_coder = set(second_coder_columns) - set(df.columns)
#
#         if missing_second_coder:
#             raise ValueError(
#                 "Missing second-coder columns: "
#                 + ", ".join(sorted(missing_second_coder))
#             )
#
#         numeric_columns.extend(second_coder_columns)
#
#     for column in numeric_columns:
#         df[column] = convert_to_numeric(df[column])
#
#     aggregations = {
#         "row_count": ("participant", "size"),
#         "participant_count": ("participant", "nunique"),
#         "TTU_total": ("TTU", lambda values: values.sum(min_count=1)),
#         "TTU_average": ("TTU", "mean"),
#         "DOU_total": ("DOU", lambda values: values.sum(min_count=1)),
#         "DOU_average": ("DOU", "mean"),
#     }
#
#     if include_second_coder:
#         aggregations.update(
#             {
#                 "TTU_second_coder_total": (
#                     "TTU_second_coder",
#                     lambda values: values.sum(min_count=1),
#                 ),
#                 "TTU_second_coder_average": ("TTU_second_coder", "mean"),
#                 "DOU_second_coder_total": (
#                     "DOU_second_coder",
#                     lambda values: values.sum(min_count=1),
#                 ),
#                 "DOU_second_coder_average": ("DOU_second_coder", "mean"),
#             }
#         )
#
#     result = (
#         df.groupby(["task_id", "group"], dropna=False)
#         .agg(**aggregations)
#         .reset_index()
#         .sort_values(["task_id", "group"])
#     )
#     return result
#
#
#
#
# if __name__ == '__main__':
#     df = read_and_summarize_csv()
#     df.to_csv("study_total_and_averages_per_task_and_group.csv", sep=";", index=False)