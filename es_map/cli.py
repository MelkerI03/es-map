from pathlib import Path
import typer
from dotenv import load_dotenv
from typing import Optional

from es_map.config import ConfigError, ElasticConfig, validate_config


load_dotenv(Path.cwd() / ".env")

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def main(
    host: str = typer.Option(
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
        Path("out/network.gv"),
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
):
    """
    Elasticsearch Network Mapper CLI
    """
    typer.echo("Generating Elasticsearch network map...")
    typer.echo(f"Host: {host}")
    typer.echo(f"Port: {port}")
    typer.echo(f"Index: {index}")
    typer.echo(f"Output file: {output}")
    typer.echo(f"Username: {username}")
    typer.echo(f"Password: {password}")
    typer.echo(f"Api_key: {api_key}")
    typer.echo(f"Use_SSL: {use_ssl}")
    typer.echo(f"CA cert: {ca_cert}")
    typer.echo(f"client cert: {client_cert}")
    typer.echo(f"Client key: {client_key}")
    typer.echo(f"Verification: {verify}")

    config = ElasticConfig(
        host=host,
        port=port,
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
        typer.secho(f"Configuration error: {e}", fg="red")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
