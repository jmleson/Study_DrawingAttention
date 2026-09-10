from datetime import timedelta



def time_to_seconds(t):
    if t is None:
        return None

    return (
        t.hour * 3600
        + t.minute * 60
        + t.second
        + t.microsecond / 1_000_000
    )


def parse_mm_ss_hundredths(value: str) -> timedelta:
    """
    Parse MM:SS:CC, where CC represents hundredths of a second.

    Example:
        "05:30:25" -> 5 minutes, 30.25 seconds
    """
    minutes, seconds, hundredths = map(int, value.split(":"))

    return timedelta(
        minutes=minutes,
        seconds=seconds,
        milliseconds=hundredths * 10,
    )