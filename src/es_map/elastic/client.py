"""Elasticsearch client utilities.

The client is constructed as a thin wrapper around the official
Elasticsearch Python client, translating configuration values into
client initialization parameters.
"""

from elasticsearch import Elasticsearch

from es_map.config import ElasticConfig
from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def create_client(config: ElasticConfig) -> Elasticsearch:
    """Create an Elasticsearch client from the given configuration.

    Supports HTTP/HTTPS, certificate verification, custom CA bundles,
    mutual TLS (mTLS), API key authentication, and basic authentication.

    Args:
        config: Connection and authentication settings.

    Returns:
        A configured Elasticsearch client instance.

    Raises:
        ValueError: If the configuration is invalid or unsupported.
    """
    scheme = "https" if config.use_ssl else "http"

    logger.info(
        "Creating Elasticsearch client",
        extra={
            "host": config.host,
            "port": config.port,
            "scheme": scheme,
        },
    )

    if config.api_key:
        logger.debug("Using API key authentication")
    elif config.username and config.password:
        logger.debug("Using basic authentication")
    else:
        logger.debug("No authentication configured")

    if config.use_ssl:
        logger.debug(
            "TLS enabled",
            extra={
                "verify": config.verify,
                "ca_cert": bool(config.ca_cert),
                "client_cert": bool(config.client_cert),
                "client_key": bool(config.client_key),
            },
        )

    kwargs: dict = {
        "hosts": [
            {
                "host": config.host,
                "port": config.port,
                "scheme": scheme,
            }
        ],
        "verify_certs": config.verify,
    }

    if config.index:
        kwargs["index"] = config.index

    if config.ca_cert:
        kwargs["ca_certs"] = str(config.ca_cert)

    if config.client_cert:
        kwargs["client_cert"] = str(config.client_cert)

    if config.client_key:
        kwargs["client_key"] = str(config.client_key)

    if config.api_key:
        kwargs["api_key"] = config.api_key
    elif config.username and config.password:
        kwargs["basic_auth"] = (config.username, config.password)

    client = Elasticsearch(**kwargs)

    return client
