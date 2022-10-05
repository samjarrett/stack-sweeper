from datetime import datetime, timedelta
from dateutil.tz import tzutc


from stack_sweeper import expiration_tag_strategy, cloudformation


def test_expiration_not_valid(stack: cloudformation.Stack):
    """Tests ExpirationTagStrategy.should_remove() false cases"""
    strategy = expiration_tag_strategy.ExpirationTagStrategy(
        "expiration", datetime(2020, 1, 1, 9, 0, 0, tzinfo=tzutc())
    )

    # Test when the stack doesn't have the tag
    assert not strategy.should_remove(stack)

    # Test when the tag is a future datetime
    stack.tags["expiration"] = "2020-01-01 10:00:00Z"
    assert not strategy.should_remove(stack)

    # Test when the tag isn't a parsable datetime (fail safe - don't delete)
    stack.tags["expiration"] = "2020-01sadasda-01 10:00:00Z"
    assert not strategy.should_remove(stack)


def test_expiration_valid(stack: cloudformation.Stack):
    """Tests ExpirationTagStrategy.should_remove() false cases"""
    strategy = expiration_tag_strategy.ExpirationTagStrategy(
        "expiration", datetime(2020, 1, 1, 9, 0, 0, tzinfo=tzutc())
    )

    # Test when the time is exactly the expiry time
    stack.tags["expiration"] = "2020-01-01 09:00:00Z"
    assert strategy.should_remove(stack)

    # Test when the tag is a time in the past
    stack.tags["expiration"] = "2020-01-01 08:59:00Z"
    assert strategy.should_remove(stack)


def test_expiration_dynamic(stack: cloudformation.Stack):
    """Tests ExpirationTagStrategy.should_remove() dynamic expiry cases"""
    strategy = expiration_tag_strategy.ExpirationTagStrategy("expiration")

    # time in the future should not be removed
    future_time = datetime.now(tz=tzutc()) + timedelta(days=1)
    stack.tags["expiration"] = future_time.isoformat(timespec="seconds")
    assert not strategy.should_remove(stack)

    # time in the past should be removed
    past_time = datetime.now(tz=tzutc()) - timedelta(minutes=2)
    stack.tags["expiration"] = past_time.isoformat(timespec="seconds")
    assert strategy.should_remove(stack)


def test_expiration_no_timezone(stack: cloudformation.Stack):
    """Tests ExpirationTagStrategy.should_remove() expiry cases without a timezone"""
    strategy = expiration_tag_strategy.ExpirationTagStrategy("expiration")

    # time in the future should not be removed
    future_time = datetime.utcnow() + timedelta(days=1)
    stack.tags["expiration"] = future_time.isoformat(timespec="seconds")
    assert not strategy.should_remove(stack)

    # time in the past should be removed
    past_time = datetime.utcnow() - timedelta(minutes=2)
    stack.tags["expiration"] = past_time.isoformat(timespec="seconds")
    assert strategy.should_remove(stack)


def test_str():
    """Tests ExpirationTagStrategy string representation"""
    strategy = expiration_tag_strategy.ExpirationTagStrategy("expiry")
    assert str(strategy) == "ExpirationTagStrategy(expiry)"

    strategy = expiration_tag_strategy.ExpirationTagStrategy("stack-sweeper:expire")
    assert str(strategy) == "ExpirationTagStrategy(stack-sweeper:expire)"


def test_get_mark_reason(stack: cloudformation.Stack):
    """Tests ExpirationTagStrategy.get_mark_reason()"""
    strategy = expiration_tag_strategy.ExpirationTagStrategy(
        "expiration", datetime(2020, 1, 9, 9, 0, 0, tzinfo=tzutc())
    )

    past_time = datetime(2020, 1, 7, 9, 0, 0, tzinfo=tzutc())
    stack.tags["expiration"] = past_time.isoformat(timespec="seconds")
    assert "expired 2 days ago" in strategy.get_mark_reason(stack)
