import argparse
import os
import sys
import logging
from datetime import timedelta
from typing import List

import boto3  # type: ignore

from .log_utils import log, log_setup
from .cloudformation import get_stacks
from .exclude_names_strategy import ExcludeNamesStrategy
from .exclude_tag_strategy import ExcludeTagStrategy
from .last_updated_strategy import LastUpdatedStrategy
from .limited_strategy import LimitedStrategy
from .nested_strategies import NestedAllStrategy, NestedAnyStrategy
from .expiration_tag_strategy import ExpirationTagStrategy
from .base_strategy import BaseStrategy


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse CLI arguments"""
    parser = argparse.ArgumentParser(
        description="Finds (and optionally deletes) stacks that meet certain age criteria"
    )
    parser.add_argument(
        "--expiry-tag",
        type=str,
        help="the tag name that contains the stack's expiry",
        required=False,
    )
    parser.add_argument(
        "--exclude-tag",
        type=str,
        help="the tag name that excludes the stack from consideration",
        required=False,
    )
    parser.add_argument(
        "--exclude-stacks",
        nargs="+",
        type=str,
        help="list of stack names to exclude from consideration",
        required=False,
        default=[],
    )
    parser.add_argument(
        "--exclude-stack-prefixes",
        nargs="+",
        type=str,
        help="list of stack name prefixes to exclude from consideration",
        required=False,
        default=[],
    )
    parser.add_argument(
        "--stack-update-age",
        type=int,
        help="number of days since last stack update",
        required=False,
    )
    parser.add_argument(
        "--limit", type=int, help="maximum number of stacks to delete", required=False,
    )
    parser.add_argument(
        "--log-level",
        help="The log level to display (default: INFO)",
        required=False,
        default="INFO",
    )
    parser.add_argument(
        "--delete",
        help="Should this delete identified stacks?",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--no-wait",
        help="Should delete operations wait for each stack to finish?",
        action="store_false",
        required=False,
        default=True,
        dest="wait",
    )

    parsed_args = parser.parse_args(args=args)
    if not any([parsed_args.stack_update_age, parsed_args.expiry_tag]):
        parser.error("At least one of --expiry-tag or --stack-update-age is required")

    if not parsed_args.wait and not parsed_args.delete:
        parser.error("You must specify --delete to use --no-wait")

    return parsed_args


def get_strategy_from_args(args: argparse.Namespace):
    """Construct a strategy from args"""
    age_strategies: List[BaseStrategy] = list()
    if args.expiry_tag:
        age_strategies.append(ExpirationTagStrategy(args.expiry_tag))

    if args.stack_update_age:
        age_strategies.append(
            LastUpdatedStrategy(timedelta(days=args.stack_update_age))
        )

    strategies: List[BaseStrategy] = [
        NestedAnyStrategy(age_strategies),
    ]

    if args.exclude_tag:
        strategies.append(ExcludeTagStrategy(args.exclude_tag))

    if any([args.exclude_stacks, args.exclude_stack_prefixes]):
        strategies.append(
            ExcludeNamesStrategy(
                exclude_names=args.exclude_stacks,
                exclude_name_prefixes=args.exclude_stack_prefixes,
            )
        )

    strategy: BaseStrategy = NestedAllStrategy(strategies)
    if args.limit:
        strategy = LimitedStrategy(args.limit, strategy)

    return strategy


def main(args: argparse.Namespace):  # pragma: no cover
    """The main entry point"""
    log_setup(args.log_level)

    if not args.delete:
        log(
            "This is a DRY RUN only. To actually delete stacks, you must add --delete to the execution"
        )
        command = " ".join(sys.argv[1:])
        log(f"e.g.: {os.path.basename(sys.argv[0])} {command} --delete")

    strategy = get_strategy_from_args(args)

    log(f"Using strategy configuration: {str(strategy)}", logging.DEBUG)

    cloudformation = boto3.client("cloudformation")
    stacks = list(get_stacks(cloudformation))

    filtered_stacks = list(filter(strategy.should_remove, stacks))

    log(f"{len(filtered_stacks)} stacks (of {len(stacks)}) identified for removal")
    for stack in filtered_stacks:
        marked_reasons = [
            mark.get_mark_reason(stack) for mark in stack.marked_by_strategies
        ]
        log(
            f"{stack.name} selected for removal: {', '.join(marked_reasons)}",
            logging.DEBUG,
        )

        if args.delete:
            try:
                stack.delete(args.wait)
            except Exception as e:  # pylint: disable=broad-except
                log(str(e), logging.ERROR)


def entry_point():  # pragma: no cover
    """The setuptools CLI entrypoint"""
    main(parse_args(sys.argv[1:]))
