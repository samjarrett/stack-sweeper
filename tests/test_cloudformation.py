# pylint:disable=redefined-outer-name
from datetime import datetime
from typing import Dict, List, Optional, Union

import pytest  # type: ignore
from botocore.exceptions import ClientError  # type: ignore

from stack_sweeper import cloudformation

from . import stubs
from .conftest import STACK_ID, StubbedClient


def test_status(fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack):
    """Tests Stack.status"""
    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "UPDATE_COMPLETE"
    )
    assert stack.status == "UPDATE_COMPLETE"

    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "UPDATE_ROLLBACK_COMPLETE"
    )
    assert stack.status == "UPDATE_ROLLBACK_COMPLETE"


def test_termination_protection(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.termination_protection"""
    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "UPDATE_COMPLETE"
    )
    assert not stack.termination_protection

    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "UPDATE_ROLLBACK_COMPLETE", True
    )
    assert stack.termination_protection


def test_resources(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.resources"""
    stubs.stub_describe_stack_resources(
        fake_cloudformation_client.stub,
        STACK_ID,
        {"ResourceOne": "AWS::IAM::Role", "ResourceTwo": "AWS::EC2::LaunchTemplate"},
    )
    resources = stack.resources
    assert "ResourceOne" in resources
    assert resources["ResourceOne"]["ResourceType"] == "AWS::IAM::Role"
    assert "ResourceTwo" in resources
    assert resources["ResourceTwo"]["ResourceType"] == "AWS::EC2::LaunchTemplate"


def test_disable_termination_protection(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.disable_termination_protection()"""
    stubs.stub_update_termination_protection(
        fake_cloudformation_client.stub, STACK_ID, False
    )
    stack.disable_termination_protection()


def test_delete_success(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.delete() successful cases"""
    stubs.stub_delete_stack(fake_cloudformation_client.stub, STACK_ID)
    stack.delete(False)


def test_delete_failure(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.delete() failure cases"""
    stubs.stub_delete_stack_error(fake_cloudformation_client.stub, "Can not delete")
    with pytest.raises(ClientError):
        stack.delete(False)


def test_delete_wait_success(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack, sleepless
):  # pylint: disable=unused-argument
    """Tests Stack.delete(wait=True) successful cases"""
    stubs.stub_delete_stack(fake_cloudformation_client.stub, STACK_ID)
    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "DELETE_COMPLETE"
    )
    stubs.stub_describe_stack_events(fake_cloudformation_client.stub, STACK_ID)
    stack.delete(True)


def test_delete_wait_failure(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack, sleepless
):  # pylint: disable=unused-argument
    """Tests Stack.delete(wait=True) failure cases"""
    stubs.stub_delete_stack(fake_cloudformation_client.stub, STACK_ID)
    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "DELETE_IN_PROGRESS"
    )
    stubs.stub_describe_stack_events(fake_cloudformation_client.stub, STACK_ID)
    stubs.stub_describe_stack_events(fake_cloudformation_client.stub, STACK_ID)
    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "DELETE_FAILED"
    )
    with pytest.raises(Exception):
        stack.delete(True)


def test_wait_success(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack, sleepless
):  # pylint: disable=unused-argument
    """Tests Stack.wait() success cases"""
    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "DELETE_COMPLETE"
    )
    stubs.stub_describe_stack_events(fake_cloudformation_client.stub, STACK_ID)
    stack.wait()

    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "DELETE_IN_PROGRESS"
    )
    stubs.stub_describe_stack_events(fake_cloudformation_client.stub, STACK_ID)
    stubs.stub_describe_stack_events(fake_cloudformation_client.stub, STACK_ID)
    stubs.stub_describe_stack(
        fake_cloudformation_client.stub, STACK_ID, "DELETE_COMPLETE"
    )
    stack.wait()


def __generate_describe_stack_response(
    stack_name: str,
    tags: List[Dict[str, str]],
    parameters: List[Dict[str, str]],
    parent: Optional[str] = None,
) -> Dict[str, Union[str, datetime, List[Dict[str, str]]]]:
    """Generates a describe_stack response"""
    response: Dict[str, Union[str, datetime, List[Dict[str, str]]]] = {
        "StackName": stack_name,
        "StackId": f"arn:aws:cloudformation:ap-southeast-2:123456789012:stack/{stack_name}"
        "/bd6129c0-de8c-11e9-9c70-0ac26335768c",
        "StackStatus": "CREATE_COMPLETE",
        "CreationTime": datetime(2020, 1, 1),
        "LastUpdatedTime": datetime(2020, 1, 1),
        "Tags": tags,
        "Parameters": parameters,
    }

    if parent:
        parent_stack_id = (
            f"arn:aws:cloudformation:ap-southeast-2:123456789012:stack/{parent}"
        )
        response["ParentId"] = parent_stack_id
        response["RootId"] = parent_stack_id

    return response


def test_get_stacks(fake_cloudformation_client: StubbedClient):
    """Test cloudformation.get_stacks()"""
    stack_responses = [__generate_describe_stack_response("stack-one", [], [])]
    stubs.stub_describe_stacks(fake_cloudformation_client.stub, stack_responses)
    stacks = list(cloudformation.get_stacks(fake_cloudformation_client.client))
    assert len(stacks) == 1
    assert isinstance(stacks[0], cloudformation.Stack)
    assert not stacks[0].tags
    assert not stacks[0].parameters

    # Test tag sanity conversion
    stack_responses.append(
        __generate_describe_stack_response(
            "stack-two",
            [{"Key": "Something", "Value": "Else"}, {"Key": "MyTag", "Value": "Value"}],
            [],
        )
    )
    stubs.stub_describe_stacks(fake_cloudformation_client.stub, stack_responses)
    stacks = list(cloudformation.get_stacks(fake_cloudformation_client.client))
    assert len(stacks) == 2
    assert isinstance(stacks[1], cloudformation.Stack)
    assert stacks[1].name == "stack-two"
    assert stacks[1].tags == {"Something": "Else", "MyTag": "Value"}

    # Test parameter sanity conversion
    stack_responses.append(
        __generate_describe_stack_response(
            "stack-three",
            [
                {"Key": "Something", "Value": "Else"},
                {"Key": "MyTag", "Value": "Value"},
            ],
            [{"ParameterKey": "ParamOne", "ParameterValue": "Value"}],
        )
    )
    stubs.stub_describe_stacks(fake_cloudformation_client.stub, stack_responses)
    stacks = list(cloudformation.get_stacks(fake_cloudformation_client.client))
    assert len(stacks) == 3
    assert stacks[2].name == "stack-three"
    assert stacks[2].parameters == {"ParamOne": "Value"}


def test_get_stacks_exclude_nested_stacks(fake_cloudformation_client: StubbedClient):
    """Test cloudformation.get_stacks() exclude nested stacks"""
    stack_responses = [
        __generate_describe_stack_response("stack-one", [], []),
        __generate_describe_stack_response("stack-two", [], [], "stack-one"),
    ]
    stubs.stub_describe_stacks(fake_cloudformation_client.stub, stack_responses)
    stacks = list(cloudformation.get_stacks(fake_cloudformation_client.client))
    assert len(stacks) == 1
