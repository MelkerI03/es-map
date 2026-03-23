"""Web rendering and serving utilities for graph visualization.

This module handles exporting graph data to static assets and
serving them via a lightweight local HTTP server for browser-based
visualization.
"""

import http.server
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

from es_map.utils.file_handling import copy_and_replace, prepare_output_dir
from es_map.utils.logging import get_logger
from es_map.utils.paths import get_root_path

logger = get_logger(__name__)


def start_web() -> None:
    """Prepare and serve the web-based graph visualization.

    This function:
    - Generates the required static assets for rendering
    - Starts a local HTTP server to host the visualization

    The served application can then fetch graph data from the API
    and render it in the browser.
    """
    out_dir = Path("./out")

    prepare_web_render(out_dir)
    serve_directory(out_dir)


def prepare_web_render(
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
    static_dir = root_path / "graph/render/static"
    templates_dir = root_path / "graph/render/templates"

    logger.debug("Copying static assets to output directory")

    prepare_output_dir(output_dir)
    copy_and_replace(static_dir, output_dir)
    print(f"copying from {static_dir} to {output_dir}")
    copy_and_replace(templates_dir / "index.html", output_dir / "index.html")

    icons_dir = output_dir / "icons"
    icons_dir.mkdir(exist_ok=True)
    images = get_root_path() / "icons"
    copy_and_replace(images / "cog.svg", icons_dir / "cog.svg")

    logger.debug(
        "Static assets copied",
        extra={"output_dir": str(output_dir)},
    )


def serve_directory(directory: Path, port: int = 8081) -> None:
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
