import calendar
import datetime


def add_months(source_date, months):
    """
    Adds a specified number of months to a given date using only
    native Python standard libraries (datetime and calendar).
    """
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    # Find the last day of the target month
    last_day_of_month = calendar.monthrange(year, month)[1]
    # Use the minimum of the original day or the target month's last day
    day = min(source_date.day, last_day_of_month)

    # If the original object was a datetime, return a datetime object
    if isinstance(source_date, datetime.datetime):
        return source_date.replace(year=year, month=month, day=day)
    # Otherwise, return a date object
    return datetime.date(year, month, day)
