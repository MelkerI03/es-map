"""Graph construction utilities from Elasticsearch data.

This module is responsible for:
- Fetching and transforming raw Elasticsearch data into domain models
- Building a subnet registry from configured networks
- Assigning hosts to subnets
- Exporting the resulting structure into a graph API model

It acts as the bridge between:
- the Elasticsearch data source
- the domain layer (Host, SubnetRegistry)
- the graph export layer used by the API and frontend
"""

import ipaddress

from elasticsearch import Elasticsearch

from es_map.analysis.models import Host, SubnetRegistry
from es_map.config import ElasticConfig
from es_map.elastic.queries import fetch_hosts
from es_map.graph.api.export import export_graph
from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def build_graph(client: Elasticsearch, config: ElasticConfig):
    registry = SubnetRegistry(config.subnets)

    hosts = build_hosts(client, config.index)
    logger.info("Fetched hosts from Elasticsearch", extra={"count": len(hosts)})

    for host in hosts:
        registry.assign_host_to_subnet(host)
    logger.info("Assigned hosts to subnet registry")

    return export_graph(registry)


def build_hosts(client: Elasticsearch, index_name: str | None) -> list[Host]:
    """Build Host objects from Elasticsearch data.

    Fetches raw host data from Elasticsearch and converts it into
    Host domain models, filtering out IPv6 addresses.

    Args:
        client: Elasticsearch client instance.
        index_name: Optional index name to query.

    Returns:
        A list of Host objects populated with IPv4 addresses.

    Raises:
        ValueError: If an invalid IP address is encountered.
    """

    raw_host_records = fetch_hosts(client, index_name)
    logger.debug(
        "Fetched raw hosts from Elasticsearch",
        extra={"raw_host_count": len(raw_host_records)},
    )

    hosts: list[Host] = []

    all_ips = set()

    for host_record in raw_host_records:
        host = Host(
            host_id=host_record["host_id"],
            hostname=host_record["hostname"],
            connections=host_record["connections"],
            first_seen=str(host_record["first_seen"]),
            last_seen=str(host_record["last_seen"]),
        )

        for ip_str in host_record["ips"]:

            try:
                ip_addr = ipaddress.ip_address(ip_str)
            except ValueError:
                logger.error(
                    "Invalid IP address encountered",
                    extra={"ip": ip_str, "host_id": host_record.get("host_id")},
                )
                raise

            if isinstance(ip_addr, ipaddress.IPv6Address):
                logger.debug(
                    "Skipping IPv6 address",
                    extra={"ip": ip_str, "host_id": host_record.get("host_id")},
                )
                continue

            if ip_addr in ipaddress.IPv4Network("127.0.0.0/8"):
                # Don't include loopback addresses
                continue

            host.add_ip(ip_addr)
            all_ips.add(ip_str)

        hosts.append(host)

    # Only add hosts connections that are in our network
    for host in hosts:
        host.connections = [conn for conn in host.connections if conn in all_ips]

    logger.debug(
        "Built hosts from Elasticsearch",
        extra={
            "host_count": len(hosts),
        },
    )
    return hosts
