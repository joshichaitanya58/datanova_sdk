import os
import pytest
from unittest.mock import patch, MagicMock
from datanova_sdk import DataNovaClient

@pytest.fixture
def client():
    with DataNovaClient(api_key="test_key") as c:
        yield c

def test_upload_missing_file(client):
    with pytest.raises(FileNotFoundError, match="Dataset file not found"):
        client.upload_dataset("non_existent_file_xyz123.csv")

def test_upload_mime_type_guessing(client, tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b,c\n1,2,3")

    excel_file = tmp_path / "data.xlsx"
    excel_file.write_bytes(b"dummy excel content")

    unknown_file = tmp_path / "data.customext"
    unknown_file.write_text("custom content")

    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.content = b'{"dataset_id": "ds_101"}'
    mock_resp.json.return_value = {"dataset_id": "ds_101"}

    with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
        res_csv = client.upload_dataset(str(csv_file))
        assert res_csv["dataset_id"] == "ds_101"
        args, kwargs = mock_req.call_args
        files = kwargs["files"]
        assert files["file"][0] == "data.csv"
        assert files["file"][2] in ["text/csv", "application/vnd.ms-excel", "text/x-csv", "application/csv"]

    with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
        res_excel = client.upload_dataset(str(excel_file))
        assert res_excel["dataset_id"] == "ds_101"
        args, kwargs = mock_req.call_args
        files = kwargs["files"]
        assert files["file"][0] == "data.xlsx"
        assert files["file"][2] in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/octet-stream", "application/vnd.ms-excel"]

    with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
        client.upload_dataset(str(unknown_file))
        args, kwargs = mock_req.call_args
        files = kwargs["files"]
        assert files["file"][2] == "application/octet-stream"
