from typing import List, Optional

from .base_strategy import BaseStrategy
from .cloudformation import Stack


class ExcludeNamesStrategy(BaseStrategy):
    """A strategy that uses the stack's name to determine if the stack should be removed"""

    exclude_names: Optional[List[str]]
    exclude_name_prefixes: Optional[List[str]]

    def __init__(
        self,
        exclude_names: Optional[List[str]] = None,
        exclude_name_prefixes: Optional[List[str]] = None,
    ):
        self.exclude_names = exclude_names
        self.exclude_name_prefixes = exclude_name_prefixes

    def should_remove(self, stack: Stack) -> bool:
        """Should this stack be removed?"""
        if self.exclude_names and stack.name in self.exclude_names:
            return False

        if self.exclude_name_prefixes:
            for name_prefix in self.exclude_name_prefixes:
                if stack.name.startswith(name_prefix):
                    return False

        return True

    def __str__(self):
        list_to_str = lambda a_list: f"[{', '.join(a_list)}]" if a_list else "None"

        exclude_names = list_to_str(self.exclude_names)
        exclude_name_prefixes = list_to_str(self.exclude_name_prefixes)
        return f"ExcludeNamesStrategy(exclude_names={exclude_names}, exclude_name_prefixes={exclude_name_prefixes})"
