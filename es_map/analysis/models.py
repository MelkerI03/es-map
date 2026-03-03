from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network
from typing import List, Set, Dict


@dataclass(eq=True)
class Host:
    """Represents a network host with an identifier, optional hostname, and IP addresses."""

    host_id: str
    hostname: str | None = None
    ips: Set[IPv4Address] = field(default_factory=set)

    def __hash__(self) -> int:
        """Compute hash based on host_id."""
        return hash(self.host_id)

    def add_ip(self, ip: IPv4Address) -> None:
        """Add an IP address to the host.

        Args:
            ip (IPv4Address): IP address to add.
        """
        self.ips.add(ip)


@dataclass
class SubnetNode:
    """Represents a subnet and the hosts that belong to it."""

    network: IPv4Network
    hosts: Set[Host] = field(default_factory=set)

    def add_host(self, host: Host) -> None:
        """Add a host to the subnet.

        Args:
            host (Host): Host to add.
        """
        self.hosts.add(host)


class SubnetRegistry:
    """Registry that maps subnets to their respective hosts."""

    def __init__(self, networks: List[IPv4Network]):
        """Initialize the registry with a list of subnets.

        Args:
            networks (List[IPv4Network]): List of IPv4Network objects to register.
        """
        self._subnets: Dict[IPv4Network, SubnetNode] = {
            net: SubnetNode(network=net) for net in networks
        }

    def find_subnets(self, ip: IPv4Address) -> List[SubnetNode]:
        """Find all subnets containing a given IP address.

        Args:
            ip (IPv4Address): IP address to search for.

        Returns:
            List[SubnetNode]: List of subnet nodes containing the IP.
        """
        return [subnet for subnet in self._subnets.values() if ip in subnet.network]

    def attach_host(self, host: Host) -> None:
        """Attach a host to all subnets that contain its IP addresses.

        Args:
            host (Host): Host to attach.
        """
        for ip in host.ips:
            for subnet in self.find_subnets(ip):
                subnet.add_host(host)
