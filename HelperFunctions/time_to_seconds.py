
def time_to_seconds(t):
    if t is None:
        return None

    return (
        t.hour * 3600
        + t.minute * 60
        + t.second
        + t.microsecond / 1_000_000
    )


