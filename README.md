# Stack Sweeper

For all your cleaning-up-of-account needs, well,
cleaning-up-of-CloudFormation-stack...needs.

Stack Sweeper helps you remove stale CloudFormation stacks, without removing baseline
ones that you need.

## Usage

Sweeping (removing) stacks:

```bash
usage: stack-sweeper [-h]
                     [--expiry-tag EXPIRY_TAG]
                     [--stack-update-age STACK_UPDATE_AGE]
                     [--exclude-tag EXCLUDE_TAG]
                     [--exclude-stacks EXCLUDE_STACKS [EXCLUDE_STACKS ...]]
                     [--exclude-stack-prefixes EXCLUDE_STACK_PREFIXES [EXCLUDE_STACK_PREFIXES ...]]
                     [--limit LIMIT]
                     [--delete]
                     [--disable-termination-protection]
                     [--no-wait]
                     [--region REGION]
                     [--log-level LOG_LEVEL]
```

Options:

- `--expiry-tag VALUE` a tag on stacks to use to determine when a stack has _expired_. i.e.
  when it should be deleted after. e.g. `stack-sweeper:expiry`.
  Default: do not use an expiry tag
- `--stack-update-age VALUE` consider stacks that have not been updated in `VALUE` days
  for deletion.
  Default: do not delete aging stacks
- `--exclude-tag VALUE` a tag on stacks to use to make stack-sweeper ignore it for
  consideration. e.g. `stack-sweeper:ignore`.
  Note: the value provided is used as a tag key, tag values are ignored.
  Default: do not use a tag for exclusion
- `--exclude-stack-prefixes VALUE [VALUE ...]` exclude any stacks with a name starting
  with `VALUE` (accepts multiple values, space-separated).
  Default: do not use a prefix for exculsion
- `--exclude-stacks VALUE [VALUE ...]` exclude specifically named stacks. Useful if you
  have stacks that cannot be tagged adn don't otherwise meet an exclusion prefix
- `--limit VALUE` maximum number of stacks to delete in one operation.
  Default: remove all matching, non-excluded stacks
- `--delete` should stack-sweeper delete identified stacks, or just report on them?
  Default: A dry-run is performed and no stacks are deleted
- `--disable-termination-protection` if a stack has termination protection enabled,
  should stack-sweeper disable it and then delete?
  Default: ignore stacks with termination protection enabled
- `--no-wait` should stack-sweeper i
  nitiate a deletion operation and exit immediately?
  Default: waits for all deletion operations to complete
- `--region` the AWS region to run against. Default: AWS_DEFAULT_REGION environment variable

### Examples

#### Deletion Criteria

To delete any stack with the tag `stack-sweeper:expiry` or that has not been updated
in more than 90 days:

```bash
stack-sweeper --expiry-tag stack-sweeper:expiry --stack-update-age 90 --delete
```

#### Excluding stacks

To ensure stacks prefixed with `StackSet-` are not considered for removal:

```bash
stack-sweeper --exclude-stack-prefixes StackSet- [...]
```

To ignore `my-crucial-stack` from deletion, even though it may meet other criteria:

```bash
stack-sweeper --exclude-stacks my-crucial-stack [...]
```

To ignore any stack tagged with `stack-sweeper:ignore`, even though it may meet other criteria:

```bash
stack-sweeper --exclude-tag stack-sweeper:ignore [...]
```
