from datetime import datetime, timezone


def get_current_timestamp() -> int:
    current_utc_datetime = datetime.now(timezone.utc)
    return current_utc_datetime
