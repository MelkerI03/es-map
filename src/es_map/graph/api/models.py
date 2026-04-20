"""Pydantic models defining the Graph API schema.

This module defines the data structures used to represent a network graph,
including nodes, edges, subnets, and layout information.

These models serve as the contract between:
- the backend graph export logic
- the FastAPI API
- the frontend visualization layer (e.g., D3.js)

All models are designed to be JSON-serializable and suitable for API responses.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Node(BaseModel):
    """Represents a single node in the graph.

    Nodes correspond to either hosts or routers within the network.
    """

    id: str = Field(description="Unique identifier for the node")
    label: str = Field(description="Display label used in the UI")
    type: Literal["host", "router"] = Field(
        description="Type of node: either 'host' or 'router'"
    )

    ip_addresses: list[str] = Field(
        default_factory=list, description="IP addresses linked to node"
    )
    subnets: list[str] = Field(
        default_factory=list, description="Subnets that the node is part of"
    )

    connections: list[str] = Field(
        default_factory=list,
        description="List of hosts that this node has directly communicated with",
    )

    first_seen: str = Field(
        default_factory=str, description="First observation of node in logs (iso)"
    )
    last_seen: str = Field(
        default_factory=str, description="Last observation of node in logs (iso)"
    )


class Edge(BaseModel):
    """Represents a connection between two nodes in the graph.

    Edges define relationships such as:
    - host -> router connections
    - subnet -> parent subnet connections
    """

    source: str = Field(description="ID of the source node")
    target: str = Field(description="ID of the target node")


class Subnet(BaseModel):
    """Represents a subnet grouping within the graph.

    A subnet contains:
    - a router node
    - associated host nodes
    - nested child subnets (indirectly via member IDs)

    The `members` field includes all node IDs that belong to this subnet.
    """

    id: str = Field(description="Unique identifier for the subnet")
    label: str = Field(description="Human-readable subnet label (e.g., CIDR)")
    members: list[str] = Field(
        description="List of node IDs that belong to this subnet"
    )


class Graph(BaseModel):
    """Top-level graph structure used for API responses and rendering.

    This object contains all nodes, edges, subnet groupings, and layout
    information required to render the network visualization.
    """

    version: str = Field(
        default="1.3",
        description="Graph schema version for compatibility tracking",
    )

    nodes: list[Node] = Field(description="All nodes in the graph")
    edges: list[Edge] = Field(description="All edges connecting nodes")
    subnets: list[Subnet] = Field(description="Subnet groupings within the graph")
    layout: dict[str, list[float]] = Field(
        description="Mapping of node IDs to (x, y) positions for rendering"
    )
