from datetime import datetime, timedelta
from pytz import timezone, utc
from tzlocal import get_localzone

def get_utc_time_from_time_usec(time_usec: int) -> datetime:
    return datetime.utcfromtimestamp(time_usec/(10**6))

def get_utc_time_elapsed_from_time_usec(time_usec: int) -> timedelta:
    return datetime.now() - get_utc_time_from_time_usec(time_usec)

def get_days_elapsed_from_time_usec(time_usec: int) -> float:
    time_elapsed = get_utc_time_elapsed_from_time_usec(time_usec)
    return time_elapsed.days + (time_elapsed.seconds / (24*3600)) + (time_elapsed.microseconds / (24*3600*10**6))

def get_years_elapsed_from_time_usec(time_usec: int) -> float:
    return get_days_elapsed_from_time_usec(time_usec) / 365

def utc2tz(utc_datetime: datetime, tz_str: str) -> datetime:
    """
    Example: utc2tz(utc_datetime, 'Asia/Tokyo')
    """
    return utc_datetime.replace(tzinfo=utc).astimezone(timezone(tz_str))

def utc2localzone(utc_datetime: datetime) -> datetime:
    localtz = get_localzone()
    return utc_datetime.replace(tzinfo=utc).astimezone(localtz)

def get_localtime_from_time_usec(time_usec: int) -> datetime:
    return utc2localzone(get_utc_time_from_time_usec(time_usec))