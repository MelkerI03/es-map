"""FastAPI application setup and lifecycle management.

This module provides utilities to:
- Create a FastAPI application exposing the graph API
- Start the API server in a separate process using Uvicorn

The API exposes the graph data via HTTP endpoints and is intended
to be consumed by frontend visualization clients.
"""

from multiprocessing import Process

import uvicorn
from fastapi import FastAPI

from es_map.graph.api.models import Graph


def start_api(graph):
    """Initialize and start the API server for a given graph.

    This function creates a FastAPI application instance and launches
    it in a separate process.

    Args:
        graph: Graph data to be served by the API.
    """
    app = create_app(graph)
    run_api(app)


def create_app(graph: Graph) -> FastAPI:
    """Create a FastAPI application instance with graph endpoints.

    The graph object is stored in the application's state and exposed
    via the `/graph` endpoint.

    Args:
        graph: Graph object to serve via the API.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    app = FastAPI()

    app.state.graph = graph

    @app.get("/graph", response_model=Graph)
    def get_graph() -> Graph:
        """Retrieve the current graph.

        Returns:
            Graph: The graph data stored in the application state.
        """
        return app.state.graph

    return app


def run_api(app, host="127.0.0.1", port=8000) -> Process:
    """Run a FastAPI application in a separate process using Uvicorn.

    This allows the API server to run concurrently with other parts
    of the application (e.g., CLI execution or rendering logic).

    Args:
        app: FastAPI application instance to run.
        host: Host address to bind the server to.
        port: Port number for the server.

    Returns:
        Process: The spawned process running the API server.
    """
    proc = Process(
        target=uvicorn.run,
        args=(app,),
        kwargs={
            "host": host,
            "port": port,
            "log_level": "info",
        },
        daemon=True,
    )

    proc.start()
    return proc
