import ipaddress

from elasticsearch import Elasticsearch

from es_map.analysis.models import Host
from es_map.elastic.queries import fetch_hosts
from es_map.utils.logging import get_logger

logger = get_logger(__name__)


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

    for host_record in raw_host_records:
        host = Host(
            host_id=host_record["host_id"],
            hostname=host_record["hostname"],
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

            host.add_ip(ip_addr)

        hosts.append(host)

    logger.debug(
        "Built hosts from Elasticsearch",
        extra={
            "host_count": len(hosts),
        },
    )
    return hosts
