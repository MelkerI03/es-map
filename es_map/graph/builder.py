import networkx as nx

from es_map.analysis.models import SubnetNode, Host, SubnetRegistry


def build_graph_from_registry(registry: SubnetRegistry) -> nx.Graph:
    """
    Build a NetworkX graph representing the network topology.

    Routers represent subnets. Hosts connect to the router of the
    smallest subnet they belong to. Routers connect to their parent
    subnet router.

    Args:
        registry (SubnetRegistry): Registry containing subnet hierarchy.

    Returns:
        nx.Graph: Network topology graph.
    """
    graph = nx.Graph()

    # Start traversal from root subnets
    roots = [s for s in registry._subnets.values() if s.parent is None]

    for root in roots:
        _add_subnet_recursive(graph, root)

    return graph


def _add_subnet_recursive(graph: nx.Graph, subnet: SubnetNode) -> None:
    """
    Recursively add subnet routers and hosts to the graph.

    Args:
        graph (nx.Graph): Graph being constructed.
        subnet (SubnetNode): Current subnet.
    """

    router_id = _router_id(subnet)

    if router_id not in graph:
        graph.add_node(
            router_id,
            label=str(subnet.network),
            type="router",
            subnet=str(subnet.network),
        )

    # Connect router to parent router
    if subnet.parent:
        parent_router = _router_id(subnet.parent)
        graph.add_edge(parent_router, router_id)

    for host in subnet.hosts:
        host_id = _add_host(graph, host)
        graph.add_edge(router_id, host_id)

    for child in subnet.child_subnets:
        _add_subnet_recursive(graph, child)


def _add_host(graph: nx.Graph, host: Host) -> str:
    """
    Add a host node to the graph.

    Args:
        graph (nx.Graph): Graph being constructed.
        host (Host): Host object.

    Returns:
        str: Host node ID.
    """

    host_id = f"host:{host.host_id}"

    if host_id not in graph:
        graph.add_node(
            host_id,
            label=host.hostname or host.host_id,
            type="host",
        )

    return host_id


def _router_id(subnet: SubnetNode) -> str:
    """
    Generate a router node ID for a subnet.

    Args:
        subnet (SubnetNode): Subnet node.

    Returns:
        str: Router node ID.
    """

    return f"router:{subnet.network_id}"
