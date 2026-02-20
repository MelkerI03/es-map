from typing import Any
from elasticsearch import Elasticsearch
from es_map.config import ElasticConfig


def create_client(config: ElasticConfig) -> Elasticsearch:
    """Create an Elasticsearch client from the given configuration.

    Supports HTTP/HTTPS, optional certificate verification, custom CA
    bundles, mutual TLS, API key authentication, and basic authentication.

    Args:
        config (ElasticConfig): Connection and authentication settings.

    Returns:
        Elasticsearch: Configured client instance.
    """
    scheme = "https" if config.use_ssl else "http"

    kwargs: dict[str, Any] = {
        "hosts": [
            {
                "host": config.host,
                "port": config.port,
                "scheme": scheme,
            }
        ],
        "verify_certs": config.verify,
    }

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
