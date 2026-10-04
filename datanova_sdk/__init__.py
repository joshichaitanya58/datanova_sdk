"""
DataNova Python SDK
Official client library for the DataNova Smart Analytics Platform REST API.

Provides synchronous and asynchronous clients for interacting with
the DataNova REST API.
"""

from .client import DataNovaAPIError, DataNovaClient, __version__

# Async client is an optional capability. The async_client module itself
# handles the optional httpx dependency.
try:
    from .async_client import AsyncDataNovaClient
except ImportError:  # pragma: no cover
    AsyncDataNovaClient = None

__all__ = [
    "DataNovaClient",
    "AsyncDataNovaClient",
    "DataNovaAPIError",
    "__version__",
]
