from datetime import date, datetime, time
from typing import Optional

# 'Thu, 02 Jun 2022 03:48:05 GMT'

DATE_FORMATS = (
    "%Y-%m-%d",  # 2017-01-25
    "%m-%d-%Y",  # 01-25-2017
    "%Y/%m/%d",  # 2017/01/25
    "%m/%d/%Y",  # 01/25/2017
    "%m.%d.%Y",  # 01.25.2017
    "%m-%d-%y",  # 01-25-17
    "%B %d, %Y",  # January 25, 2017
    "%b %d, %Y",  # January 25, 2017
    "%a, %d %b %Y",  # Mon, 25 January 2017
    "%A, %d %b %Y",  # Monday, 25 January 2017
)

TIME_FORMATS = (
    "%H:%M:%S",  # 03:48:05
    "%H:%M",  # 03:48
    "%I:%M:%S %p",  # 03:48:05 PM
    "%I:%M:%S %z",  # 03:48:05 -0700
    "%I:%M:%S %Z",  # 03:48:05 PDT
    "%H:%M:%S %Z",  # 03:48:05 PDT
    "%I:%M %p",  # 03:48 PM
    "%I:%M %z",  # 03:48 -0700
    "%I:%M",  # 03:48
)
DATE_TIME_SEPS = (" ", "T")


def decode_datetime(s: str) -> Optional[datetime]:
    for df in DATE_FORMATS:
        for tf in TIME_FORMATS:
            for sep in DATE_TIME_SEPS:
                f = "{0}{1}{2}".format(df, sep, tf)
                try:
                    return datetime.strptime(s, f)
                except ValueError:
                    pass
    return None


def decode_date(s: str) -> Optional[date]:
    for f in DATE_FORMATS:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            pass
    return None


def decode_time(s: str) -> Optional[time]:
    for f in TIME_FORMATS:
        try:
            return datetime.strptime(s, f).time()
        except ValueError:
            pass
    return None
