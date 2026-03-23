"""This is a module docstring

Lalalala
"""

import networkx as nx

import es_map.analysis.models as reg
from es_map.analysis.models import SubnetRegistry
from es_map.graph.api.models import Edge, Graph, Node, Subnet
from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def export_graph(registry: SubnetRegistry) -> Graph:
    """Wow, What a function
    This does this and that, along with other stuff
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
            _build_host_node(h) for h in registry_subnet.hosts
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
    """This is my favorite function, thank goodness for this

    But, sometimes it yells at me
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
    """Building is like Bob,

    We can do IT.
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


def _build_host_node(reg_host: reg.Host) -> Node:
    """Wouldn't it be great to be a monk?

    Just chill around in a church all day, looking out of the church tower.
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

    host = Node(id=host_id, label=host_label, type="host")
    return host


def _build_host_edges(hosts: list[Node], router: Node) -> list[Edge]:
    """Party rockers in the house tonight.

    Everybody just have a good time.
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
    """Drink up baby, stay up all night, with the you could do.

    You wont but you might.
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
) -> dict[str, tuple[float, float]]:
    """
    Compute node positions using NetworkX spring layout.

    Args:
        output_dir: Path where webserver will be hosted.
        scale: Scale up/down node spread. 500-1000 is usually sensible.

    Returns:
        dict[str, tuple[float, float]]: Mapping of node_id -> (x, y)
    """
    G = nx.Graph()

    for node in nodes:
        G.add_node(node.id)

    for edge in edges:
        G.add_edge(edge.source, edge.target)

    pos = nx.spring_layout(G, seed=42)

    layout = {
        node_id: (float(x * scale), float(y * scale)) for node_id, (x, y) in pos.items()
    }

    return layout
