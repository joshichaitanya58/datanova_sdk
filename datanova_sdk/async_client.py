"""
DataNova Python SDK - Async Client
Official asynchronous client for the DataNova Smart Analytics Platform REST API.
"""

import asyncio
import logging
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False

from .client import DataNovaAPIError, __version__

logger = logging.getLogger("datanova.async")

DatasetID = Union[int, str]


class AsyncDataNovaClient:
    """
    Asynchronous DataNova API client using httpx.

    API key can be supplied directly or through:

        DATANOVA_API_KEY

    Base URL can be supplied directly or through:

        DATANOVA_BASE_URL

    Example:
        async with AsyncDataNovaClient() as client:
            health = await client.health()
            print(health)
    """

    DEFAULT_BASE_URL = "https://datanova-fude.onrender.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[int, float] = 60,
        max_retries: int = 3,
        verify_ssl: bool = True,
        user_agent: Optional[str] = None,
    ):
        if not HTTPX_AVAILABLE:
            raise ImportError(
                "The 'httpx' library is required for AsyncDataNovaClient. "
                "Install it using: pip install 'datanova-sdk[async]'"
            )

        # Environment variable fallback
        api_key = api_key or os.getenv("DATANOVA_API_KEY")

        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError(
                "API key is required and cannot be empty. "
                "Pass api_key=... or set DATANOVA_API_KEY."
            )

        if timeout <= 0:
            raise ValueError("timeout must be greater than 0.")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        self.api_key = api_key.strip()

        self.base_url = (
            base_url
            or os.getenv("DATANOVA_BASE_URL")
            or self.DEFAULT_BASE_URL
        ).rstrip("/")

        self.timeout = float(timeout)
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": (
                user_agent
                or f"DataNova-Python-SDK-Async/{__version__}"
            ),
        }

        # httpx transport-level retries are mainly useful for connection
        # failures. Application-level retry behavior should remain limited
        # and predictable.
        transport = httpx.AsyncHTTPTransport(
            retries=max_retries
        )

        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=self.timeout,
            transport=transport,
            verify=self.verify_ssl,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """Close the underlying HTTPX client."""
        if not self.client.is_closed:
            await self.client.aclose()

    async def __aenter__(self) -> "AsyncDataNovaClient":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        await self.close()

    def __repr__(self) -> str:
        return (
            f"AsyncDataNovaClient("
            f"base_url={self.base_url!r}, "
            f"timeout={self.timeout!r})"
        )

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_id(
        value: DatasetID,
        name: str,
    ) -> DatasetID:
        if value is None:
            raise ValueError(f"{name} is required.")

        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{name} cannot be empty.")

        return value

    @staticmethod
    def _validate_text(
        value: str,
        name: str,
    ) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{name} is required and cannot be empty."
            )

        return value.strip()

    # ------------------------------------------------------------------
    # Core HTTP request
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> Dict[str, Any]:

        url = f"{self.base_url}/{path.lstrip('/')}"

        logger.debug(
            "DataNova async request: %s %s",
            method.upper(),
            url,
        )

        try:
            response = await self.client.request(
                method=method.upper(),
                url=url,
                json=json,
                files=files,
                params=params,
                headers=headers,
                timeout=timeout or self.timeout,
            )

        except httpx.HTTPError as exc:
            logger.error(
                "DataNova async network error: %s",
                exc,
            )

            raise DataNovaAPIError(
                f"Network error communicating with DataNova API: {exc}"
            ) from exc

        # --------------------------------------------------------------
        # Safe response parsing
        # --------------------------------------------------------------

        try:
            data: Any = (
                response.json()
                if response.content
                else {}
            )

        except ValueError:
            data = {
                "raw_response": response.text
            }

        # --------------------------------------------------------------
        # Request / correlation ID
        # --------------------------------------------------------------

        request_id = (
            response.headers.get("X-Request-ID")
            or response.headers.get("X-Correlation-ID")
        )

        # --------------------------------------------------------------
        # API error handling
        # --------------------------------------------------------------

        if not response.is_success:

            if isinstance(data, dict):
                error_message = (
                    data.get("error")
                    or data.get("message")
                    or data.get("detail")
                    or f"HTTP {response.status_code} Error"
                )

                payload = data

            else:
                error_message = (
                    f"HTTP {response.status_code} Error"
                )

                payload = {
                    "raw_response": data
                }

            logger.error(
                "DataNova API error [%s] %s: %s",
                response.status_code,
                method.upper(),
                error_message,
            )

            raise DataNovaAPIError(
                str(error_message),
                status_code=response.status_code,
                payload=payload,
                request_id=request_id,
            )

        # --------------------------------------------------------------
        # Normalize successful response
        # --------------------------------------------------------------

        if isinstance(data, dict):

            if request_id and "request_id" not in data:
                data = dict(data)
                data["request_id"] = request_id

            return data

        return {
            "data": data,
            **(
                {"request_id": request_id}
                if request_id
                else {}
            ),
        }

    # ------------------------------------------------------------------
    # 1. System & Health
    # ------------------------------------------------------------------

    async def health(self) -> Dict[str, Any]:
        """Check DataNova API health."""
        return await self._request(
            "GET",
            "/api/v1/health",
        )

    # ------------------------------------------------------------------
    # 2. Dataset Management
    # ------------------------------------------------------------------

    async def list_datasets(self) -> Dict[str, Any]:
        """List datasets available to the authenticated account."""
        return await self._request(
            "GET",
            "/api/v1/datasets",
        )

    async def upload_dataset(
        self,
        file_path: Union[str, os.PathLike],
    ) -> Dict[str, Any]:
        """
        Upload CSV, Excel, or tabular dataset.

        The file handle remains open only for the duration of the request.
        """

        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Dataset file not found: {path}"
            )

        mime_type = (
            mimetypes.guess_type(path.name)[0]
            or "application/octet-stream"
        )

        with path.open("rb") as file_handle:

            files = {
                "file": (
                    path.name,
                    file_handle,
                    mime_type,
                )
            }

            return await self._request(
                "POST",
                "/api/v1/datasets/upload",
                files=files,
            )

    async def preview_dataset(
        self,
        dataset_id: DatasetID,
    ) -> Dict[str, Any]:
        """Get dataset preview, schema and sample information."""

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        return await self._request(
            "GET",
            f"/api/v1/datasets/{dataset_id}/preview",
        )

    # ------------------------------------------------------------------
    # 3. Analytics & AI
    # ------------------------------------------------------------------

    async def run_eda(
        self,
        dataset_id: DatasetID,
        target_column: Optional[str] = None,
    ) -> Dict[str, Any]:

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        payload: Dict[str, Any] = {
            "dataset_id": dataset_id
        }

        if target_column is not None:
            payload["target_column"] = self._validate_text(
                target_column,
                "target_column",
            )

        return await self._request(
            "POST",
            "/api/v1/analysis/eda",
            json=payload,
        )

    async def clean_dataset(
        self,
        dataset_id: DatasetID,
        strategies: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        payload: Dict[str, Any] = {
            "dataset_id": dataset_id
        }

        if strategies is not None:

            if not isinstance(strategies, dict):
                raise TypeError(
                    "strategies must be a dictionary."
                )

            payload["strategies"] = strategies

        return await self._request(
            "POST",
            "/api/v1/analysis/clean",
            json=payload,
        )

    async def generate_visualizations(
        self,
        dataset_id: DatasetID,
        chart_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        payload: Dict[str, Any] = {
            "dataset_id": dataset_id
        }

        if chart_types is not None:

            if not isinstance(chart_types, list):
                raise TypeError(
                    "chart_types must be a list."
                )

            payload["chart_types"] = chart_types

        return await self._request(
            "POST",
            "/api/v1/analysis/visualizations",
            json=payload,
        )

    async def run_auto_analysis(
        self,
        dataset_id: DatasetID,
    ) -> Dict[str, Any]:

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        return await self._request(
            "POST",
            "/api/v1/analysis/auto",
            json={
                "dataset_id": dataset_id
            },
        )

    async def get_analysis_report(
        self,
        analysis_id: DatasetID,
    ) -> Dict[str, Any]:

        analysis_id = self._validate_id(
            analysis_id,
            "analysis_id",
        )

        return await self._request(
            "GET",
            f"/api/v1/analysis/{analysis_id}/report",
        )

    async def get_analysis_code(
        self,
        analysis_id: DatasetID,
    ) -> Dict[str, Any]:

        analysis_id = self._validate_id(
            analysis_id,
            "analysis_id",
        )

        return await self._request(
            "GET",
            f"/api/v1/analysis/{analysis_id}/code",
        )

    async def ask_question(
        self,
        query: str,
        dataset_id: Optional[DatasetID] = None,
    ) -> Dict[str, Any]:

        payload: Dict[str, Any] = {
            "query": self._validate_text(
                query,
                "query",
            )
        }

        if dataset_id is not None:
            payload["dataset_id"] = self._validate_id(
                dataset_id,
                "dataset_id",
            )

        return await self._request(
            "POST",
            "/api/v1/ask",
            json=payload,
        )

    # ------------------------------------------------------------------
    # 4. Machine Learning
    # ------------------------------------------------------------------

    async def train_regression(
        self,
        dataset_id: DatasetID,
        target_column: str,
    ) -> Dict[str, Any]:

        return await self._request(
            "POST",
            "/api/v1/ml/regression",
            json={
                "dataset_id": self._validate_id(
                    dataset_id,
                    "dataset_id",
                ),
                "target_column": self._validate_text(
                    target_column,
                    "target_column",
                ),
            },
        )

    async def train_classification(
        self,
        dataset_id: DatasetID,
        target_column: str,
    ) -> Dict[str, Any]:

        return await self._request(
            "POST",
            "/api/v1/ml/classification",
            json={
                "dataset_id": self._validate_id(
                    dataset_id,
                    "dataset_id",
                ),
                "target_column": self._validate_text(
                    target_column,
                    "target_column",
                ),
            },
        )

    # ------------------------------------------------------------------
    # 5. Async Pipelines
    # ------------------------------------------------------------------

    async def execute_pipeline(
        self,
        dataset_id: DatasetID,
        steps: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        if not isinstance(steps, list) or not steps:
            raise ValueError(
                "steps must be a non-empty list."
            )

        return await self._request(
            "POST",
            "/api/v1/pipeline/execute",
            json={
                "dataset_id": dataset_id,
                "steps": steps,
            },
        )

    async def get_pipeline_status(
        self,
        task_id: str,
    ) -> Dict[str, Any]:

        task_id = self._validate_text(
            task_id,
            "task_id",
        )

        return await self._request(
            "GET",
            f"/api/v1/pipeline/status/{task_id}",
        )

    async def wait_for_pipeline(
        self,
        task_id: str,
        *,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
        terminal_statuses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Poll a pipeline until it reaches a terminal state.

        Example:

            result = await client.wait_for_pipeline(
                task_id,
                poll_interval=2,
                timeout=300,
            )
        """

        task_id = self._validate_text(
            task_id,
            "task_id",
        )

        if poll_interval <= 0:
            raise ValueError(
                "poll_interval must be greater than 0."
            )

        if timeout <= 0:
            raise ValueError(
                "timeout must be greater than 0."
            )

        terminal_states = {
            status.lower()
            for status in (
                terminal_statuses
                or [
                    "completed",
                    "complete",
                    "success",
                    "succeeded",
                    "failed",
                    "error",
                    "cancelled",
                    "canceled",
                ]
            )
        }

        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        while True:

            result = await self.get_pipeline_status(
                task_id
            )

            status = next(
                (
                    str(result.get(key))
                    .strip()
                    .lower()
                    for key in (
                        "status",
                        "state",
                        "task_status",
                    )
                    if result.get(key) is not None
                ),
                "",
            )

            if status in terminal_states:
                return result

            if loop.time() >= deadline:
                raise TimeoutError(
                    f"Pipeline {task_id!r} did not finish "
                    f"within {timeout} seconds."
                )

            await asyncio.sleep(
                poll_interval
            )

    # ------------------------------------------------------------------
    # 6. High-Level Workflows
    # ------------------------------------------------------------------

    async def analyze_dataset(
        self,
        dataset_id: DatasetID,
        *,
        question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run automated analysis and optionally ask an AI question.
        """

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        result = await self.run_auto_analysis(
            dataset_id
        )

        if question is not None:

            result = dict(result)

            result["question"] = (
                await self.ask_question(
                    question,
                    dataset_id=dataset_id,
                )
            )

        return result

    async def upload_and_analyze(
        self,
        file_path: Union[str, os.PathLike],
        *,
        question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a dataset and immediately start automated analysis.
        """

        upload_result = await self.upload_dataset(
            file_path
        )

        dataset_id = (
            upload_result.get("dataset_id")
            or upload_result.get("id")
        )

        if dataset_id is None:
            raise DataNovaAPIError(
                "Upload succeeded but no dataset_id "
                "was returned by the API.",
                payload=upload_result,
            )

        analysis_result = await self.analyze_dataset(
            dataset_id,
            question=question,
        )

        return {
            "upload": upload_result,
            "analysis": analysis_result,
        }

    # ------------------------------------------------------------------
    # 7. Developer API Keys
    # ------------------------------------------------------------------

    async def generate_api_key(
        self,
        key_name: str,
        environment: str = "live",
        scopes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        payload: Dict[str, Any] = {
            "key_name": self._validate_text(
                key_name,
                "key_name",
            ),
            "environment": self._validate_text(
                environment,
                "environment",
            ),
        }

        if scopes is not None:

            if not isinstance(scopes, list):
                raise TypeError(
                    "scopes must be a list."
                )

            payload["scopes"] = scopes

        return await self._request(
            "POST",
            "/api/developer/api_key/generate",
            json=payload,
        )

    async def revoke_api_key(
        self,
        key_id: DatasetID,
    ) -> Dict[str, Any]:

        return await self._request(
            "POST",
            "/api/developer/api_key/revoke",
            json={
                "key_id": self._validate_id(
                    key_id,
                    "key_id",
                )
            },
        )
