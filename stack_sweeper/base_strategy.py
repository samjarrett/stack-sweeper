from .cloudformation import Stack


class BaseStrategy:
    """The base strategy class"""

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
