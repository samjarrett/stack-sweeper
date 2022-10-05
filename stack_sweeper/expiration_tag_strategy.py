from datetime import datetime
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

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
        if self.tag_name not in stack.tags:
            return False

        try:
            expiry = parser.parse(stack.tags[self.tag_name])
            if not expiry.tzinfo:  # force it to have a timezone of UTC if none is set
                expiry = expiry.replace(tzinfo=tzutc())
        except ParserError:
            return False

        result = expiry <= self.compare_time

        if result:
            stack.mark(self)

        return result

    def __str__(self):
        return f"ExpirationTagStrategy({self.tag_name})"
