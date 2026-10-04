import pytest
from unittest.mock import patch, MagicMock
import requests
from datanova_sdk import DataNovaClient, DataNovaAPIError

@pytest.fixture
def client():
    with DataNovaClient(api_key="test_key", base_url="https://datanova-fude.onrender.com") as c:
        yield c

def test_health(client):
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.content = b'{"status": "healthy"}'
    mock_resp.json.return_value = {"status": "healthy"}

    with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
        res = client.health()
        assert res == {"status": "healthy"}
        mock_req.assert_called_once_with(
            method="GET",
            url="https://datanova-fude.onrender.com/api/v1/health",
            json=None,
            files=None,
            timeout=client.timeout
        )

def test_list_datasets(client):
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.content = b'{"datasets": [{"id": 1, "name": "sales.csv"}]}'
    mock_resp.json.return_value = {"datasets": [{"id": 1, "name": "sales.csv"}]}

    with patch.object(client.session, "request", return_value=mock_resp):
        res = client.list_datasets()
        assert "datasets" in res
        assert len(res["datasets"]) == 1

def test_preview_dataset(client):
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.content = b'{"columns": ["age", "income"]}'
    mock_resp.json.return_value = {"columns": ["age", "income"]}

    with patch.object(client.session, "request", return_value=mock_resp):
        res = client.preview_dataset(dataset_id=42)
        assert res["columns"] == ["age", "income"]

def test_analytics_and_ml_endpoints(client):
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.content = b'{"success": true}'
    mock_resp.json.return_value = {"success": True}

    with patch.object(client.session, "request", return_value=mock_resp):
        assert client.run_eda(1, target_column="target")["success"] is True
        assert client.clean_dataset(1, strategies={"fill_missing": "mean"})["success"] is True
        assert client.generate_visualizations(1, chart_types=["histogram"])["success"] is True
        assert client.run_auto_analysis(1)["success"] is True
        assert client.get_analysis_report(10)["success"] is True
        assert client.get_analysis_code(10)["success"] is True
        assert client.ask_question("What is the average sales?", dataset_id=1)["success"] is True
        assert client.train_regression(1, target_column="price")["success"] is True
        assert client.train_classification(1, target_column="label")["success"] is True
        assert client.execute_pipeline(1, steps=[{"step": "clean"}])["success"] is True
        assert client.get_pipeline_status("task_abc123")["success"] is True
        assert client.generate_api_key("dev_key")["success"] is True
        assert client.revoke_api_key(5)["success"] is True

def test_json_decode_error_fallback(client):
    mock_resp = MagicMock()
    mock_resp.ok = False
    mock_resp.status_code = 502
    mock_resp.content = b'<html>Bad Gateway</html>'
    mock_resp.text = '<html>Bad Gateway</html>'
    mock_resp.json.side_effect = ValueError("Invalid JSON")

    with patch.object(client.session, "request", return_value=mock_resp):
        with pytest.raises(DataNovaAPIError) as exc_info:
            client.health()
        assert exc_info.value.status_code == 502
        assert "HTTP 502 Error" in str(exc_info.value)
        assert exc_info.value.payload == {"raw_response": "<html>Bad Gateway</html>"}

def test_api_error_raising(client):
    mock_resp = MagicMock()
    mock_resp.ok = False
    mock_resp.status_code = 400
    mock_resp.content = b'{"error": "Dataset not found"}'
    mock_resp.json.return_value = {"error": "Dataset not found"}

    with patch.object(client.session, "request", return_value=mock_resp):
        with pytest.raises(DataNovaAPIError) as exc_info:
            client.preview_dataset(999)
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == "Dataset not found"
        assert exc_info.value.payload == {"error": "Dataset not found"}

def test_network_exception_handling(client):
    with patch.object(client.session, "request", side_effect=requests.RequestException("Connection refused")):
        with pytest.raises(DataNovaAPIError) as exc_info:
            client.health()
        assert "Network error communicating with DataNova API" in str(exc_info.value)
