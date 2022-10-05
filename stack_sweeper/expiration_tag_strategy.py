from datetime import datetime, timedelta
from typing import Optional

from dateutil import parser
from dateutil.parser import ParserError  # type: ignore
from dateutil.tz import tzutc

from .base_strategy import BaseStrategy
from .cloudformation import Stack


class ExpirationTagStrategy(BaseStrategy):
    """A strategy that uses an expiry tag to determine if the stack should be removed"""

    tag_name: str
    compare_time: datetime

    def __init__(self, tag_name: str, compare_time: Optional[datetime] = None):
        if not compare_time:
            compare_time = datetime.now(tz=tzutc())

        self.tag_name = tag_name
        self.compare_time = compare_time

    def expiry(self, stack: Stack) -> datetime:
        """Provide a parsed, tz-aware expiry datetime object"""
        expiry = parser.parse(stack.tags[self.tag_name])
        if not expiry.tzinfo:  # force it to have a timezone of UTC if none is set
            expiry = expiry.replace(tzinfo=tzutc())

        return expiry

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
        if self.tag_name not in stack.tags:
            return False

        try:
            result = self.expiry(stack) <= self.compare_time
        except ParserError:
            return False

        if result:
            stack.mark(self)

        return result

    def __str__(self):
        return f"ExpirationTagStrategy({self.tag_name})"

    def get_mark_reason(self, stack: Stack) -> str:
        """Get a reason why the stack was marked"""
        expiry = self.expiry(stack)
        age: timedelta = self.compare_time - expiry

        return f"expired {age.days} days ago (expiry: {expiry.isoformat(timespec='seconds')})"
