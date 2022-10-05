from typing import List, Dict
from datetime import datetime
import uuid

from botocore.stub import ANY


def stub_get_parameter_value(
    stubber, name: str, value: str, version: int = 1, param_type: str = "String",
):
    """Stubs SSM get_parameter_value responses"""
    response = {
        "Parameter": {
            "Name": name,
            "Type": param_type,
            "Value": value,
            "Version": version,
            "LastModifiedDate": datetime(2020, 1, 1),
            "ARN": f"arn:aws:ssm:ap-southeast-2:305295870059:parameter/{name.strip('/')}",
        }
    }
    stubber.add_response(
        "get_parameter",
        response,
        expected_params={"Name": name, "WithDecryption": True},
    )


def stub_get_parameter_unset(stubber, name: str):
    """Stubs SSM get_parameter_value responses where the parameter is unset"""
    stubber.add_client_error(
        "get_parameter",
        "ParameterNotFound",
        "Parameter was not found",
        400,
        expected_params={"Name": name, "WithDecryption": True},
    )


def stub_put_parameter_value(
    stubber, name: str, description: str, value: str, version: int = 1
):
    """Stubs SSM put_parameter_value responses"""
    response = {
        "Version": version,
    }
    stubber.add_response(
        "put_parameter",
        response,
        expected_params={
            "Name": name,
            "Description": description,
            "Value": value,
            "Type": "SecureString",
            "Overwrite": True,
        },
    )


def stub_add_tags_to_resource(stubber, name: str, tags: List[Dict]):
    """Stubs SSM add_tags_to_resource responses"""
    stubber.add_response(
        "add_tags_to_resource",
        {},
        expected_params={
            "ResourceType": "Parameter",
            "ResourceId": name,
            "Tags": tags,
        },
    )


def stub_describe_stack(stubber, stack_name: str, status: str):
    """Stubs CloudFormation describe_stacks responses for a specific stack"""
    response = {
        "Stacks": [
            {
                "StackName": stack_name,
                "StackStatus": status,
                "CreationTime": datetime(2020, 1, 1),
            }
        ]
    }
    stubber.add_response(
        "describe_stacks", response, expected_params={"StackName": stack_name},
    )


def stub_describe_stacks(stubber, stacks: List):
    """Stubs CloudFormation describe_stacks responses"""
    response = {"Stacks": stacks}
    stubber.add_response("describe_stacks", response, expected_params={})


def stub_delete_stack(stubber, stack_name: str):
    """Stubs CloudFormation delete_stack responses"""
    stubber.add_response(
        "delete_stack", {}, expected_params={"StackName": stack_name},
    )


def stub_delete_stack_error(stubber, error_message: str):
    """Stubs CloudFormation delete_stack responses when an error occurs"""
    stubber.add_client_error(
        "delete_stack",
        "ClientError",
        error_message,
        400,
        expected_params={"StackName": ANY},
    )


def stub_describe_stack_events(stubber, stack_id: str):
    """Stubs CloudFormation describe_stack_events responses"""
    stack_name = stack_id.split("/")[1]

    response = {
        "StackEvents": [
            {
                "StackId": stack_id,
                "EventId": str(uuid.uuid4()),
                "StackName": stack_name,
                "LogicalResourceId": "Something",
                "Timestamp": datetime(2020, 1, 1),
                "ResourceStatus": "CREATE_IN_PROGRESS",
                "ResourceStatusReason": "Resource creation initiated",
            },
            {
                "StackId": stack_id,
                "EventId": str(uuid.uuid4()),
                "StackName": stack_name,
                "LogicalResourceId": "Something",
                "Timestamp": datetime(2020, 1, 1),
                "ResourceStatus": "CREATE_COMPLETE",
            },
        ]
    }
    stubber.add_response(
        "describe_stack_events", response, expected_params={"StackName": stack_id},
    )


def stub_describe_stack_resources(stubber, stack_id: str, resources=Dict[str, str]):
    """Stubs CloudFormation describe_stack_resources responses"""
    stack_name = stack_id.split("/")[1]

    response = {
        "StackResources": [
            {
                "StackId": stack_id,
                "StackName": stack_name,
                "LogicalResourceId": logical_resource_id,
                "PhysicalResourceId": f"{logical_resource_id}-PHYSICAL-1234",
                "ResourceType": resource_type,
                "Timestamp": datetime(2020, 1, 1),
                "ResourceStatus": "UPDATE_COMPLETE",
                "DriftInformation": {"StackResourceDriftStatus": "NOT_CHECKED"},
            }
            for logical_resource_id, resource_type in resources.items()
        ]
    }
    stubber.add_response(
        "describe_stack_resources", response, expected_params={"StackName": stack_id},
    )
