"""Elasticsearch query helpers.

This module contains high-level query functions that retrieve
cluster information and return structured Python data.
"""

import re
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

# from tempfile import NamedTemporaryFile
from elasticsearch import Elasticsearch

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def fetch_hosts_from_file(file: Path, query_index: str) -> list[dict]:
    """Fetch host information from Elasticdump formatted file

    This query groups documents by host ID and retrieves associated
    hostnames and IP addresses.

    Args:
        client: Elasticsearch client instance. TODO
        query_index: Elasticsearch index to query.

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

    def wildcard_to_regex(wildcard_pattern: str) -> str:
        """Translates wildcard syntax to a regex pattern.

        * -> matches everything (.*)
        ? -> matches any single character (.)

        Returns: regex_pattern
        """
        regex_pattern = re.escape(wildcard_pattern)
        regex_pattern = regex_pattern.replace(r"\*", ".*")
        regex_pattern = regex_pattern.replace(r"\?", ".")

        return f"^(\\.ds\\-)?{regex_pattern}$"

    index_pattern = wildcard_to_regex(query_index)

    df = (
        pl.scan_ndjson(file, ignore_errors=True)
        .filter(pl.col("_index").str.contains(index_pattern))
        .select(
            [
                pl.col("_source")
                .struct.field("host")
                .struct.field("id")
                .alias("host_id"),
                pl.col("_source")
                .struct.field("host")
                .struct.field("name")
                .alias("host_name"),
                pl.col("_source")
                .struct.field("host")
                .struct.field("ip")
                .alias("host_ip"),
                pl.col("_source")
                .struct.field("source")
                .struct.field("ip")
                .alias("source_ip"),
                pl.col("_source")
                .struct.field("destination")
                .struct.field("ip")
                .alias("destination_ip"),
                pl.col("_source")
                .struct.field("@timestamp")
                .cast(pl.Utf8, strict=False)
                .alias("timestamp"),
            ]
        )
        # Resolves null issues
        .with_columns(
            [
                pl.concat_list(pl.col("source_ip").cast(pl.Utf8, strict=False)).alias(
                    "source_ip"
                ),
                pl.concat_list(
                    pl.col("destination_ip").cast(pl.Utf8, strict=False)
                ).alias("destination_ip"),
            ]
        )
        # Connections are (source_ips ∪ destination_ips)
        .select(
            [
                "host_id",
                "host_name",
                "host_ip",
                "timestamp",
                pl.col("source_ip")
                .fill_null([])
                .list.concat(
                    pl.col("destination_ip").fill_null([])
                )  # concatenates both lists
                .list.unique()  # set union
                .alias("ip"),
            ]
        )
        # Host ID is the key
        .group_by("host_id")
        .agg(
            [
                pl.col("host_name").drop_nulls().first().alias("hostname"),
                pl.col("host_ip").explode().drop_nulls().unique().alias("ips"),
                pl.col("ip").explode().drop_nulls().unique().alias("connections"),
                pl.min("timestamp").alias("first_seen"),
                pl.max("timestamp").alias("last_seen"),
            ]
        )
        .collect(engine="streaming")
    )

    return df.to_dicts()


def fetch_hosts_from_client(client: Elasticsearch, query_index: str) -> list[dict]:
    """Fetch host information from Elasticsearch using aggregations.

    This query groups documents by host ID and retrieves associated
    hostnames and IP addresses.

    Args:
        client: Elasticsearch client instance.
        query_index: Elasticsearch index to query.

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

    def epoch_to_iso(time: float) -> str:
        strftime_format = "%Y-%m-%dT%H:%M:%S.%f"

        dt_object = datetime.fromtimestamp(time / 1000, UTC)  # Translate from ms -> s
        iso_time = dt_object.strftime(strftime_format)[:-3] + "Z"  # Jank
        return iso_time

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

        first_seen = bucket.get("first_seen", {}).get("value", "")
        first_seen_iso = epoch_to_iso(first_seen)

        last_seen = bucket.get("last_seen", {}).get("value", "")
        last_seen_iso = epoch_to_iso(last_seen)

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
                "first_seen": first_seen_iso,
                "last_seen": last_seen_iso,
                "connections": connections,
            }
        )

    logger.debug(
        "Parsed hosts from aggregation",
        extra={"host_count": len(results)},
    )

    return results
