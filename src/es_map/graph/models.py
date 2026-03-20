"""TODO: Module Docstring

This is a module
"""

from typing import Literal
from pydantic import BaseModel, Field


class Node(BaseModel):
    """Todo: Write docstring"""

    id: str
    label: str
    type: Literal["host", "router"]


class Edge(BaseModel):
    """Todo: Write docstring"""

    source: str
    target: str


class Subnet(BaseModel):
    """Todo: Write docstring"""

    id: str
    label: str
    members: list[str]


class Graph(BaseModel):
    """Todo: Write docstring"""

    version: str = Field(default="1.0")

    nodes: list[Node]
    edges: list[Edge]
    subnets: list[Subnet]
