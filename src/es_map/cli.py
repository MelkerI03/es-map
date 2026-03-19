from pathlib import Path
import networkx as nx
import typer
from dotenv import load_dotenv
from typing import List, Optional

from es_map.analysis.ingest import build_hosts_from_es
from es_map.analysis.models import SubnetRegistry
from es_map.config import (
    ConfigError,
    ElasticConfig,
    parse_and_validate_subnets,
    validate_config,
)
from es_map.elastic.client import create_client

from es_map.graph.builder import apply_layout, build_nx_graph
from es_map.graph.export_graph import export_graph
from es_map.graph.web_renderer import render_web, serve_directory
from es_map.utils.logging import get_logger, setup_logging


if not load_dotenv(Path.cwd() / ".env"):
    load_dotenv()

app = typer.Typer(no_args_is_help=True, add_completion=False)
logger = get_logger(__name__)


@app.command()
def main(
    subnets: List[str] = typer.Argument(..., help="List of subnets in CIDR notation"),
    elastic_host: str = typer.Option(
        "localhost",
        "--host",
        "-H",
        help="Elasticsearch host",
        envvar="ES_HOST",
    ),
    port: int = typer.Option(
        9200,
        "--port",
        "-p",
        help="Elasticsearch port",
        envvar="ES_PORT",
    ),
    username: Optional[str] = typer.Option(
        None,
        "--username",
        "-u",
        help="Elasticsearch username",
        envvar="ES_USERNAME",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-P",
        help="Elasticsearch password",
        hide_input=True,
        envvar="ES_PASSWORD",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="Elasticsearch API key",
        hide_input=True,
        envvar="ES_API_KEY",
    ),
    output: Path = typer.Option(
        Path("out/network.svg"),
        "--output",
        "-o",
        help="Output file name",
        envvar="ES_OUT_DIR",
    ),
    index: Optional[str] = typer.Option(
        None,
        "--index",
        "-i",
        help="Specific index to analyze",
        envvar="ES_INDEX",
    ),
    use_ssl: bool = typer.Option(
        False,
        "--ssl",
        "-s",
        help="Use HTTPS",
        envvar="ES_SSL",
    ),
    ca_cert: Optional[Path] = typer.Option(
        None,
        "--ca-cert",
        help="Path to CA certificate bundle",
        exists=True,
        file_okay=True,
        dir_okay=False,
        envvar="ES_CA_CERT",
    ),
    client_cert: Optional[Path] = typer.Option(
        None,
        "--client-cert",
        help="Path to client certificate (for mTLS)",
        exists=True,
        envvar="ES_CLIENT_CERT",
    ),
    client_key: Optional[Path] = typer.Option(
        None,
        "--client-key",
        help="Path to client private key (for mTLS)",
        exists=True,
        envvar="ES_CLIENT_KEY",
    ),
    verify: bool = typer.Option(
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
    log_file: Optional[Path] = typer.Option(
        None,
        "--log-file",
        help="Optional log file path",
    ),
) -> None:
    """
    Elasticsearch Network Mapper CLI
    """
    setup_logging(log_level=log_level, log_file=log_file)

    logger.info("Starting Elasticsearch Network Mapper")
    logger.debug("CLI arguments: %s", locals())

    try:
        parsed_subnets = parse_and_validate_subnets(subnets)
    except (ValueError, AssertionError) as e:
        print(e)
        logger.critical("Invalid IPv4 CIDR format: {subnet}")
        typer.secho(
            f"Fatal error: {e}. Run with --log-level DEBUG for details.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    config = ElasticConfig(
        host=elastic_host,
        port=port,
        subnets=parsed_subnets,
        index=index,
        output=output,
        username=username,
        password=password,
        api_key=api_key,
        use_ssl=use_ssl,
        ca_cert=ca_cert,
        client_cert=client_cert,
        client_key=client_key,
        verify=verify,
    )

    try:
        validate_config(config)
    except ConfigError as e:
        logger.warning("Configuration validation failed: %s", e)
        typer.secho(f"Configuration error: {e}", fg=typer.colors.RED)

    try:
        client = create_client(config)
    except Exception as e:
        logger.critical(f"Fatal error while creating client: {e}", exc_info=False)
        typer.secho(
            f"Fatal error: {e}. Run with --log-level DEBUG for details.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    # --- Collect network data ---
    hosts = build_hosts_from_es(client, config.index)

    registry = SubnetRegistry(parsed_subnets)

    for host in hosts:
        registry.attach_host(host)

    data = export_graph(registry)
    G = build_nx_graph(data)
    layout = nx.spring_layout(G, seed=42)

    network_data = apply_layout(data, layout)

    # --- Render in browser ---
    out_dir = Path("./out")

    render_web(network_data, out_dir)
    serve_directory(out_dir)

    # --- Finish ---
    logger.info("Finished successfully")


if __name__ == "__main__":
    app()
