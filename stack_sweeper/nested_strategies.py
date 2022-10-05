from typing import List

from .base_strategy import BaseStrategy
from .cloudformation import Stack


class BaseMultiNestedStrategy(BaseStrategy):
    """Base class for all multi-nested strategies"""

    nested_strategies: List[BaseStrategy]

    def __init__(self, nested_strategies: List[BaseStrategy]):
        self.nested_strategies = nested_strategies


class NestedAllStrategy(BaseMultiNestedStrategy):
    """A strategy that requires that all nested strategies concur before the stack is selected"""

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
        for strategy in self.nested_strategies:
            result = strategy.should_remove(stack)
            if not result:
                return False

        return True


class NestedAnyStrategy(BaseMultiNestedStrategy):
    """A strategy that requires that a single nested strategy concurs before the stack is selected"""

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
        for strategy in self.nested_strategies:
            result = strategy.should_remove(stack)
            if result:
                return True

        return False
