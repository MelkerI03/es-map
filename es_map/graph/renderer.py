from pathlib import Path
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph


def render_graph(graph: nx.Graph, output: Path) -> None:
    """
    Render a NetworkX graph using Graphviz and save it to a file.
    """
    # Convert NetworkX graph to PyGraphviz AGraph
    agraph = to_agraph(graph)

    # Set default node attributes (applies to all nodes initially)
    agraph.node_attr.update(
        {
            "shape": "ellipse",
            "style": "filled",
            "fillcolor": "lightgreen",
            "fontsize": "10",
        }
    )

    # Override router nodes
    for node, data in graph.nodes(data=True):
        n = agraph.get_node(node)
        if data.get("type") == "router":
            n.attr.update(  # pyright: ignore[reportAttributeAccessIssue]
                {
                    "shape": "box",
                    "fillcolor": "lightblue",
                    "style": "filled",
                    "fontsize": "10",
                }
            )

    agraph.edge_attr.update(
        {
            "color": "gray",
            "penwidth": "1.2",
        }
    )

    # Layout and render
    agraph.layout(prog="dot")
    agraph.draw(str(output))

    print(f"Graph rendered to {output}")
