import os
from collections import namedtuple
import time
from datetime import datetime

import pytest  # type: ignore
import boto3  # type: ignore
from botocore.stub import Stubber  # type: ignore

from stack_sweeper import cloudformation

# prevent boto from looking for IAM creds via metadata while running tests
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

STACK_NAME = "MyStack"
STACK_ID = (
    f"arn:aws:cloudformation:ap-southeast-2:123456789012:stack/{STACK_NAME}"
    "/bd6129c0-de8c-11e9-9c70-0ac26335768c"
)


StubbedClient = namedtuple("StubbedClient", ["stub", "client"])


@pytest.yield_fixture
def fake_cloudformation_client() -> StubbedClient:
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
