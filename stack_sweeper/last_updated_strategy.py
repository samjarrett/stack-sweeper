from datetime import datetime, timedelta
from typing import Optional

from dateutil.tz import tzutc

from .base_strategy import BaseStrategy
from .cloudformation import Stack


class LastUpdatedStrategy(BaseStrategy):
    """A strategy that uses the last updated date of the stack to determine if it should be removed"""

    allowed_delta: timedelta
    compare_time: datetime

    def __init__(
        self, allowed_delta: timedelta, compare_time: Optional[datetime] = None
    ):
        if not compare_time:
            compare_time = datetime.now(tz=tzutc())

        self.allowed_delta = allowed_delta
        self.compare_time = compare_time

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
        expiry = stack.last_updated_at + self.allowed_delta

        result = expiry <= self.compare_time

        if result:
            stack.mark(self)

        return result

    def __str__(self):
        allowed_delta = str(self.allowed_delta).replace(", 0:00:00", "")
        return f"LastUpdatedStrategy({allowed_delta})"

    def get_mark_reason(self, stack: Stack) -> str:
        """Get a reason why the stack was marked"""
        last_updated_at = stack.last_updated_at
        age = self.compare_time - last_updated_at
        allowed_delta = str(self.allowed_delta).replace(", 0:00:00", "")

        return (
            f"last updated {age.days} days ago "
            f"(threshold: {allowed_delta}, last updated: {last_updated_at.strftime('%Y-%m-%d')})"
        )
