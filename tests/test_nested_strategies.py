from stack_sweeper import cloudformation, nested_strategies

from .conftest import AlwaysFalseStrategy, AlwaysTrueStrategy


def test_nested_all_strategy(stack: cloudformation.Stack):
    """Tests NestedAllStrategy.should_remove() cases"""
    # Test a single strategy
    strategy = nested_strategies.NestedAllStrategy([AlwaysTrueStrategy()])
    assert strategy.should_remove(stack)

    strategy = nested_strategies.NestedAllStrategy([AlwaysFalseStrategy()])
    assert not strategy.should_remove(stack)

    # Test multi-strategies
    strategy = nested_strategies.NestedAllStrategy(
        [AlwaysTrueStrategy(), AlwaysFalseStrategy()]
    )
    assert not strategy.should_remove(stack)


def test_nested_any_strategy(stack: cloudformation.Stack):
    """Tests NestedAnyStrategy.should_remove() false cases"""
    # Test a single strategy
    strategy = nested_strategies.NestedAnyStrategy([AlwaysTrueStrategy()])
    assert strategy.should_remove(stack)

    strategy = nested_strategies.NestedAnyStrategy([AlwaysFalseStrategy()])
    assert not strategy.should_remove(stack)

    # Test multi-strategies with one True
    strategy = nested_strategies.NestedAnyStrategy(
        [AlwaysTrueStrategy(), AlwaysFalseStrategy()]
    )
    assert strategy.should_remove(stack)

    # Test multi-strategies with only False
    strategy = nested_strategies.NestedAnyStrategy(
        [AlwaysFalseStrategy(), AlwaysFalseStrategy()]
    )
    assert not strategy.should_remove(stack)


def test_str():
    """Tests LimitedStrategy string representation"""
    strategy = nested_strategies.NestedAllStrategy([AlwaysTrueStrategy()])
    assert str(strategy) == "NestedAllStrategy(nested_strategies=[AlwaysTrueStrategy])"

    strategy = nested_strategies.NestedAllStrategy(
        [AlwaysTrueStrategy(), AlwaysFalseStrategy()]
    )
    assert (
        str(strategy)
        == "NestedAllStrategy(nested_strategies=[AlwaysTrueStrategy, AlwaysFalseStrategy])"
    )

    strategy = nested_strategies.NestedAnyStrategy([AlwaysTrueStrategy()])
    assert str(strategy) == "NestedAnyStrategy(nested_strategies=[AlwaysTrueStrategy])"

    strategy = nested_strategies.NestedAnyStrategy(
        [AlwaysTrueStrategy(), AlwaysFalseStrategy()]
    )
    assert (
        str(strategy)
        == "NestedAnyStrategy(nested_strategies=[AlwaysTrueStrategy, AlwaysFalseStrategy])"
    )
