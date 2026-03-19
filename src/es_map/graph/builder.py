"""
These might not be needed in the future, with forces 'forcing'
nodes into good positions regardless
"""

import networkx as nx


def build_nx_graph(data: dict) -> nx.Graph:
    G = nx.Graph()

    for node in data["nodes"]:
        G.add_node(node["id"])

    for edge in data["edges"]:
        G.add_edge(edge["source"], edge["target"])

    return G


def apply_layout(data: dict, pos: dict, scale: float = 800) -> dict:
    for node in data["nodes"]:
        node_id = node["id"]

        if node_id in pos:
            x, y = pos[node_id]

            node["x"] = float(x) * scale
            node["y"] = float(y) * scale

    return data
