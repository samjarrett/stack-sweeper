import os
import time
from collections import namedtuple
from datetime import datetime
from itertools import cycle

import boto3  # type: ignore
import pytest  # type: ignore
from botocore.stub import Stubber  # type: ignore

from stack_sweeper import base_strategy, cloudformation

# prevent boto from looking for IAM creds via metadata while running tests
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

STACK_NAME = "MyStack"
STACK_ID = (
    f"arn:aws:cloudformation:ap-southeast-2:123456789012:stack/{STACK_NAME}"
    "/bd6129c0-de8c-11e9-9c70-0ac26335768c"
)


StubbedClient = namedtuple("StubbedClient", ["stub", "client"])


class AlwaysTrueStrategy(base_strategy.BaseStrategy):
    """An always-true strategy. Because some people want to watch the world burn"""

    # pylint: disable=redefined-outer-name
    def should_remove(self, stack: cloudformation.Stack) -> bool:
        """The stack should always be removed"""
        return True

    def __str__(self):
        return "AlwaysTrueStrategy"


class AlwaysFalseStrategy(base_strategy.BaseStrategy):
    """An always-false strategy. Chaotic evil"""

    # pylint: disable=redefined-outer-name
    def should_remove(self, stack: cloudformation.Stack) -> bool:
        """The stack should never be removed"""
        return False

    def __str__(self):
        return "AlwaysFalseStrategy"


class AlternatingTrueStrategy(base_strategy.BaseStrategy):
    """A flip-flopping strategy"""

    def __init__(self):
        self.iterator = cycle([True, False])

    # pylint: disable=redefined-outer-name
    def should_remove(self, stack: cloudformation.Stack) -> bool:
        """The stack should always be removed"""
        return next(self.iterator)


@pytest.fixture
def fake_cloudformation_client() -> StubbedClient:  # type: ignore
    """Creates a stubbed boto3 CloudFormation client"""
    cloudformation_client = boto3.client("cloudformation")
    with Stubber(cloudformation_client) as stubbed_client:
        yield StubbedClient(stubbed_client, cloudformation_client)
        stubbed_client.assert_no_pending_responses()


@pytest.fixture
def sleepless(monkeypatch):
    """Monkeypatches time.sleep to not sleep"""

    def sleep(seconds):  # pylint: disable=unused-argument
        """Fake sleep implementation - does nothing"""

    monkeypatch.setattr(time, "sleep", sleep)


@pytest.fixture
def stack(
    fake_cloudformation_client: StubbedClient,  # pylint: disable=redefined-outer-name
) -> cloudformation.Stack:
    """Create a Stack object"""

    return cloudformation.Stack(
        cloudformation=fake_cloudformation_client.client,
        stack_id=STACK_ID,
        name=STACK_NAME,
        parameters={"Hello": "You"},
        tags={"MyTag": "TagValue"},
        created_at=datetime(2020, 1, 1),
        last_updated_at=datetime(2020, 1, 1),
    )
