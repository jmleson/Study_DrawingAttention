from Study import participants, tasks
from HelperFunctions.get_data import get_data




def data_to_csv():
    for p in participants:
        for t in tasks:
            p.create_task_files(task=t)
            p.create_task_files_2nd_coding(task=t)

    # Daten laden
    df = get_data(participants=participants, task_ids=[i for i in range(1, 18)])
    #TODO entries in some columns are enum values -> move them to their name for csv

    for column in ["structural_aspects",
                        # "operation_type",
                        # "operand_type",
                        # "result_type",
                        # "Ref_direction",
                        # "Ref_dispersion"
                   ]:
        df[column] = df[column].apply(
            lambda x: [i.name for i in x]
        )
    df.to_csv("study_data.csv", sep=";", index=False)# INFO! important for R-usage

    df["task_id"] = df["task_id"].apply(lambda x: x.replace("task_", "")).astype(int)
    return df


if __name__ == '__main__':
    data_to_csv()

