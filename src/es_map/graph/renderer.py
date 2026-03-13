from pathlib import Path
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import networkx as nx
import hypernetx as hnx


def render_overlay(
    nx_graph: nx.Graph,
    hyper_graph: hnx.Hypergraph,
    output: Path,
) -> None:
    """Render an overlay of a NetworkX graph and a HyperNetX hypergraph.

    Nodes are positioned using a reproducible spring layout.
    Hyperedges (subnets) are drawn underneath the network nodes.

    Args:
        nx_graph (nx.Graph): The network topology graph (hosts + routers).
        hyper_graph (hnx.Hypergraph): Hypergraph representing subnet groupings.
        output (Path): Path to save the rendered figure (e.g., SVG, PNG).
    """
    pos = nx.spring_layout(nx_graph, seed=42)

    node_positions: Dict[str, Tuple[float, float]] = {
        node: (float(x), float(y)) for node, (x, y) in pos.items()
    }

    _, ax = plt.subplots(figsize=(8, 8))

    hnx.draw(
        hyper_graph,
        pos=node_positions,
        with_node_labels=False,
        node_radius=3,
        ax=ax,
        fill_edges=True,
        fill_edge_alpha=-0.8,
    )

    hostnames = {
        node: (attrs.get("hostname", node) if attrs.get("type") == "host" else "R")
        for node, attrs in nx_graph.nodes(data=True)
    }

    nx.draw(
        nx_graph,
        pos=node_positions,
        labels=hostnames,
        node_color="lightblue",
        edge_color="black",
        node_size=800,
        font_size=10,
        ax=ax,
        linewidths=1.5,
    )

    ax.set_title("Network Graph", fontsize=14)
    ax.margins(0.1)

    plt.tight_layout()
    plt.savefig(output)
    print(f"Overlay rendered to {output}")
