"""Graph export utilities for converting internal subnet registry data
into a structured graph representation.

This module transforms the domain-level `SubnetRegistry` into a
Pydantic-based graph model consisting of nodes, edges, subnets,
and layout information suitable for visualization and frontend use.

The exported graph is intended to be consumed by rendering layers
(e.g. D3.js) or exposed via an API.
"""

import networkx as nx

import es_map.analysis.models as reg
from es_map.analysis.models import SubnetRegistry
from es_map.graph.api.models import Edge, Graph, Node, Subnet
from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def export_graph(registry: SubnetRegistry) -> Graph:
    """Convert a subnet registry into a graph model.

    This function traverses the entire subnet hierarchy and builds:
    - Router nodes
    - Host nodes
    - Parent-child subnet edges
    - Host-to-router edges
    - Subnet groupings
    - A computed layout for visualization

    Args:
        registry: The subnet registry containing all discovered
            subnets and their associated hosts.

    Returns:
        Graph: A fully constructed graph object containing nodes,
            edges, subnets, and layout data.
    """
    subnets: list[Subnet] = []
    nodes: list[Node] = []
    edges: list[Edge] = []

    logger.debug("Starting graph export")
    logger.debug("Processing %d subnets", len(registry._subnets))

    for registry_subnet in registry._subnets.values():
        logger.debug(
            "Processing subnet",
            extra={
                "subnet": str(registry_subnet.network),
                "hosts": len(registry_subnet.hosts),
            },
        )

        router = _build_router_node(registry_subnet)
        nodes.append(router)

        if registry_subnet.parent:
            edges.append(_build_parent_edge(registry_subnet))

        current_subnet_hosts: list[Node] = [
            _build_host_node(registry, h) for h in registry_subnet.hosts
        ]

        nodes.extend(current_subnet_hosts)

        edges.extend(_build_host_edges(current_subnet_hosts, router))

        if not registry_subnet.network == registry.root_subnet:
            subnets.append(_build_subnet(registry_subnet))

    layout = generate_layout(nodes, edges)

    logger.debug(
        "Graph export complete",
        extra={
            "nodes": len(nodes),
            "edges": len(edges),
            "subnets": len(subnets),
        },
    )

    return Graph(nodes=nodes, edges=edges, subnets=subnets, layout=layout)


def _build_router_node(reg_subnet: reg.Subnet) -> Node:
    """Create a router node for a subnet.

    Args:
        reg_subnet: The subnet from which the router is derived.

    Returns:
        Node: A node representing the subnet's router.
    """
    logger.debug(
        "Creating router node",
        extra={"router_id": reg_subnet.router_id},
    )

    router_id = reg_subnet.router_id
    router_label = "R"

    router = Node(id=router_id, label=router_label, type="router")
    return router


def _build_parent_edge(reg_subnet: reg.Subnet) -> Edge:
    """Create an edge between a subnet and its parent subnet.

    Args:
        reg_subnet: The subnet containing a reference to its parent.

    Returns:
        Edge: An edge connecting the parent router to this subnet's router.
    """
    assert reg_subnet.parent

    logger.debug(
        "Creating parent edge",
        extra={
            "source": reg_subnet.parent.router_id,
            "target": reg_subnet.router_id,
        },
    )

    edge_source = reg_subnet.parent.router_id
    edge_target = reg_subnet.router_id
    edge = Edge(source=edge_source, target=edge_target)

    return edge


def _build_host_node(registry: SubnetRegistry, reg_host: reg.Host) -> Node:
    """Create a node representing a host.

    Args:
        registry: The subnet registry containing all discovered
            subnets and their associated hosts.
        reg_host: The host object from the registry.

    Returns:
        Node: A node representing the host, using hostname as label
            if available, otherwise falling back to host ID.
    """

    logger.debug(
        "Creating host node",
        extra={
            "host_id": reg_host.host_id,
            "hostname": reg_host.hostname,
        },
    )
    host_id = reg_host.host_id
    host_label = reg_host.hostname if reg_host.hostname else host_id

    host_ips = [str(ip) for ip in reg_host.ip_addresses]

    host_subnets: list[str] = []
    for ip in reg_host.ip_addresses:
        subnets = registry.get_subnets_for_ip(ip)
        subnet_cidrs = [str(subnet.network) for subnet in subnets]
        host_subnets.extend(subnet_cidrs)

    host = Node(
        id=host_id,
        label=host_label,
        ip_addresses=host_ips,
        subnets=host_subnets,
        type="host",
    )
    return host


def _build_host_edges(hosts: list[Node], router: Node) -> list[Edge]:
    """Create edges connecting hosts to their subnet router.

    Args:
        hosts: List of host nodes belonging to a subnet.
        router: The router node for the subnet.

    Returns:
        list[Edge]: Edges connecting each host to the router.
    """

    logger.debug(
        "Creating host edges",
        extra={
            "router": router.id,
            "host_count": len(hosts),
        },
    )
    return [Edge(source=host.id, target=router.id) for host in hosts]


def _build_subnet(registry_subnet: reg.Subnet) -> Subnet:
    """Create a subnet representation including all member nodes.

    This includes recursive collection of:
    - Hosts
    - Router
    - All nested child subnet members

    Args:
        registry_subnet: The subnet to convert.

    Returns:
        Subnet: A structured subnet object with member IDs and metadata.
    """

    def get_member_ids_recursive(registry_subnet: reg.Subnet) -> list[str]:
        member_ids = [host.host_id for host in registry_subnet.hosts]
        member_ids.append(registry_subnet.router_id)

        for child in registry_subnet.child_subnets:
            member_ids.extend(get_member_ids_recursive(child))

        return member_ids

    subnet_id = registry_subnet.subnet_id
    subnet_label = str(registry_subnet.network)
    subnet_member_ids = get_member_ids_recursive(registry_subnet)

    logger.debug(
        "Creating subnet",
        extra={
            "subnet": str(registry_subnet.network),
            "members": len(subnet_member_ids),
        },
    )

    subnet = Subnet(id=subnet_id, label=subnet_label, members=subnet_member_ids)
    return subnet


def generate_layout(
    nodes: list[Node], edges: list[Edge], scale: float = 800
) -> dict[str, list[float]]:
    """Compute a 2D layout for graph nodes using a force-directed algorithm.

    The layout is computed using NetworkX's spring layout algorithm
    with a fixed random seed for deterministic output.

    Args:
        nodes: List of graph nodes.
        edges: List of graph edges.
        scale: Scaling factor for layout coordinates. Larger values
            spread nodes further apart.

    Returns:
        dict[str, list[float]: Mapping of node IDs to [x, y]
            positions suitable for rendering.
    """
    G = nx.Graph()

    for node in nodes:
        G.add_node(node.id)

    for edge in edges:
        G.add_edge(edge.source, edge.target)

    pos = nx.spring_layout(G, seed=42)

    layout = {
        node_id: [float(x * scale), float(y * scale)] for node_id, (x, y) in pos.items()
    }

    return layout
