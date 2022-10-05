from stack_sweeper import exclude_tag_strategy, cloudformation


def test_not_excluded(stack: cloudformation.Stack):
    """Tests ExcludeTagStrategy.should_remove() false cases"""
    strategy = exclude_tag_strategy.ExcludeTagStrategy("stack-sweep:ignore")

    # Test when the stack doesn't have any tags
    stack.tags = dict()
    assert strategy.should_remove(stack)

    # test when the stack has other tags
    stack.tags["stack-sweep:something"] = "yes"
    assert strategy.should_remove(stack)


def test_excluded(stack: cloudformation.Stack):
    """Tests ExcludeTagStrategy.should_remove() false cases"""
    strategy = exclude_tag_strategy.ExcludeTagStrategy("stack-sweep:ignore")

    # Test when the tag is present with no value
    stack.tags["stack-sweep:ignore"] = ""
    assert not strategy.should_remove(stack)

    # Test when other tags are present too
    stack.tags["stack-sweep:something"] = "yes"
    assert len(stack.tags) > 1
    assert not strategy.should_remove(stack)

    # Test when the tag is present and has any value
    stack.tags["stack-sweep:ignore"] = "asdfghjkl"
    assert not strategy.should_remove(stack)
    stack.tags["stack-sweep:ignore"] = "qwertyuiop"
    assert not strategy.should_remove(stack)


def test_str():
    """Tests ExcludeTagStrategy string representation"""
    strategy = exclude_tag_strategy.ExcludeTagStrategy("exclude")
    assert str(strategy) == "ExcludeTagStrategy(exclude)"

    strategy = exclude_tag_strategy.ExcludeTagStrategy("stack-sweeper:ignore")
    assert str(strategy) == "ExcludeTagStrategy(stack-sweeper:ignore)"
