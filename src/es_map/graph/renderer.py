from pathlib import Path
from typing import Any, Dict
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import networkx as nx
import hypernetx as hnx
from hypernetx.drawing.rubber_band import (
    add_edge_defaults,
    draw_hyper_edges,
    get_default_radius,
    inflate,
)


def render_hypergraph(
    hyper_graph: hnx.Hypergraph, pos: Dict[str, Any], ax: Axes
) -> None:
    """Render a HyperNetX hypergraph on an existing matplotlib axis.

    Hyperedges are drawn as filled regions ("rubber bands") around their
    member nodes. Node positions must correspond to the layout used for the
    underlying graph so both visualizations align.
    Nodes are not rendered.

    Args:
        hyper_graph (hnx.Hypergraph): Hypergraph representing subnet groupings.
        pos (Dict[str, Tuple[float, float]]): Mapping of node identifiers to layout positions.
        ax (matplotlib.axes.Axes): Axis to render the hypergraph onto.
    """

    r0 = get_default_radius(hyper_graph, pos)
    node_radius = dict(
        zip(
            hyper_graph.nodes,
            [
                r0 * r
                for r in inflate(
                    hyper_graph.nodes, 3
                )  # pyright: ignore[reportGeneralTypeIssues]
            ],
        )
    )

    dr = 0.2
    edges_kwargs = add_edge_defaults(hyper_graph, {})
    draw_hyper_edges(
        H=hyper_graph,
        pos=pos,
        node_radius=node_radius,
        dr=dr,
        ax=ax,
        fill_edges=True,
        fill_edge_alpha=-0.8,
        **edges_kwargs,
    )


def render_nx_graph(nx_graph: nx.Graph, pos: Dict[str, Any], ax: Axes):
    """Render a NetworkX graph with labeled nodes on a matplotlib axis.

    Hosts are labeled with their hostname attribute if available, while
    router nodes are labeled with the generic label "R".

    Args:
        nx_graph (nx.Graph): Graph representing network topology.
        pos (Dict[str, Tuple[float, float]]): Mapping of node identifiers to layout positions.
        ax (matplotlib.axes.Axes): Axis to render the hypergraph onto.
    """

    hostnames = {
        node: (attrs.get("hostname", node) if attrs.get("type") == "host" else "R")
        for node, attrs in nx_graph.nodes(data=True)
    }

    nx.draw(
        nx_graph,
        pos=pos,
        labels=hostnames,
        node_color="lightblue",
        edge_color="black",
        node_size=800,
        font_size=10,
        ax=ax,
        linewidths=1.5,
    )


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
    _, ax = plt.subplots()

    render_hypergraph(hyper_graph, pos, ax)
    render_nx_graph(nx_graph, pos, ax)

    ax.margins(0.1)

    plt.tight_layout()
    plt.savefig(output)
    print(f"Overlay rendered to {output}")
