"""Web rendering and serving utilities for graph visualization.

This module handles exporting graph data to static assets and
serving them via a lightweight local HTTP server for browser-based
visualization.
"""

import http.server
import json
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

import networkx as nx

from es_map.utils.file_handling import copy_and_replace
from es_map.utils.logging import get_logger
from es_map.utils.paths import get_root_path

logger = get_logger(__name__)


def init_positioning(output_dir: Path, scale: int = 800) -> None:
    """
    Compute node positions using NetworkX spring layout.

    Args:
        output_dir (Path): Path where webserver will be hosted.

    Returns:
        Dict[str, Tuple[float, float]]: Mapping of node_id -> (x, y)
    """
    api_json = output_dir / "graph.json"
    data = json.loads(api_json.read_text(encoding="utf-8"))

    G = nx.Graph()

    for node in data.get("nodes", []):
        G.add_node(node["id"])

    for edge in data.get("edges", []):
        G.add_edge(edge["source"], edge["target"])

    pos = nx.spring_layout(G, seed=42)

    layout = {
        node_id: (float(x * scale), float(y * scale)) for node_id, (x, y) in pos.items()
    }

    with open(output_dir / "layout.json", "w") as f:
        json.dump(layout, f)


def render_web(
    output_dir: Path,
) -> None:
    """Render the network graph as a static web visualization.

    This function:
        Copies required static assets (JS, HTML) into the output directory

    Args:
        output_dir: Directory where web assets will be written.

    Raises:
        OSError: If file operations fail.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("Ensured output directory exists", extra={"path": str(output_dir)})

    root_path = get_root_path()
    static_dir = root_path / "graph/static"
    templates_dir = root_path / "graph/templates"

    logger.debug("Copying static assets to output directory")

    copy_and_replace(static_dir / "d3.v7.min.js", output_dir / "d3.v7.min.js")
    copy_and_replace(static_dir / "graph.js", output_dir / "graph.js")
    copy_and_replace(templates_dir / "index.html", output_dir / "index.html")

    logger.debug(
        "Static assets copied",
        extra={"output_dir": str(output_dir)},
    )


def serve_directory(directory: Path, port: int = 8000) -> None:
    """Serve a directory over HTTP and open it in the default browser.

    Starts a local HTTP server in a background thread and blocks
    until the user terminates the process.

    Args:
        directory: Directory to serve.
        port: Port to bind the server to.
    """

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

    # Skip TIME_WAIT on TCP close
    class ReuseAddrTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    logger.info(
        "Starting HTTP server",
        extra={"directory": str(directory), "port": port},
    )

    server = ReuseAddrTCPServer(("localhost", port), Handler)

    def run_server():
        server.serve_forever()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    webbrowser.open(f"http://localhost:{port}")

    logger.info("Opened browser", extra={"url": f"http://localhost:{port}"})

    try:
        input("Press ENTER to stop the server...\n")
    finally:
        logger.info("Shutting down HTTP server")
        server.shutdown()
        server.server_close()
        sys.exit(0)
