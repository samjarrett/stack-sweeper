from .base_strategy import BaseStrategy
from .cloudformation import Stack


class LimitedStrategy(BaseStrategy):
    """A strategy that limits how many operations will be performed"""

    limit: int
    nested_strategy: BaseStrategy
    processed: int = 0

    def __init__(self, limit: int, nested_strategy: BaseStrategy):
        self.limit = limit
        self.nested_strategy = nested_strategy

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
        if self.processed >= self.limit:
            return False

        result = self.nested_strategy.should_remove(stack)

        if result:
            self.processed += 1

        return result
