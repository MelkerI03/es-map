from es_map.analysis.models import SubnetRegistry
from es_map.graph.models import Edge, Graph, Node, Subnet
import es_map.analysis.models as reg


def export_graph(registry: SubnetRegistry) -> Graph:
    subnets: list[Subnet] = []
    nodes: list[Node] = []
    edges: list[Edge] = []

    for registry_subnet in registry._subnets.values():

        router = _build_router_node(registry_subnet)
        nodes.append(router)

        if registry_subnet.parent:
            edges.append(_build_parent_edge(registry_subnet))

        current_subnet_hosts: list[Node] = [
            _build_host_node(h) for h in registry_subnet.hosts
        ]

        nodes.extend(current_subnet_hosts)

        edges.extend(_build_host_edges(current_subnet_hosts, router))

        subnets.append(_build_subnet(registry_subnet, hosts=current_subnet_hosts))

    return Graph(nodes=nodes, edges=edges, subnets=subnets)


def _build_router_node(reg_subnet: reg.Subnet) -> Node:
    router_id = reg_subnet.router_id
    router_label = "R"

    router = Node(id=router_id, label=router_label, type="router")
    return router


def _build_parent_edge(reg_subnet: reg.Subnet) -> Edge:
    assert reg_subnet.parent

    edge_source = reg_subnet.parent.router_id
    edge_target = reg_subnet.router_id
    edge = Edge(source=edge_source, target=edge_target)

    return edge


def _build_host_node(reg_host: reg.Host) -> Node:
    host_id = reg_host.host_id
    host_label = reg_host.hostname if reg_host.hostname else host_id

    host = Node(id=host_id, label=host_label, type="host")
    return host


def _build_host_edges(hosts: list[Node], router: Node) -> list[Edge]:
    return [Edge(source=host.id, target=router.id) for host in hosts]


def _build_subnet(registry_subnet: reg.Subnet, hosts: list[Node]) -> Subnet:
    subnet_id = registry_subnet.subnet_id
    subnet_label = str(registry_subnet.network)
    subnet_member_ids = [host.id for host in hosts]

    subnet = Subnet(id=subnet_id, label=subnet_label, members=subnet_member_ids)
    return subnet
