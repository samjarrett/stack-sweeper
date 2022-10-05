from datetime import datetime, timedelta
from dateutil.tz import tzutc


from stack_sweeper import last_updated_strategy, cloudformation


def test_expiration_not_valid(stack: cloudformation.Stack):
    """Tests LastUpdatedStrategy.should_remove() false cases"""
    strategy = last_updated_strategy.LastUpdatedStrategy(
        timedelta(days=7), datetime(2020, 1, 7, 9, 0, 0, tzinfo=tzutc())
    )

    # test when the expiry is in the past but before the window
    stack.last_updated_at = datetime.today().replace(tzinfo=tzutc())
    assert not strategy.should_remove(stack)

    stack.last_updated_at = datetime(2020, 1, 1, 0, 0, 0, tzinfo=tzutc())
    assert not strategy.should_remove(stack)

    stack.last_updated_at = datetime(2020, 1, 1, 0, 0, 0, tzinfo=tzutc())
    assert not strategy.should_remove(stack)

    # Test when the tag is a future datetime
    stack.last_updated_at = datetime(2020, 1, 8, 0, 0, 0, tzinfo=tzutc())
    assert not strategy.should_remove(stack)


def test_expiration_valid(stack: cloudformation.Stack):
    """Tests LastUpdatedStrategy.should_remove() false cases"""
    strategy = last_updated_strategy.LastUpdatedStrategy(
        timedelta(days=7), datetime(2020, 1, 8, 9, 0, 0, tzinfo=tzutc())
    )

    # Test when the time is exactly the expiry time
    stack.last_updated_at = datetime(2020, 1, 1, 9, 0, 0, tzinfo=tzutc())
    assert strategy.should_remove(stack)

    # Test when the tag is a time in the past
    stack.last_updated_at = datetime(2019, 12, 30, 0, 0, 0, tzinfo=tzutc())
    assert strategy.should_remove(stack)


def test_expiration_dynamic(stack: cloudformation.Stack):
    """Tests LastUpdatedStrategy.should_remove() dynamic expiry cases"""
    strategy = last_updated_strategy.LastUpdatedStrategy(timedelta(days=7))

    # time in the future should not be removed
    future_time = datetime.now(tz=tzutc()) + timedelta(days=1)
    stack.last_updated_at = future_time
    assert not strategy.should_remove(stack)

    # time in the past should be removed
    past_time = datetime.now(tz=tzutc()) - timedelta(days=7, hours=1)
    stack.last_updated_at = past_time
    assert strategy.should_remove(stack)


def test_str():
    """Tests LastUpdatedStrategy string representation"""
    strategy = last_updated_strategy.LastUpdatedStrategy(timedelta(days=7))
    assert str(strategy) == "LastUpdatedStrategy(7 days)"

    strategy = last_updated_strategy.LastUpdatedStrategy(timedelta(days=90))
    assert str(strategy) == "LastUpdatedStrategy(90 days)"

    # test that the other parts are only chopped off if they're 0
    strategy = last_updated_strategy.LastUpdatedStrategy(timedelta(days=90, hours=2))
    assert str(strategy) == "LastUpdatedStrategy(90 days, 2:00:00)"
