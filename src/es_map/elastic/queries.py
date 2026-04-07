"""Elasticsearch query helpers.

This module contains high-level query functions that retrieve
cluster information and return structured Python data.
"""

from elasticsearch import Elasticsearch

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def _extract_aggregate(object: dict) -> list[dict]:
    """Extract structured host data from Elasticsearch aggregation response.

    Parses the 'hosts' aggregation buckets and extracts host information
    including identifiers, names, IP addresses, timestamps, and network
    connections.

    Args:
        object: Raw Elasticsearch search response body containing aggregations.

    Returns:
        A list of dictionaries containing:
            - host_id: Unique identifier of the host (host.id or fallback field).
            - hostname: Optional hostname (top result).
            - ips: List of IP address strings.
            - first_seen: First time host has been mentioned.
            - last_seen: Last time host has been mentioned.
            - connections: List of hosts that this host has communicated with directly.

    Raises:
        KeyError: If the expected aggregation structure is missing.
    """
    aggregations = object.get("aggregations", {})
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

        first_seen = bucket.get("first_seen", {}).get("value", "")
        last_seen = bucket.get("last_seen", {}).get("value", "")

        source_ips_buckets = bucket.get("source_ips", {}).get("buckets", [])
        source_ips = {conn["key"] for conn in source_ips_buckets}

        destination_ips_buckets = bucket.get("destination_ips", {}).get("buckets", [])
        destination_ips = {conn["key"] for conn in destination_ips_buckets}

        connections = list(source_ips | destination_ips)

        results.append(
            {
                "host_id": host_id,
                "hostname": hostname,
                "ips": ips,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "connections": connections,
            }
        )
    return results


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
            - first_seen: First time host has been mentioned.
            - last_seen: Last time host has been mentioned.
            - connections: List of hosts that this host has communicated with directly.

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

    aggs = client.search(
        index=query_index,
        size=0,
        aggs={
            "hosts": {
                "terms": {"field": "host.id", "size": 10000},
                "aggs": {
                    "hostnames": {"terms": {"field": "host.name", "size": 1}},
                    "ips": {"terms": {"field": "host.ip", "size": 100}},
                    "first_seen": {"min": {"field": "@timestamp"}},
                    "last_seen": {"max": {"field": "@timestamp"}},
                    "source_ips": {"terms": {"field": "source.ip", "size": 1000}},
                    "destination_ips": {
                        "terms": {
                            "field": "destination.ip",
                            "size": 1000,
                        }
                    },
                },
            }
        },
    )

    fallback_aggs = client.search(
        index=query_index,
        size=0,
        query={"bool": {"must_not": {"exists": {"field": "host.id"}}}},
        aggs={
            "hosts": {
                "terms": {"field": "elastic_agent.id", "size": 10000},
                "aggs": {
                    "hostnames": {"terms": {"field": "host.name", "size": 1}},
                    "ips": {"terms": {"field": "host.ip", "size": 100}},
                    "first_seen": {"min": {"field": "@timestamp"}},
                    "last_seen": {"max": {"field": "@timestamp"}},
                    "source_ips": {"terms": {"field": "source.ip", "size": 1000}},
                    "destination_ips": {
                        "terms": {
                            "field": "destination.ip",
                            "size": 1000,
                        }
                    },
                },
            }
        },
    )

    hosts = _extract_aggregate(aggs.body)
    idless_hosts = _extract_aggregate(fallback_aggs.body)

    results = hosts + idless_hosts

    logger.debug(
        "Parsed hosts from aggregation",
        extra={"host_count": len(results)},
    )

    return results
