"""Configuration models and validation for the Elasticsearch Network Mapper.

This module defines the ElasticConfig data structure and provides
utilities for parsing and validating user-provided configuration inputs.
"""

import ipaddress
from dataclasses import dataclass
from pathlib import Path

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ElasticConfig:
    """Configuration for connecting to and querying Elasticsearch.

    Attributes:
        host: Elasticsearch host address.
        port: Elasticsearch port.
        subnets: List of IPv4 networks to analyze.
        index: Optional Elasticsearch index to query.
        username: Optional authentication username.
        password: Optional authentication password.
        api_key: Optional API key for authentication.
        use_ssl: Whether to use HTTPS.
        ca_cert: Path to CA certificate bundle.
        client_cert: Path to client certificate (mTLS).
        client_key: Path to client private key (mTLS).
        verify: Whether to verify SSL certificates.
    """

    host: str
    port: int
    subnets: list[ipaddress.IPv4Network]
    index: str | None = None
    username: str | None = None
    password: str | None = None
    api_key: str | None = None
    use_ssl: bool = False
    ca_cert: Path | None = None
    client_cert: Path | None = None
    client_key: Path | None = None
    verify: bool = True


class ConfigError(Exception):
    pass


def build_config(
    host,
    port,
    subnet_cidrs,
    index,
    username,
    password,
    api_key,
    ssl_enabled,
    ca_cert,
    client_cert,
    client_key,
    verify_ssl,
) -> ElasticConfig:

    parsed_subnets = parse_subnets(subnet_cidrs)
    logger.info("Parsed subnets", extra={"count": len(parsed_subnets)})
    elastic_config = ElasticConfig(
        host=host,
        port=port,
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

    return elastic_config


def parse_subnets(raw_subnets: list[str]) -> list[ipaddress.IPv4Network]:
    """Parse and validate a list of subnet strings.

    Each subnet is converted into an IPv4Network object. Invalid
    inputs raise a ConfigError.

    Args:
        raw_subnets: List of subnet strings in CIDR notation.

    Returns:
        A list of validated IPv4Network objects.

    Raises:
        ConfigError: If any subnet is invalid.
    """
    validated_subnets: list[ipaddress.IPv4Network] = []

    for subnet in raw_subnets:
        try:
            network = ipaddress.ip_network(subnet, strict=False)

            if not isinstance(network, ipaddress.IPv4Network):
                raise ConfigError(f"Invalid IPv4 CIDR format: {subnet}")

            validated_subnets.append(network)
        except (ValueError, AssertionError):
            logger.warning(
                "Invalid subnet encountered",
                extra={"subnet": subnet},
            )
            raise ConfigError(f"Invalid IPv4 CIDR format: {subnet}")

    return validated_subnets


def validate_config(config: ElasticConfig) -> None:
    """Validate an ElasticConfig instance.

    Ensures that authentication and TLS settings are consistent and
    mutually exclusive where required.

    Args:
        config: The configuration to validate.

    Raises:
        ConfigError: If the configuration is invalid.
    """
    logger.debug("Validating configuration")

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

    logger.debug(
        "Configuration validated successfully",
        extra={"host": config.host, "port": config.port},
    )
