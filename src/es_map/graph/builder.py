from typing import List, Set
from es_map.analysis.models import SubnetNode
import networkx as nx
import hypernetx as hnx


def build_subnet_graph(subnets: List[SubnetNode]) -> hnx.Hypergraph:
    """Build a hypergraph representing subnet membership.

    Each subnet is represented as a hyperedge containing all hosts that
    belong to the subnet, the router representing that subnet as well as
    all nodes in child subnets.

    Args:
        subnets: List of SubnetNode objects representing the network.

    Returns:
        hnx.Hypergraph: Hypergraph where:
            - nodes represent hosts or subnet routers
            - hyperedges represent subnets
    """

    def get_children(subnet: SubnetNode) -> Set[str]:
        members: Set[str] = set()
        members.add(subnet.router_id)
        for host in subnet.hosts:
            members.add(host.host_id)

        for child in subnet.child_subnets:
            members.update(get_children(child))

        return members

    edges: dict[str, Set[str]] = {}

    for subnet in subnets:
        members = get_children(subnet)

        edges[str(subnet.network)] = members

    return hnx.Hypergraph(edges)


def build_topology_graph(subnets: List[SubnetNode]) -> nx.Graph:
    """Build a topology graph describing network routing structure.

    The topology graph models how hosts connect to subnet routers and how
    subnet routers connect to parent subnet routers. The resulting graph
    represents the routing hierarchy of the network.

    Edge rules:
        - Each host connects to the router of the subnet it belongs to.
        - Each subnet router connects to the router of its parent subnet.

    Args:
        subnets: List of SubnetNode objects describing the subnet hierarchy.

    Returns:
        nx.Graph: Undirected graph containing host and router nodes with edges
        representing routing relationships.
    """

    graph = nx.Graph()

    for subnet in subnets:
        router_id = subnet.router_id

        # Ensure router node exists
        graph.add_node(
            router_id,
            type="router",
            subnet=str(subnet.network),
            subnet_id=subnet.network_id,
        )

        # Connect hosts to router
        for host in subnet.hosts:
            graph.add_node(
                host.host_id,
                type="host",
                hostname=host.hostname,
            )

            graph.add_edge(host.host_id, router_id)

        # Connect router to parent router
        if subnet.parent is not None:
            parent_router = subnet.parent.router_id

            graph.add_node(
                parent_router,
                type="router",
                subnet=str(subnet.parent.network),
                subnet_id=subnet.parent.network_id,
            )

            graph.add_edge(router_id, parent_router)

    return graph
