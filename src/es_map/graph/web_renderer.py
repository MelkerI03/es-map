import http.server
import json
from pathlib import Path
import socketserver
import sys
import threading
from typing import Any, Dict, List
import webbrowser

from es_map.utils.file_handling import overwrite_copy
from es_map.utils.paths import get_root_path
from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def render_web(
    network_data: Dict[str, List[Dict[str, Any]]],
    output_dir: Path,
) -> None:
    """Render the subnet graph as a local web visualization.

    This function:
        1. Exports the data into graph.json
        2. Copies static assets into the output directory

    Args:
        network_data (dict): Source of truth for the network graph.
        output_dir (Path): Directory where web assets will be written.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "graph.json").write_text(
        json.dumps(network_data, indent=2), encoding="utf-8"
    )

    root_path = get_root_path()
    static_dir = root_path / "graph/static"
    templates_dir = root_path / "graph/templates"

    overwrite_copy(static_dir / "d3.v7.min.js", output_dir / "d3.v7.min.js")
    overwrite_copy(static_dir / "graph.js", output_dir / "graph.js")
    overwrite_copy(templates_dir / "index.html", output_dir / "index.html")


def serve_directory(directory: Path, port: int = 8000) -> None:
    """Serve a directory over HTTP and open it in the default browser.

    Args:
        directory (Path): Directory to serve.
        port (int): Port to bind the server to.
    """

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

    # Skip TIME_WAIT on TCP close
    class ReuseAddrTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = ReuseAddrTCPServer(("localhost", port), Handler)

    def run_server():
        httpd.serve_forever()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    webbrowser.open(f"http://localhost:{port}")

    try:
        input("Press ENTER to stop the server...\n")
    finally:
        httpd.shutdown()
        httpd.server_close()
        sys.exit(0)
