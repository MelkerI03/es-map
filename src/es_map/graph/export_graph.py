from typing import Any, Dict, List, Set
from es_map.analysis.models import Subnet, SubnetRegistry
from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def export_graph(subnet_registry: SubnetRegistry) -> Dict[str, List[Dict[str, Any]]]:
    """Export SubnetRegistry into a graph structure for rendering.

    This function produces a layout-agnostic graph representation consisting
    of nodes, edges, and subnet groupings.

    Args:
        subnet_registry (SubnetRegistry): Source of truth for network structure.

    Returns:
        dict: A dictionary containing:
            - nodes: list of node dictionaries
            - edges: list of edge dictionaries
            - subnets: list of subnet groupings
    """

    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    subnets: List[Dict[str, Any]] = []

    # Track added nodes to avoid duplicates
    seen_nodes: Set[str] = set()

    def add_node(node_id: str, label: str, node_type: str):
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
                    "source": str(host.host_id),
                    "target": str(router_id),
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
                    "source": str(router_id),
                    "target": str(subnet.parent.router_id),
                }
            )

    def collect_members(node: Subnet) -> Set[str]:
        members: Set[str] = set()

        members.add(node.router_id)

        for host in node.hosts:
            members.add(host.host_id)

        for child in node.child_subnets:
            members |= collect_members(child)

        return members

    for subnet in subnet_registry._subnets.values():

        if str(subnet.network) == "0.0.0.0/0":
            continue

        members = collect_members(subnet)

        subnets.append(
            {
                "id": str(subnet.network),
                "label": str(subnet.network),
                "members": list(members),
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
        "subnets": subnets,
    }
