from Study import participants
from HelperFunctions.get_data import get_data

alpha = 0.05

# Daten laden
df = get_data(participants=participants, task_ids=[i for i in range(1, 18)])
#TODO entries in some columns are enum values -> move them to their name for csv

for column in ["structural_aspects",
                    "operation_type",
                    "operand_type",
                    "result_type",
                    "Ref_direction",
                    "Ref_dispersion"]:
    df[column] = df[column].apply(
        lambda x: [i.name for i in x]
    )
df.to_csv("study_data.csv", sep=";", index=False)# INFO! important for R-usage


df["id"] = df["id"].apply(lambda x: x.replace("task_", "")).astype(int)







