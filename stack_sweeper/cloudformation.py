import time
from datetime import datetime
from typing import Any, Dict, Iterator, Optional, List

from .log_utils import log
from .paginator import paginate

IN_PROGRESS_STACK_STATUSES = [
    "DELETE_IN_PROGRESS",
]

SUCCESSFUL_STACK_STATUSES = [
    "CREATE_COMPLETE",
    "UPDATE_COMPLETE",
    "IMPORT_COMPLETE",
    "DELETE_COMPLETE",
]


def log_event(
    logical_resource_id: str, resource_status: str, status_reason: Optional[str] = None
):
    """Formats and logs a CloudFormation stack event"""
    if status_reason:
        return log(f"{logical_resource_id} - {resource_status} - {status_reason}")

    return log(f"{logical_resource_id} - {resource_status}")


class Stack:
    """Class that holds information about a CloudFormation stack, and can perform update to it"""

    stack_id: str
    name: str
    parameters: Dict[str, str]
    tags: Dict[str, str]
    created_at: datetime
    last_updated_at: datetime
    marked_by_strategies: List
    cloudformation: Any

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)

        self.marked_by_strategies = []

    @classmethod
    def factory_from_stack_detail(cls, cloudformation, stack_detail: Dict[str, Any]):
        """Create a Stack object from the describe_stacks output"""
        tags = {tag["Key"]: tag["Value"] for tag in stack_detail.get("Tags", [])}
        parameters = {
            parameter["ParameterKey"]: parameter["ParameterValue"]
            for parameter in stack_detail.get("Parameters", [])
        }

        return cls(
            stack_id=stack_detail["StackId"],
            name=stack_detail["StackName"],
            parameters=parameters,
            tags=tags,
            created_at=stack_detail["CreationTime"],
            last_updated_at=stack_detail.get(
                "LastUpdatedTime", stack_detail["CreationTime"]
            ),
            cloudformation=cloudformation,
        )

    @property
    def status(self):
        """Retrieves the stack's current status"""
        return self.__describe()["StackStatus"]

    @property
    def resources(self):
        """Retrieves the stack's resources"""
        stack_resources = self.cloudformation.describe_stack_resources(
            StackName=self.stack_id
        )["StackResources"]

        return {resource["LogicalResourceId"]: resource for resource in stack_resources}

    @property
    def events(self):
        """Retrieves stack events"""
        return self.cloudformation.describe_stack_events(StackName=self.stack_id)[
            "StackEvents"
        ]

    def delete(self, wait: bool = True):
        """Performs a delete against the stack and optionally waits for it to complete"""
        self.cloudformation.delete_stack(StackName=self.stack_id)

        if wait:
            stack_status = self.wait()

            if stack_status not in SUCCESSFUL_STACK_STATUSES:
                raise Exception(
                    f"Stack did not delete successfully: {self.name} is in {stack_status} status"
                )

    def wait(self) -> str:
        """Waits for a stack update to complete, logging each event during the update"""
        stack_status = self.status
        events = self.events

        event_ids = [event["EventId"] for event in events]

        for event in reversed(events[:1]):
            log_event(
                event["LogicalResourceId"],
                event["ResourceStatus"],
                event.get("ResourceStatusReason", None),
            )

        while stack_status in IN_PROGRESS_STACK_STATUSES:
            events = filter(
                lambda event: event["EventId"] not in event_ids, reversed(self.events),
            )

            for event in events:
                log_event(
                    event["LogicalResourceId"],
                    event["ResourceStatus"],
                    event.get("ResourceStatusReason", None),
                )
                event_ids.append(event["EventId"])

            stack_status = self.status

            time.sleep(5)

        return stack_status

    def mark(self, strategy):
        """Mark this stack as being selected by the strategy"""
        self.marked_by_strategies.append(strategy)

    def __describe(self) -> Dict:
        """Call CloudFormation DescribeStack"""
        stack_data = self.cloudformation.describe_stacks(StackName=self.stack_id)

        return stack_data["Stacks"][0]  # type: ignore


def get_stacks(cloudformation) -> Iterator[Stack]:
    """Retrieve all stacks as Stack objects"""
    return map(
        lambda stack: Stack.factory_from_stack_detail(cloudformation, stack),
        paginate(cloudformation.describe_stacks),
    )
