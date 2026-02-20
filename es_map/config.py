from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ElasticConfig:
    host: str
    port: int
    index: Optional[str] = None
    output: Path = Path("out/network.gv")
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    use_ssl: bool = False
    ca_cert: Optional[Path] = None
    client_cert: Optional[Path] = None
    client_key: Optional[Path] = None
    verify: bool = True


def build_config(
    host: str,
    port: int,
    index: str,
    output: Path,
    username: Optional[str],
    password: Optional[str],
    api_key: Optional[str],
    use_ssl: bool,
    ca_cert: Optional[Path],
    client_cert: Optional[Path],
    client_key: Optional[Path],
    verify: bool,
) -> ElasticConfig:

    return ElasticConfig(
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


class ConfigError(Exception):
    pass


def validate_config(config: ElasticConfig) -> None:
    if config.api_key and (config.username or config.password):
        raise ConfigError("Cannot use API key together with username/password.")

    if (config.username and not config.password) or (
        config.password and not config.username
    ):
        raise ConfigError("Both username and password must be provided together.")

    if config.client_cert and not config.client_key:
        raise ConfigError("Client key must be provided when using client certificate.")

    if config.client_key and not config.client_cert:
        raise ConfigError("Client certificate must be provided with client key.")

    if not config.use_ssl and (
        config.ca_cert or config.client_cert or config.client_key
    ):
        raise ConfigError("TLS options require --ssl.")
