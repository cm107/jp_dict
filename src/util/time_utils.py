from datetime import datetime, timedelta, timezone

def get_utc_time_from_time_usec(time_usec: int) -> datetime:
    return datetime.utcfromtimestamp(time_usec/(10**6))

def get_utc_time_elapsed_from_time_usec(time_usec: int) -> timedelta:
    return datetime.now() - get_utc_time_from_time_usec(time_usec)

def get_days_elapsed_from_time_usec(time_usec: int) -> float:
    time_elapsed = get_utc_time_elapsed_from_time_usec(time_usec)
    return time_elapsed.days + (time_elapsed.seconds / (24*3600)) + (time_elapsed.microseconds / (24*3600*10**6))

def get_years_elapsed_from_time_usec(time_usec: int) -> float:
    return get_days_elapsed_from_time_usec(time_usec) / 365