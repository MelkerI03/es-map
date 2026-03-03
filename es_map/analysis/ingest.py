import ipaddress

from elasticsearch import Elasticsearch
from es_map.elastic.queries import fetch_hosts
from es_map.analysis.models import Host
import logging

logger = logging.getLogger(__name__)


def build_hosts_from_es(client: Elasticsearch, index: str | None) -> list[Host]:
    raw_hosts = fetch_hosts(client, index)

    hosts: list[Host] = []

    for entry in raw_hosts:
        host = Host(
            host_id=entry["host_id"],
            hostname=entry["hostname"],
        )

        for ip_str in entry["ips"]:
            ip_addr = ipaddress.ip_address(ip_str)
            if type(ip_addr) == ipaddress.IPv6Address:
                continue
            assert type(ip_addr) == ipaddress.IPv4Address

            host.add_ip(ip_addr)

        hosts.append(host)

    logger.debug(f"hosts: {hosts}")
    return hosts
