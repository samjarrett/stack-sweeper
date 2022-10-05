from stack_sweeper import cloudformation, exclude_names_strategy


def test_not_excluded(stack: cloudformation.Stack):
    """Tests ExcludeNamesStrategy.should_remove() true cases"""

    stack.name = "MyStack"

    # test no names excluded
    strategy = exclude_names_strategy.ExcludeNamesStrategy()
    assert strategy.should_remove(stack)

    # test other names excluded
    strategy = exclude_names_strategy.ExcludeNamesStrategy(exclude_names=["SomeStack"])
    assert strategy.should_remove(stack)

    stack.name = "AnotherStack"
    assert strategy.should_remove(stack)

    # test other name prefixes excluded
    strategy = exclude_names_strategy.ExcludeNamesStrategy(
        exclude_name_prefixes=["Prefix-One", "Prefix-Two"]
    )
    assert strategy.should_remove(stack)

    # prove it's not static
    stack.name = "AnotherStack"
    assert strategy.should_remove(stack)

    # prove it isn't using part of the prefix list
    stack.name = "Prefix-Three"
    assert strategy.should_remove(stack)
    stack.name = "Prefix"
    assert strategy.should_remove(stack)

    # Test it needs to be a prefix
    stack.name = "Mystack-Prefix-One"
    assert strategy.should_remove(stack)


def test_excluded(stack: cloudformation.Stack):
    """Tests ExcludeNamesStrategy.should_remove() true cases"""
    stack.name = "MyStack"

    # Test when the excluded name list is a single name
    strategy = exclude_names_strategy.ExcludeNamesStrategy(exclude_names=["MyStack"])
    assert not strategy.should_remove(stack)

    # Test multiple excluded names
    strategy = exclude_names_strategy.ExcludeNamesStrategy(
        exclude_names=["MyStack", "SecondStack"]
    )
    assert not strategy.should_remove(stack)

    # Test prefixes
    strategy = exclude_names_strategy.ExcludeNamesStrategy(exclude_name_prefixes=["My"])
    assert not strategy.should_remove(stack)

    strategy = exclude_names_strategy.ExcludeNamesStrategy(
        exclude_name_prefixes=["My", "Another"]
    )
    assert not strategy.should_remove(stack)

    stack.name = "AnotherStack"
    assert not strategy.should_remove(stack)


def test_str():
    """Tests ExcludeNamesStrategy string representation"""
    strategy = exclude_names_strategy.ExcludeNamesStrategy()
    assert (
        str(strategy)
        == "ExcludeNamesStrategy(exclude_names=None, exclude_name_prefixes=None)"
    )

    strategy = exclude_names_strategy.ExcludeNamesStrategy(
        exclude_names=["My", "Stack"]
    )
    assert (
        str(strategy)
        == "ExcludeNamesStrategy(exclude_names=[My, Stack], exclude_name_prefixes=None)"
    )

    strategy = exclude_names_strategy.ExcludeNamesStrategy(
        exclude_name_prefixes=["My", "Prefixes"]
    )
    assert (
        str(strategy)
        == "ExcludeNamesStrategy(exclude_names=None, exclude_name_prefixes=[My, Prefixes])"
    )

    strategy = exclude_names_strategy.ExcludeNamesStrategy(
        exclude_names=["My, Stack"], exclude_name_prefixes=["My", "Prefixes"]
    )
    assert (
        str(strategy)
        == "ExcludeNamesStrategy(exclude_names=[My, Stack], exclude_name_prefixes=[My, Prefixes])"
    )
