from datetime import datetime, date
from django.utils import timezone


class DateTimeProvider:
    tz = timezone.get_current_timezone()

    @classmethod
    def with_timezone(cls, when: datetime) -> datetime:
        return timezone.make_aware(when, cls.tz)

    @classmethod
    def now(cls) -> datetime:
        return cls.with_timezone(datetime.now())

    @classmethod
    def today(cls) -> date:
        return cls.with_timezone(date.today()).date()
