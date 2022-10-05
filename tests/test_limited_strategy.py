from stack_sweeper import cloudformation, limited_strategy

from .conftest import AlternatingTrueStrategy, AlwaysTrueStrategy


def test_limited_strategy(stack: cloudformation.Stack):
    """Tests LimitedStrategy.should_remove() cases"""
    strategy = limited_strategy.LimitedStrategy(5, AlwaysTrueStrategy())

    # First five should be removed
    for _ in range(5):
        assert strategy.should_remove(stack)

    # All subsequent ones should not be removed
    for _ in range(5):
        assert not strategy.should_remove(stack)

    # Test an alternating strategy, so we know that we're only counting positive removals
    strategy = limited_strategy.LimitedStrategy(5, AlternatingTrueStrategy())

    # Five out of ten should be removed
    for index in range(10):
        expected_success = index % 2 == 0
        assert strategy.should_remove(stack) == expected_success

    # All subsequent ones should not be removed
    for _ in range(5):
        assert not strategy.should_remove(stack)


def test_str():
    """Tests LimitedStrategy string representation"""
    strategy = limited_strategy.LimitedStrategy(1, AlwaysTrueStrategy())
    assert str(strategy) == "LimitedStrategy(1, nested_strategy=AlwaysTrueStrategy)"

    strategy = limited_strategy.LimitedStrategy(30, AlwaysTrueStrategy())
    assert str(strategy) == "LimitedStrategy(30, nested_strategy=AlwaysTrueStrategy)"
