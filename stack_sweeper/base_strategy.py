from .cloudformation import Stack


class BaseStrategy:
    """The base strategy class"""

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""

    def get_mark_reason(self, stack: Stack) -> str:
        """Get a reason why the stack was marked"""
