"""
Elasticsearch query helpers.

This module contains high-level query functions that retrieve
cluster information and return structured Python data.
"""

from typing import Any, Dict, List
from elasticsearch import Elasticsearch


def fetch_hosts(client: Elasticsearch, index: str | None) -> List[Dict[str, Any]]:
    index = index or "*"  # If not defined, include all
    response = client.search(
        index=index,
        size=0,
        aggs={
            "hosts": {
                "terms": {"field": "host.id", "size": 10000},
                "aggs": {
                    "hostnames": {"terms": {"field": "host.name", "size": 1}},
                    "ips": {"terms": {"field": "host.ip", "size": 100}},
                },
            }
        },
    )

    buckets = response.body["aggregations"]["hosts"]["buckets"]

    results = []

    for bucket in buckets:
        host_id = bucket["key"]

        hostname_bucket = bucket["hostnames"]["buckets"]
        hostname = hostname_bucket[0]["key"] if hostname_bucket else None

        ips = [ip["key"] for ip in bucket["ips"]["buckets"]]

        results.append(
            {
                "host_id": host_id,
                "hostname": hostname,
                "ips": ips,
            }
        )

    return results
