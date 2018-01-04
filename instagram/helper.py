import calendar
from datetime import datetime
import pytz


def timestamp_to_datetime(ts):
    naive = datetime.utcfromtimestamp(float(ts))
    return naive.replace(tzinfo=pytz.UTC)


def datetime_to_timestamp(dt):
    return calendar.timegm(dt.timetuple())
