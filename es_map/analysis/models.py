from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network
from typing import List, Set, Dict


@dataclass(eq=True)
class Host:
    host_id: str
    hostname: str | None = None
    ips: set[IPv4Address] = field(default_factory=set)

    def __hash__(self) -> int:
        return hash(self.host_id)

    def add_ip(self, ip: IPv4Address) -> None:
        self.ips.add(ip)


@dataclass
class SubnetNode:
    network: IPv4Network
    hosts: Set[Host] = field(default_factory=set)

    def add_host(self, host: Host) -> None:
        self.hosts.add(host)


class SubnetRegistry:
    def __init__(self, networks: list[IPv4Network]):
        self._subnets: Dict[IPv4Network, SubnetNode] = {
            net: SubnetNode(network=net) for net in networks
        }

    def find_subnets(self, ip: IPv4Address) -> List[SubnetNode]:
        return [subnet for subnet in self._subnets.values() if ip in subnet.network]

    def attach_host(self, host: Host) -> None:
        for ip in host.ips:
            for subnet in self.find_subnets(ip):
                subnet.add_host(host)
