from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network
import ipaddress
from typing import List, Optional, Set, Dict
import hashlib


@dataclass(eq=True)
class Host:
    """Represents a network host with an identifier, optional hostname, and IP addresses."""

    host_id: str
    hostname: str | None = None
    ips: Set[IPv4Address] = field(default_factory=set)
    child_subnets: List["SubnetNode"] = field(
        default_factory=list
    )  # For virtual subnets

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
    parent: Optional["SubnetNode"] = field(
        default=None, repr=False, compare=False
    )  # TODO: add Union[Host, SubnetNode] so that virtual subnets can be owned by a host
    child_subnets: List["SubnetNode"] = field(default_factory=list, repr=False)

    def add_host(self, host: Host) -> None:
        """Add a host to the subnet.

        Args:
            host (Host): Host to add.
        """
        self.hosts.add(host)

    # TODO: Discern different NAT'ed subnet ids from eachother. Might be 2 different 10.0.2.0/24 subnets in the same network.
    @property
    def network_id(self) -> str:
        """A stable hashed identifier for this subnet."""
        raw = str(self.network).encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        return f"subnet:{digest[:12]}"

    @property
    def router_id(self) -> str:
        return f"router:{self.network_id}"


class SubnetRegistry:
    """Registry that maps subnets to their respective hosts."""

    def __init__(self, networks: List[IPv4Network]):
        """Initialize the registry with a list of subnets.

        Args:
            networks (List[IPv4Network]): List of IPv4Network objects to register.
        """
        self.externally_connected = False

        self.root_subnet = IPv4Network("0.0.0.0/0")
        networks.append(self.root_subnet)
        self._subnets: Dict[IPv4Network, SubnetNode] = {
            net: SubnetNode(network=net) for net in networks
        }
        self._build_hierarchy()

    def __repr__(self) -> str:
        return self._subnets.__repr__()

    def find_subnets_from_ip(self, ip: IPv4Address) -> List[SubnetNode]:
        """Find all subnets containing a given IP address.

        Args:
            ip (IPv4Address): IP address to search for.

        Returns:
            List[SubnetNode]: List of subnet nodes containing the IP.
        """
        return [subnet for subnet in self._subnets.values() if ip in subnet.network]

    def _build_hierarchy(self) -> None:
        """Assign parent relationships between subnets using CIDR containment."""

        subnets = list(self._subnets.values())

        subnets.sort(key=lambda s: s.network.prefixlen)

        candidates = []

        for subnet in subnets:
            subnet.parent = None

            for parent in reversed(candidates):
                if subnet.network.subnet_of(parent.network):
                    subnet.parent = parent
                    parent.child_subnets.append(subnet)
                    break

            candidates.append(subnet)

    def attach_host(self, host: Host) -> None:
        """Attach a host to the most specific subnet that contains any of its IPs.

        If a host is not part of a defined network, the whole registry is flagged
        as externally connected.

        Args:
            host (Host): Host to attach.
        """
        # Flatten and take best match
        max_subnet = max(
            (subnet for ip in host.ips for subnet in self.find_subnets_from_ip(ip)),
            key=lambda s: s.network.prefixlen,
            default=self._subnets[self.root_subnet],
        )

        if max_subnet.network == self.root_subnet:
            self.externally_connected = True
            return

        max_subnet.add_host(host)
