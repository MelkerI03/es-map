"""Domain models for network topology representation.

This module defines the core data structures used to model
network entities and their relationships, including:

- Host: Represents an individual machine with associated IP addresses
- Subnet: Represents a hierarchical IPv4 network segment
- SubnetRegistry: Manages subnet hierarchy construction and host assignment

These models form the domain layer of the application and are responsible for:
- Maintaining consistent relationships between hosts and subnets
- Encapsulating subnet hierarchy logic (CIDR containment)
- Providing stable identifiers for graph construction

This module is intentionally independent of:
- External data sources (e.g., Elasticsearch)
- API schemas (e.g., Pydantic models)
- Rendering or visualization concerns

It serves as the single source of truth for network topology logic.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass(eq=True)
class Host:
    """Represents a network host.

    Attributes:
        host_id (str): Unique identifier for the host.
        hostname (str): Optional human-readable hostname.
        ip_addresses (set[IPv4Address]): Set of IPv4 addresses assigned to the host.
        child_subnets (list[Subnet]): Virtual subnets owned by this host.
        connections (list[str]): List of host ids that this host has communicated with.
        first_seen (str): First time this node has been observed in the network (epoch).
        last_seen (str): Last time this node has been observed in the network (epoch).
    """

    host_id: str
    hostname: str | None = None
    ip_addresses: set[IPv4Address] = field(default_factory=set)
    child_subnets: list[Subnet] = field(default_factory=list)  # For virtual subnets
    connections: list[str] = field(default_factory=list)

    first_seen: str = ""
    last_seen: str = ""

    def __hash__(self) -> int:
        """Compute hash based on host_id."""
        return hash(self.host_id)

    def add_ip(self, ip: IPv4Address) -> None:
        """Add an IP address to the host.

        Args:
            ip: IP address to add.
        """
        self.ip_addresses.add(ip)


@dataclass
class Subnet:
    """Represents a subnet in a hierarchical network structure.

    Attributes:
        network (IPv4Network): The IPv4 network represented by this node.
        hosts (list[Host]): Hosts assigned to this subnet.
        parent (Subnet | None): Parent subnet in the hierarchy.
        child_subnets (list[Subnet]): Nested subnets within this subnet.
    """

    network: IPv4Network
    hosts: set[Host] = field(default_factory=set)
    parent: Subnet | None = field(default=None, repr=False, compare=False)
    child_subnets: list[Subnet] = field(default_factory=list, repr=False)

    def add_host(self, host: Host) -> None:
        """Add a host to the subnet.

        Args:
            host (Host): Host to add.
        """
        self.hosts.add(host)

    @property
    def subnet_id(self) -> str:
        """Generate a stable identifier for the subnet.

        Returns:
            A deterministic hash-based identifier derived from the network.
        """
        network_bytes = str(self.network).encode("utf-8")
        digest = hashlib.sha256(network_bytes).hexdigest()
        return f"subnet:{digest[:12]}"

    @property
    def router_id(self) -> str:
        """Generate a router identifier associated with this subnet.

        Returns:
            A string identifier prefixed with 'router:'.
        """
        return f"router:{self.subnet_id}"


class SubnetRegistry:
    """Registry for managing subnet hierarchy and host assignments.

    This class organizes subnets into a hierarchy and provides
    functionality to assign hosts to the most specific matching subnet.
    """

    def __init__(self, networks: list[IPv4Network]):
        """Initialize the registry with a list of subnets.

        Args:
            networks: List of IPv4Network objects to register.
        """
        self.externally_connected = False

        self.root_subnet = IPv4Network("0.0.0.0/0")

        networks = list(networks)
        networks.append(self.root_subnet)

        self._subnets: dict[IPv4Network, Subnet] = {
            net: Subnet(network=net) for net in networks
        }
        self._build_hierarchy()

    def get_subnets_for_ip(self, ip: IPv4Address) -> list[Subnet]:
        """Get all subnets containing the given IP address.

        Args:
            ip: IP address to search for.

        Returns:
            list[Subnet]: List of subnet nodes containing the IP.
        """
        return [subnet for subnet in self._subnets.values() if ip in subnet.network]

    def _build_hierarchy(self) -> None:
        """Build parent-child relationships between subnets.

        Subnets are ordered by prefix length and assigned parents based
        on CIDR containment.
        """

        subnets = list(self._subnets.values())

        logger.debug(
            "Building subnet hierarchy",
            extra={"subnet_count": len(subnets)},
        )

        subnets.sort(key=lambda s: s.network.prefixlen)

        potential_parents = []

        for subnet in subnets:
            subnet.parent = None

            for parent in reversed(potential_parents):
                if subnet.network.subnet_of(parent.network):
                    subnet.parent = parent
                    parent.child_subnets.append(subnet)

                    logger.debug(
                        "Assigned parent subnet",
                        extra={
                            "child": str(subnet.network),
                            "parent": str(parent.network),
                        },
                    )
                    break

            potential_parents.append(subnet)

    def assign_host_to_subnet(self, host: Host) -> None:
        """Assign a host to the most specific subnet that contains any of its IPs.

        If no matching subnet is found, the registry is marked as externally connected.

        Args:
            host: Host to attach.
        """
        logger.debug(
            "Attaching host to subnet",
            extra={"host_id": host.host_id, "ip_count": len(host.ip_addresses)},
        )
        # Flatten and take best match
        most_specific_subnet = max(
            (
                subnet
                for ip in host.ip_addresses
                for subnet in self.get_subnets_for_ip(ip)
            ),
            key=lambda s: s.network.prefixlen,
            default=self._subnets[self.root_subnet],
        )

        if most_specific_subnet.network == self.root_subnet:
            logger.debug(
                "Host not matched to any subnet, marking as external",
                extra={"host_id": host.host_id},
            )
            self.externally_connected = True
            return

        most_specific_subnet.add_host(host)
