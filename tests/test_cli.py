# pylint:disable=redefined-outer-name
from argparse import Namespace
from datetime import timedelta

import pytest

from stack_sweeper import cli


@pytest.fixture
def base_namespace() -> Namespace:
    """A pytest fixture that provides an empty Namespace object"""
    return Namespace(
        expiry_tag=None,
        stack_update_age=None,
        exclude_tag=[],
        exclude_stacks=[],
        exclude_stack_prefixes=[],
        limit=None,
    )


def test_parse_args():
    """Tests parse_args()"""
    args = [
        "--expiry-tag",
        "expiry",
        "--exclude-tag",
        "exclude",
        "--exclude-stacks",
        "one",
        "two",
        "--exclude-stack-prefixes",
        "p1",
        "p2",
        "--stack-update-age",
        "90",
    ]
    namespace = cli.parse_args(args)
    assert namespace.expiry_tag == "expiry"
    assert namespace.exclude_tag == "exclude"
    assert namespace.exclude_stacks == ["one", "two"]
    assert namespace.exclude_stack_prefixes == ["p1", "p2"]
    assert namespace.stack_update_age == 90
    assert namespace.log_level == "INFO"
    assert not namespace.delete
    assert namespace.wait

    args = [
        "--expiry-tag",
        "myexpiry",
        "--exclude-tag",
        "myexclude",
        "--exclude-stacks",
        "exone",
        "extwo",
        "--exclude-stack-prefixes",
        "myp1",
        "myp2",
        "--stack-update-age",
        "7",
        "--delete",
        "--no-wait",
        "--log-level",
        "DEBUG",
    ]
    namespace = cli.parse_args(args)
    assert namespace.expiry_tag == "myexpiry"
    assert namespace.exclude_tag == "myexclude"
    assert namespace.exclude_stacks == ["exone", "extwo"]
    assert namespace.exclude_stack_prefixes == ["myp1", "myp2"]
    assert namespace.stack_update_age == 7
    assert namespace.log_level == "DEBUG"
    assert namespace.delete
    assert not namespace.wait


def test_parse_args_required_params():
    """Tests parse_args() required params"""
    # No args will trigger needing --expiry-tag / --stack-update-age
    args = []
    with pytest.raises(SystemExit):
        cli.parse_args(args)

    # --no-wait without --delete will exit too
    args = ["--expiry-tag", "myexpiry", "--no-wait"]
    with pytest.raises(SystemExit):
        cli.parse_args(args)


def test_get_strategy_from_args_empty(base_namespace: Namespace):
    """Tests get_strategy_from_args() on an empty args"""
    # Test an empty one is basically empty
    strategy = cli.get_strategy_from_args(base_namespace)
    assert isinstance(strategy, cli.NestedAllStrategy)
    assert len(strategy.nested_strategies) == 1
    assert isinstance(strategy.nested_strategies[0], cli.NestedAnyStrategy)
    assert not strategy.nested_strategies[0].nested_strategies


def test_get_strategy_from_args_expiry_tag(base_namespace: Namespace):
    """Tests get_strategy_from_args() with an expiry tag"""
    base_namespace.expiry_tag = "expiry"
    strategy = cli.get_strategy_from_args(base_namespace)
    assert len(strategy.nested_strategies[0].nested_strategies) == 1
    assert isinstance(
        strategy.nested_strategies[0].nested_strategies[0], cli.ExpirationTagStrategy
    )
    assert strategy.nested_strategies[0].nested_strategies[0].tag_name == "expiry"


def test_get_strategy_from_args_stack_update_age(base_namespace: Namespace):
    """Tests get_strategy_from_args() with a stack update age"""
    base_namespace.stack_update_age = 90
    strategy = cli.get_strategy_from_args(base_namespace)
    assert len(strategy.nested_strategies[0].nested_strategies) == 1
    assert isinstance(
        strategy.nested_strategies[0].nested_strategies[0], cli.LastUpdatedStrategy
    )
    assert strategy.nested_strategies[0].nested_strategies[
        0
    ].allowed_delta == timedelta(days=90)


def test_get_strategy_from_args_exclude_tag(base_namespace: Namespace):
    """Tests get_strategy_from_args() with an exclude tag"""
    base_namespace.exclude_tag = "exclude"
    strategy = cli.get_strategy_from_args(base_namespace)
    assert isinstance(strategy.nested_strategies[1], cli.ExcludeTagStrategy)
    assert strategy.nested_strategies[1].tag_name == "exclude"


def test_get_strategy_from_args_exclude_stack_name(base_namespace: Namespace):
    """Tests get_strategy_from_args() with an exclude stack names"""
    base_namespace.exclude_stacks = ["stack-one", "stack-two"]
    base_namespace.exclude_stack_prefixes = ["prefixone", "prefixtwo"]
    strategy = cli.get_strategy_from_args(base_namespace)
    assert isinstance(strategy.nested_strategies[1], cli.ExcludeNamesStrategy)
    assert strategy.nested_strategies[1].exclude_names == ["stack-one", "stack-two"]
    assert strategy.nested_strategies[1].exclude_name_prefixes == [
        "prefixone",
        "prefixtwo",
    ]


def test_get_strategy_from_args_limit(base_namespace: Namespace):
    """Tests get_strategy_from_args() with a limit set"""
    base_namespace.limit = 10
    strategy = cli.get_strategy_from_args(base_namespace)
    assert isinstance(strategy, cli.LimitedStrategy)
    assert strategy.limit == 10
    assert isinstance(strategy.nested_strategy, cli.NestedAllStrategy)
