import pandas as pd


def convert_to_numeric(series: pd.Series) -> pd.Series:
    """
    Convert values to numbers.

    Both decimal-point values (e.g. 2.5) and decimal-comma values
    (e.g. 2,5) are supported. Invalid or empty values become NaN.
    """
    return pd.to_numeric(
        series.astype("string").str.replace(",", ".", regex=False),
        errors="coerce",
    )
