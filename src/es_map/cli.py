"""Command-line interface for the Elasticsearch Network Mapper.

This module orchestrates configuration, data ingestion, graph
construction, and rendering of a network topology visualization.
"""

from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv

from es_map.analysis.ingest import build_graph
from es_map.api.app import start_api
from es_map.config import build_config
from es_map.elastic.client import create_client
from es_map.graph.render.web_renderer import start_web
from es_map.utils.logging import get_logger, setup_logging

env_path = Path.cwd() / ".env"
_ = load_dotenv(env_path) or load_dotenv()
logger = get_logger(__name__)

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def main(
    subnet_cidrs: Annotated[
        list[str], typer.Argument(help="List of subnets in CIDR notation")
    ],
    elastic_host: Annotated[
        str | None,
        typer.Option("--host", "-H", help="Elasticsearch host", envvar="ES_HOST"),
    ] = None,
    elastic_port: Annotated[
        int | None,
        typer.Option(
            "--port",
            "-p",
            help="Elasticsearch port",
            envvar="ES_PORT",
        ),
    ] = None,
    username: Annotated[
        str | None,
        typer.Option(
            "--username",
            "-u",
            help="Elasticsearch username",
            envvar="ES_USERNAME",
        ),
    ] = None,
    password: Annotated[
        str | None,
        typer.Option(
            "--password",
            "-P",
            help="Elasticsearch password",
            hide_input=True,
            envvar="ES_PASSWORD",
        ),
    ] = None,
    api_key: Annotated[
        str | None,
        typer.Option(
            "--api-key",
            "-k",
            help="Elasticsearch API key",
            hide_input=True,
            envvar="ES_API_KEY",
        ),
    ] = None,
    ssl_enabled: Annotated[
        bool,
        typer.Option(
            "--ssl",
            "-s",
            help="Use HTTPS",
            envvar="ES_SSL",
        ),
    ] = False,
    ca_cert: Annotated[
        Path | None,
        typer.Option(
            "--ca-cert",
            help="Path to CA certificate bundle",
            exists=True,
            file_okay=True,
            dir_okay=False,
            envvar="ES_CA_CERT",
        ),
    ] = None,
    client_cert: Annotated[
        Path | None,
        typer.Option(
            "--client-cert",
            help="Path to client certificate (for mTLS)",
            exists=True,
            envvar="ES_CLIENT_CERT",
        ),
    ] = None,
    client_key: Annotated[
        Path | None,
        typer.Option(
            "--client-key",
            help="Path to client private key (for mTLS)",
            exists=True,
            envvar="ES_CLIENT_KEY",
        ),
    ] = None,
    verify_ssl: Annotated[
        bool,
        typer.Option(
            "--verify/--no-verify",
            help="Verify server certificate",
            envvar="ES_VERIFY",
        ),
    ] = True,
    input_file: Annotated[
        Path | None,
        typer.Option(
            "--input",
            "-f",
            help="Path to Elasticsearch export JSON/NDJSON file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    index: Annotated[
        str | None,
        typer.Option(
            "--index",
            "-i",
            help="Specific index to analyze",
            envvar="ES_INDEX",
        ),
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            "-l",
            help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        ),
    ] = "INFO",
    log_file: Annotated[
        Path | None,
        typer.Option(
            "--log-file",
            help="Optional log file path",
        ),
    ] = None,
) -> None:
    """Elasticsearch Network Mapper CLI.

    This command-line interface connects to an Elasticsearch cluster,
    retrieves host data, builds a subnet hierarchy, and generates
    a visual network graph.
    """
    setup_logging(log_level=log_level, log_file=log_file)

    logger.info("Starting Elasticsearch Network Mapper")
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

    client = None
    if input_file is None:
        elastic_config = build_config(
            host=elastic_host,
            port=elastic_port,
            subnet_cidrs=subnet_cidrs,
            username=username,
            password=password,
            api_key=api_key,
            ssl_enabled=ssl_enabled,
            ca_cert=ca_cert,
            client_cert=client_cert,
            client_key=client_key,
            verify_ssl=verify_ssl,
        )
        client = create_client(elastic_config)

    if not index:
        index = "*"

    graph = build_graph(
        client=client, input_file=input_file, index_name=index, subnets=subnet_cidrs
    )

    start_api(graph)

    start_web()

    logger.info("Finished successfully")
    typer.Exit()


if __name__ == "__main__":
    app()
