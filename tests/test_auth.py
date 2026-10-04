import pytest
from datanova_sdk import DataNovaClient, AsyncDataNovaClient

def test_client_api_key_required():
    with pytest.raises(ValueError, match="API key is required"):
        DataNovaClient(api_key="")

    with pytest.raises(ValueError, match="API key is required"):
        DataNovaClient(api_key="   ")

    with pytest.raises(ValueError, match="API key is required"):
        DataNovaClient(api_key=None)

def test_async_client_api_key_required():
    with pytest.raises(ValueError, match="API key is required"):
        AsyncDataNovaClient(api_key="")

def test_client_headers_and_config():
    client = DataNovaClient(api_key="test_key_123", base_url="https://datanova-fude.onrender.com", timeout=30)
    assert client.base_url == "https://datanova-fude.onrender.com"
    assert client.timeout == 30
    assert client.session.headers["Authorization"] == "Bearer test_key_123"
    assert client.session.headers["X-API-Key"] == "test_key_123"
    assert "DataNova-Python-SDK/1.0.0" in client.session.headers["User-Agent"]
    client.close()
