"""Graph construction and layout utilities.

This module provides helper functions for building NetworkX graphs
from structured data and applying layout coordinates to nodes for
visualization purposes.
"""

import networkx as nx

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def build_nx_graph(graph_data: dict) -> nx.Graph:
    """Build a NetworkX graph from structured node and edge data.

    Args:
        graph_data: Dictionary containing:
            - "nodes": List of node dictionaries with an "id" field.
            - "edges": List of edge dictionaries with "source" and "target".

    Returns:
        A NetworkX Graph containing the nodes and edges.
    """
    logger.debug(
        "Building NetworkX graph",
        extra={
            "node_count": len(graph_data.get("nodes", [])),
            "edge_count": len(graph_data.get("edges", [])),
        },
    )

    graph = nx.Graph()

    for node in graph_data["nodes"]:
        graph.add_node(node["id"])

    for edge in graph_data["edges"]:
        graph.add_edge(edge["source"], edge["target"])

    return graph


def apply_layout(graph_data: dict, pos: dict, scale: float = 800):
    """Apply layout positions to graph nodes in-place.

    Updates node dictionaries in-place with x and y
    coordinates based on layout positions.

    Args:
        graph_data: Dictionary containing node data.
        pos: Mapping of node IDs to (x, y) layout coordinates.
        scale: Scaling factor applied to layout coordinates.
    """
    logger.debug(
        "Applying layout to nodes",
        extra={
            "node_count": len(graph_data.get("nodes", [])),
            "positions_provided": len(pos),
            "scale": scale,
        },
    )

    nodes = graph_data.get("nodes")
    if nodes is None:
        return graph_data

    for node in nodes:
        node_id = node["id"]

        if node_id in pos:
            x, y = pos[node_id]

            node["x"] = float(x) * scale
            node["y"] = float(y) * scale
        else:
            logger.debug(
                "No layout position for node",
                extra={"node_id": node_id},
            )
