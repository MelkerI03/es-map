"""Command-line interface for the Elasticsearch Network Mapper.

This module orchestrates configuration, data ingestion, graph
construction, and rendering of a network topology visualization.
"""

from pathlib import Path

import networkx as nx
import typer
from dotenv import load_dotenv

from es_map.analysis.ingest import build_hosts
from es_map.analysis.models import SubnetRegistry
from es_map.config import (
    ConfigError,
    ElasticConfig,
    parse_subnets,
    validate_config,
)
from es_map.elastic.client import create_client
from es_map.graph.builder import apply_layout, build_nx_graph
from es_map.graph.export_graph import export_graph
from es_map.graph.web_renderer import render_web, serve_directory
from es_map.utils.logging import get_logger, setup_logging


env_path = Path.cwd() / ".env"
_ = load_dotenv(env_path) or load_dotenv()

app = typer.Typer(no_args_is_help=True, add_completion=False)
logger = get_logger(__name__)


@app.command()
def main(
    subnet_cidrs: list[str] = typer.Argument(
        ..., help="List of subnets in CIDR notation"
    ),
    elastic_host: str = typer.Option(
        "localhost",
        "--host",
        "-H",
        help="Elasticsearch host",
        envvar="ES_HOST",
    ),
    elastic_port: int = typer.Option(
        9200,
        "--port",
        "-p",
        help="Elasticsearch port",
        envvar="ES_PORT",
    ),
    username: str | None = typer.Option(
        None,
        "--username",
        "-u",
        help="Elasticsearch username",
        envvar="ES_USERNAME",
    ),
    password: str | None = typer.Option(
        None,
        "--password",
        "-P",
        help="Elasticsearch password",
        hide_input=True,
        envvar="ES_PASSWORD",
    ),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        "-k",
        help="Elasticsearch API key",
        hide_input=True,
        envvar="ES_API_KEY",
    ),
    index: str | None = typer.Option(
        None,
        "--index",
        "-i",
        help="Specific index to analyze",
        envvar="ES_INDEX",
    ),
    ssl_enabled: bool = typer.Option(
        False,
        "--ssl",
        "-s",
        help="Use HTTPS",
        envvar="ES_SSL",
    ),
    ca_cert: Path | None = typer.Option(
        None,
        "--ca-cert",
        help="Path to CA certificate bundle",
        exists=True,
        file_okay=True,
        dir_okay=False,
        envvar="ES_CA_CERT",
    ),
    client_cert: Path | None = typer.Option(
        None,
        "--client-cert",
        help="Path to client certificate (for mTLS)",
        exists=True,
        envvar="ES_CLIENT_CERT",
    ),
    client_key: Path | None = typer.Option(
        None,
        "--client-key",
        help="Path to client private key (for mTLS)",
        exists=True,
        envvar="ES_CLIENT_KEY",
    ),
    verify_ssl: bool = typer.Option(
        True,
        "--verify/--no-verify",
        help="Verify server certificate",
        envvar="ES_VERIFY",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        "-l",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
    log_file: Path | None = typer.Option(
        None,
        "--log-file",
        help="Optional log file path",
    ),
) -> None:
    """Elasticsearch Network Mapper CLI.

    This command-line interface connects to an Elasticsearch cluster,
    retrieves host data, builds a subnet hierarchy, and generates
    a visual network graph.

    Args:
        subnet_cidrs: List of CIDR subnet strings to analyze.
        elastic_host: Elasticsearch host address.
        elastic_port: Elasticsearch port.
        username: Optional Elasticsearch username.
        password: Optional Elasticsearch password.
        api_key: Optional Elasticsearch API key.
        index: Optional Elasticsearch index to query.
        ssl_enabled: Whether to use HTTPS.
        ca_cert: Path to CA certificate.
        client_cert: Path to client certificate.
        client_key: Path to client private key.
        verify_ssl: Whether to verify SSL certificates.
        log_level: Logging verbosity level.
        log_file: Optional log file path.
    """
    setup_logging(log_level=log_level, log_file=log_file)

    logger.info("Starting Elasticsearch Network Mapper")
    logger.debug("CLI arguments: %s", locals())
    logger.debug(
        "CLI arguments parsed",
        extra={
            "subnets": subnet_cidrs,
            "elastic_host": elastic_host,
            "port": elastic_port,
            "index": index,
            "use_ssl": ssl_enabled,
            "verify": verify_ssl,
            "log_level": log_level,
        },
    )

    try:
        parsed_subnets = parse_subnets(subnet_cidrs)
        logger.info("Parsed subnets", extra={"count": len(parsed_subnets)})
    except (ValueError, AssertionError) as e:
        logger.error("Invalid subnet input: %s", e)
        typer.secho(
            f"Fatal error: {e}. Run with --log-level DEBUG for details.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    elastic_config = ElasticConfig(
        host=elastic_host,
        port=elastic_port,
        subnets=parsed_subnets,
        index=index,
        username=username,
        password=password,
        api_key=api_key,
        use_ssl=ssl_enabled,
        ca_cert=ca_cert,
        client_cert=client_cert,
        client_key=client_key,
        verify=verify_ssl,
    )

    try:
        validate_config(elastic_config)
    except ConfigError as e:
        logger.warning("Configuration validation failed", extra={"error": str(e)})
        typer.secho(f"Configuration error: {e}", fg=typer.colors.RED)

    client = create_client(elastic_config)

    # --- Collect network data ---
    hosts = build_hosts(client, elastic_config.index)
    logger.info("Fetched hosts from Elasticsearch", extra={"count": len(hosts)})

    registry = SubnetRegistry(parsed_subnets)
    logger.info("Assigned hosts to subnet registry")

    for host in hosts:
        registry.assign_host_to_subnet(host)

    graph_data = export_graph(registry)
    graph = build_nx_graph(graph_data)
    layout = nx.spring_layout(graph, seed=42)

    apply_layout(graph_data, layout)

    # --- Render in browser ---
    out_dir = Path("./out")
    logger.info("Rendering network graph", extra={"output_dir": str(out_dir)})

    render_web(graph_data, out_dir)
    serve_directory(out_dir)

    # --- Finish ---
    logger.info("Finished successfully")


if __name__ == "__main__":
    app()
