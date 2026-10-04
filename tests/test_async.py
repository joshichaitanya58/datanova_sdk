import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datanova_sdk import AsyncDataNovaClient, DataNovaAPIError

def test_async_client_health():
    async def run():
        async with AsyncDataNovaClient(api_key="async_key_123") as client:
            mock_resp = MagicMock()
            mock_resp.is_success = True
            mock_resp.content = b'{"status": "ok"}'
            mock_resp.json.return_value = {"status": "ok"}

            with patch.object(client.client, "request", new_callable=AsyncMock, return_value=mock_resp):
                res = await client.health()
                assert res == {"status": "ok"}
    asyncio.run(run())

def test_async_client_upload_and_mime(tmp_path):
    async def run():
        csv_file = tmp_path / "sample.csv"
        csv_file.write_text("col1,col2\nval1,val2")

        async with AsyncDataNovaClient(api_key="async_key_123") as client:
            mock_resp = MagicMock()
            mock_resp.is_success = True
            mock_resp.content = b'{"dataset_id": "ds_async_01"}'
            mock_resp.json.return_value = {"dataset_id": "ds_async_01"}

            with patch.object(client.client, "request", new_callable=AsyncMock, return_value=mock_resp) as mock_req:
                res = await client.upload_dataset(str(csv_file))
                assert res["dataset_id"] == "ds_async_01"
                _, kwargs = mock_req.call_args
                assert kwargs["files"]["file"][0] == "sample.csv"
                assert kwargs["files"]["file"][2] in ["text/csv", "application/vnd.ms-excel", "text/x-csv"]
    asyncio.run(run())

def test_async_client_error_handling():
    async def run():
        async with AsyncDataNovaClient(api_key="async_key_123") as client:
            mock_resp = MagicMock()
            mock_resp.is_success = False
            mock_resp.status_code = 404
            mock_resp.content = b'{"error": "Not Found"}'
            mock_resp.json.return_value = {"error": "Not Found"}

            with patch.object(client.client, "request", new_callable=AsyncMock, return_value=mock_resp):
                with pytest.raises(DataNovaAPIError) as exc_info:
                    await client.preview_dataset(999)
                assert exc_info.value.status_code == 404
                assert "Not Found" in str(exc_info.value)
    asyncio.run(run())
