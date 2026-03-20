"""Elasticsearch query helpers.

This module contains high-level query functions that retrieve
cluster information and return structured Python data.
"""

from elasticsearch import Elasticsearch

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def fetch_hosts(client: Elasticsearch, query_index: str | None) -> list[dict]:
    """Fetch host information from Elasticsearch using aggregations.

    This query groups documents by host ID and retrieves associated
    hostnames and IP addresses.

    Args:
        client: Elasticsearch client instance.
        query_index: Optional index to query. If not provided, all indices are queried.

    Returns:
        A list of dictionaries containing:
            - host_id: Unique identifier of the host.
            - hostname: Optional hostname.
            - ips: List of IP address strings.

    Raises:
        KeyError: If the expected aggregation structure is missing.
    """
    query_index = (
        query_index or "*"
    )  # Default to querying all indices if none specified

    logger.debug(
        "Fetching hosts from Elasticsearch",
        extra={"index": query_index},
    )

    response = client.search(
        index=query_index,
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

    aggregations = response.body.get("aggregations", {})
    hosts_agg = aggregations.get("hosts", {})
    buckets = hosts_agg.get("buckets", [])

    logger.debug(
        "Received host aggregation results",
        extra={"bucket_count": len(buckets)},
    )

    results = []

    for bucket in buckets:
        host_id = bucket["key"]

        hostname_bucket = bucket["hostnames"]["buckets"]
        if hostname_bucket:
            hostname = hostname_bucket[0]["key"]
        else:
            hostname = None

        ip_buckets = bucket.get("ips", {}).get("buckets", [])
        ips = [ip["key"] for ip in ip_buckets]

        results.append(
            {
                "host_id": host_id,
                "hostname": hostname,
                "ips": ips,
            }
        )

    logger.debug(
        "Parsed hosts from aggregation",
        extra={"host_count": len(results)},
    )
    return results
