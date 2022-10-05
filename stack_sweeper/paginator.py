from typing import Dict, Iterator


def paginate(method, **kwargs) -> Iterator[Dict]:
    """Paginates through a boto3/botocore client method"""
    client = method.__self__
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for result in page:
            yield result
