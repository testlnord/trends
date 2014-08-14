"""Unrelated util stuff """
import datetime


def get_threshold_date(time, from_date=None) -> datetime.datetime:
    """ Calculates threshold date
    Calculates based on refresh_time value in sources` settings.
    :param time: refresh time. Valid values: "day", "week", "month"
    :param from_date: date to count from. If from_date is None then it gets current time value.
    """
    assert time in ['month', 'week', 'day'], "Wrong time value"
    if from_date is None:
        from_date = datetime.datetime.now().date()
    if time == 'month':
        month = from_date.month - 1
        if month == 0:
            return datetime.datetime(from_date.year - 1, 1, from_date.day)
        else:
            return datetime.datetime(from_date.year, month, from_date.day)
    else:
        days = 7
        if time == 'day':
            days = 1
        return from_date - datetime.timedelta(days=days)
