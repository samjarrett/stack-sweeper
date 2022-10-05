from .base_strategy import BaseStrategy
from .cloudformation import Stack


class ExcludeTagStrategy(BaseStrategy):
    """A strategy that uses an exclusion tag's presence to determine if the stack should be removed"""

    tag_name: str

    def __init__(self, tag_name: str):
        self.tag_name = tag_name

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
        return self.tag_name not in stack.tags
