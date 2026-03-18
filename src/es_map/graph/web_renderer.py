import json
from pathlib import Path
import networkx as nx

from es_map.analysis.models import SubnetNode, SubnetRegistry


def export_graph(nx_graph: nx.Graph, subnet_registry: SubnetRegistry, pos: dict):
    print("\n=== EXPORT GRAPH (D3 MODE) ===\n")

    nodes = []
    edges = []
    subnets = []

    # --- Nodes
    for node, data in nx_graph.nodes(data=True):
        id_map = {node: str(node) for node in nx_graph.nodes()}
        node_id = id_map[node]

        x, y = pos[node_id]

        node_type = data.get("type", "host")
        hostname = data.get("hostname")

        nodes.append(
            {
                "id": str(node_id),
                "label": data.get("label", str(hostname)),
                "type": node_type,
                "x": float(x) * 800,
                "y": float(y) * 800,
            }
        )

        print(f"Node: {node_id} ({node_type}) @ {x:.2f}, {y:.2f}")

    # --- Edges
    for u, v in nx_graph.edges():
        edges.append({"source": str(u), "target": str(v)})
        print(f"Edge: {u} -> {v}")

    # --- Subnets
    for subnet in subnet_registry._subnets.values():
        if str(subnet.network) == "0.0.0.0/0":
            continue
        members = set()

        # collect hosts recursively
        def collect(node: SubnetNode):
            members.update(h.host_id for h in node.hosts)
            members.add(node.router_id)
            for child in node.child_subnets:
                collect(child)

        collect(subnet)

        subnets.append(
            {
                "id": str(subnet.network),
                "label": str(subnet.network),
                "members": list(members),
            }
        )

        for s in subnets:
            print(f"sub {s} has members: {members}")

        print(f"Subnet: {subnet.network} -> {len(members)} members")

    return {
        "nodes": nodes,
        "edges": edges,
        "subnets": subnets,
    }


def render_web(
    nx_graph: nx.Graph,
    subnet_registry: SubnetRegistry,
    output_dir: Path,
):
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    pos = nx.spring_layout(nx_graph, seed=42)

    data = export_graph(nx_graph, subnet_registry, pos)

    # write JSON
    (output_dir / "graph.json").write_text(json.dumps(data, indent=2))

    template_dir = Path(__file__).parent / "templates"
    (output_dir / "index.html").write_text((template_dir / "index.html").read_text())

    static_dir = Path(__file__).parent / "static"
    (output_dir / "graph.js").write_text((static_dir / "graph.js").read_text())

    print(f"\n✅ D3 visualization written to: {output_dir / 'index.html'}\n")
