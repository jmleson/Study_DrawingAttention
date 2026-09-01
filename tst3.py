import pandas as pd
from rpy2 import robjects
from rpy2.robjects import pandas2ri, Formula
from rpy2.robjects.packages import importr


# Daten laden
df = get_data(participants=participants, task_ids=[i for i in range(1, 18)])
df["id"] = df["id"].apply(lambda x: x.replace("task_", "")).astype(int)


# automatische Konvertierung pandas <-> R
pandas2ri.activate()

nparLD = importr("nparLD")

# dat: DataFrame mit y, a, b, id
# a = Within-Faktor, b = Between-Faktor
fit = nparLD.nparLD(
    Formula("y ~ a * b"),
    data=dat,
    subject="id"
)

print(fit)