"""Graph export utilities.

This module converts domain models (SubnetRegistry, Host, Subnet)
into a structured graph representation suitable for visualization.

The output format is layout-agnostic and intended for downstream
processing such as graph layout or rendering.
"""

from es_map.analysis.models import Subnet, SubnetRegistry
from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def export_graph(subnet_registry: SubnetRegistry) -> dict[str, list[dict]]:
    """Export a SubnetRegistry into a graph representation.

    Converts the subnet hierarchy and associated hosts into a
    layout-agnostic structure consisting of nodes, edges, and subnet groupings.

    Args:
        subnet_registry: Source of truth for network structure.

    Returns:
        A dictionary containing:
            - nodes: List of node dictionaries with id, label, and type
            - edges: List of edge dictionaries with source and target
            - subnets: List of subnet groupings with member node IDs
    """
    logger.debug(
        "Exporting graph from subnet registry",
        extra={"subnet_count": len(subnet_registry._subnets)},
    )

    nodes: list[dict] = []
    edges: list[dict] = []
    subnets: list[dict] = []

    # Track added nodes to avoid duplicates
    seen_nodes: set[str] = set()

    def add_node(node_id: str, label: str, node_type: str):
        """Add a node to the graph if it has not already been added.

        Args:
            node_id: Unique identifier for the node.
            label: Display label for the node.
            node_type: Type of node (e.g., "host", "router").
        """
        if node_id in seen_nodes:
            return
        seen_nodes.add(node_id)

        nodes.append(
            {
                "id": str(node_id),
                "label": label,
                "type": node_type,
            }
        )

    # Build nodes n edges from registry
    for subnet in subnet_registry._subnets.values():

        router_id = subnet.router_id

        add_node(
            router_id,
            label=str(subnet.network),
            node_type="router",
        )

        # Hosts in this subnet
        for host in subnet.hosts:

            add_node(
                host.host_id,
                label=host.hostname or host.host_id,
                node_type="host",
            )

            # host -> router edge
            edges.append(
                {
                    "source": host.host_id,
                    "target": router_id,
                }
            )

        # Parent subnet connection
        if subnet.parent:
            add_node(
                subnet.parent.router_id,
                label=str(subnet.parent.network),
                node_type="router",
            )

            # router -> router edge
            edges.append(
                {
                    "source": router_id,
                    "target": subnet.parent.router_id,
                }
            )

        logger.debug(
            "Constructed graph structure",
            extra={
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
        )

    def collect_members(node: Subnet) -> set[str]:
        """Recursively collect all member node IDs for a subnet.

        Includes the subnet's router, its hosts, and all members of
        child subnets.

        Args:
            node: Subnet node to collect members from.

        Returns:
            A set of node IDs belonging to the subnet.
        """
        members: set[str] = set()

        members.add(node.router_id)

        for host in node.hosts:
            members.add(host.host_id)

        for child in node.child_subnets:
            members |= collect_members(child)

        return members

    for subnet in subnet_registry._subnets.values():

        # Skip root subnet
        if subnet.network == subnet_registry.root_subnet:
            continue

        members = collect_members(subnet)

        subnets.append(
            {
                "id": str(subnet.network),
                "label": str(subnet.network),
                "members": list(members),
            }
        )

        logger.debug(
            "Constructed subnet groupings",
            extra={"subnet_group_count": len(subnets)},
        )

    return {
        "nodes": nodes,
        "edges": edges,
        "subnets": subnets,
    }
