"""
DataNova Python SDK - Synchronous Client

Official Python client for the DataNova Smart Analytics Platform REST API.
"""

import logging
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger("datanova")


# =========================================================
# SDK VERSION
# =========================================================

__version__ = "1.1.1"


# =========================================================
# TYPES
# =========================================================

DatasetID = Union[int, str]
PathLike = Union[str, os.PathLike]


# =========================================================
# EXCEPTIONS
# =========================================================

class DataNovaAPIError(Exception):
    """
    Exception raised when the DataNova REST API returns an error.

    Attributes:
        status_code: HTTP status code, if available.
        payload: Parsed API error payload.
        request_id: Server request/correlation ID, if available.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        payload: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)

        self.status_code = status_code
        self.payload = payload or {}
        self.request_id = request_id


# =========================================================
# CLIENT
# =========================================================

class DataNovaClient:
    """
    DataNova Python SDK client.

    The client provides synchronous access to the DataNova
    Smart Analytics Platform REST API.

    API key can be supplied directly:

        client = DataNovaClient(
            api_key="dn_live_..."
        )

    Or through:

        DATANOVA_API_KEY

    Base URL can also be configured using:

        DATANOVA_BASE_URL

    Example:

        with DataNovaClient(api_key="dn_live_...") as client:
            health = client.health()
            print(health)
    """

    DEFAULT_BASE_URL = "https://datanova-fude.onrender.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[int, float] = 60,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        verify_ssl: bool = True,
        user_agent: Optional[str] = None,
    ):
        # -------------------------------------------------
        # API KEY
        # -------------------------------------------------

        api_key = api_key or os.getenv("DATANOVA_API_KEY")

        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError(
                "API key is required and cannot be empty. "
                "Pass api_key=... or set DATANOVA_API_KEY."
            )

        # -------------------------------------------------
        # VALIDATE CONFIGURATION
        # -------------------------------------------------

        if timeout <= 0:
            raise ValueError(
                "timeout must be greater than 0."
            )

        if max_retries < 0:
            raise ValueError(
                "max_retries cannot be negative."
            )

        if backoff_factor < 0:
            raise ValueError(
                "backoff_factor cannot be negative."
            )

        # -------------------------------------------------
        # CLIENT CONFIG
        # -------------------------------------------------

        self.api_key = api_key.strip()

        self.base_url = (
            base_url
            or os.getenv("DATANOVA_BASE_URL")
            or self.DEFAULT_BASE_URL
        ).rstrip("/")

        self.timeout = float(timeout)
        self.max_retries = int(max_retries)
        self.backoff_factor = float(backoff_factor)
        self.verify_ssl = verify_ssl

        # -------------------------------------------------
        # HTTP SESSION
        # -------------------------------------------------

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "X-API-Key": self.api_key,
                "Accept": "application/json",
                "User-Agent": (
                    user_agent
                    or f"DataNova-Python-SDK/{__version__}"
                ),
            }
        )

        # -------------------------------------------------
        # RETRY CONFIGURATION
        # -------------------------------------------------

        if self.max_retries > 0:

            retry_strategy = Retry(
                total=self.max_retries,
                connect=self.max_retries,
                read=self.max_retries,
                status=self.max_retries,
                backoff_factor=self.backoff_factor,
                status_forcelist=[
                    429,
                    502,
                    503,
                    504,
                ],
                allowed_methods=frozenset(
                    [
                        "GET",
                        "HEAD",
                        "OPTIONS",
                    ]
                ),
                respect_retry_after_header=True,
                raise_on_status=False,
            )

            adapter = HTTPAdapter(
                max_retries=retry_strategy
            )

            self.session.mount(
                "http://",
                adapter,
            )

            self.session.mount(
                "https://",
                adapter,
            )

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(self) -> "DataNovaClient":
        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return (
            f"DataNovaClient("
            f"base_url={self.base_url!r}, "
            f"timeout={self.timeout!r})"
        )

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def close(self) -> None:
        """Close the underlying HTTP session."""

        if self.session:
            self.session.close()

    # =====================================================
    # VALIDATION HELPERS
    # =====================================================

    @staticmethod
    def _validate_id(
        value: DatasetID,
        name: str,
    ) -> DatasetID:
        """Validate dataset/analysis/key identifiers."""

        if value is None:
            raise ValueError(
                f"{name} is required."
            )

        if isinstance(value, str) and not value.strip():
            raise ValueError(
                f"{name} cannot be empty."
            )

        return value

    @staticmethod
    def _validate_text(
        value: str,
        name: str,
    ) -> str:
        """Validate a required text parameter."""

        if not isinstance(value, str):
            raise TypeError(
                f"{name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{name} is required and cannot be empty."
            )

        return value.strip()

    # =====================================================
    # REQUEST HANDLER
    # =====================================================

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an HTTP request against the DataNova API.

        Handles:
        - JSON parsing
        - API errors
        - network errors
        - request IDs
        - non-JSON responses
        """

        url = f"{self.base_url}/{path.lstrip('/')}"

        logger.debug(
            "DataNova request: %s %s",
            method.upper(),
            url,
        )

        try:

            response = self.session.request(
                method=method.upper(),
                url=url,
                json=json,
                files=files,
                params=params,
                headers=headers,
                timeout=(
                    timeout
                    if timeout is not None
                    else self.timeout
                ),
                verify=self.verify_ssl,
            )

        except requests.RequestException as exc:

            logger.error(
                "DataNova network error: %s",
                exc,
            )

            raise DataNovaAPIError(
                f"Network error communicating with "
                f"DataNova API: {exc}"
            ) from exc

        # -------------------------------------------------
        # REQUEST ID
        # -------------------------------------------------

        request_id = (
            response.headers.get("X-Request-ID")
            or response.headers.get(
                "X-Correlation-ID"
            )
        )

        # -------------------------------------------------
        # RESPONSE PARSING
        # -------------------------------------------------

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

        # -------------------------------------------------
        # API ERROR
        # -------------------------------------------------

        if not response.ok:

            if isinstance(data, dict):

                error_message = (
                    data.get("error")
                    or data.get("message")
                    or data.get("detail")
                    or (
                        f"HTTP "
                        f"{response.status_code} "
                        f"Error"
                    )
                )

                payload = data

            else:

                error_message = (
                    f"HTTP "
                    f"{response.status_code} "
                    f"Error"
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

        # -------------------------------------------------
        # SUCCESS RESPONSE
        # -------------------------------------------------

        if isinstance(data, dict):

            if (
                request_id
                and "request_id" not in data
            ):
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

    # =====================================================
    # 1. SYSTEM & HEALTH
    # =====================================================

    def health(self) -> Dict[str, Any]:
        """Check DataNova API health."""

        return self._request(
            "GET",
            "/api/v1/health",
        )

    # =====================================================
    # 2. DATASETS
    # =====================================================

    def list_datasets(self) -> Dict[str, Any]:
        """List datasets for the authenticated account."""

        return self._request(
            "GET",
            "/api/v1/datasets",
        )

    def upload_dataset(
        self,
        file_path: PathLike,
    ) -> Dict[str, Any]:
        """
        Upload a CSV, Excel, or tabular dataset.

        Example:

            result = client.upload_dataset(
                "sales.csv"
            )
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

            return self._request(
                "POST",
                "/api/v1/datasets/upload",
                files=files,
            )

    def preview_dataset(
        self,
        dataset_id: DatasetID,
    ) -> Dict[str, Any]:
        """Get dataset schema, preview and summary data."""

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        return self._request(
            "GET",
            f"/api/v1/datasets/{dataset_id}/preview",
        )

    # =====================================================
    # 3. DATA ANALYTICS & AI
    # =====================================================

    def run_eda(
        self,
        dataset_id: DatasetID,
        target_column: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform Exploratory Data Analysis."""

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        payload: Dict[str, Any] = {
            "dataset_id": dataset_id
        }

        if target_column is not None:

            payload["target_column"] = (
                self._validate_text(
                    target_column,
                    "target_column",
                )
            )

        return self._request(
            "POST",
            "/api/v1/analysis/eda",
            json=payload,
        )

    def clean_dataset(
        self,
        dataset_id: DatasetID,
        strategies: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:
        """Apply DataNova data cleaning operations."""

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        payload: Dict[str, Any] = {
            "dataset_id": dataset_id
        }

        if strategies is not None:

            if not isinstance(
                strategies,
                dict,
            ):
                raise TypeError(
                    "strategies must be a dictionary."
                )

            payload["strategies"] = strategies

        return self._request(
            "POST",
            "/api/v1/analysis/clean",
            json=payload,
        )

    def generate_visualizations(
        self,
        dataset_id: DatasetID,
        chart_types: Optional[
            List[str]
        ] = None,
    ) -> Dict[str, Any]:
        """Generate charts and statistical visualizations."""

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        payload: Dict[str, Any] = {
            "dataset_id": dataset_id
        }

        if chart_types is not None:

            if not isinstance(
                chart_types,
                list,
            ):
                raise TypeError(
                    "chart_types must be a list."
                )

            payload["chart_types"] = chart_types

        return self._request(
            "POST",
            "/api/v1/analysis/visualizations",
            json=payload,
        )

    def run_auto_analysis(
        self,
        dataset_id: DatasetID,
    ) -> Dict[str, Any]:
        """Run complete automated DataNova analysis."""

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        return self._request(
            "POST",
            "/api/v1/analysis/auto",
            json={
                "dataset_id": dataset_id
            },
        )

    def get_analysis_report(
        self,
        analysis_id: DatasetID,
    ) -> Dict[str, Any]:
        """Fetch analysis report information."""

        analysis_id = self._validate_id(
            analysis_id,
            "analysis_id",
        )

        return self._request(
            "GET",
            f"/api/v1/analysis/"
            f"{analysis_id}/report",
        )

    def get_analysis_code(
        self,
        analysis_id: DatasetID,
    ) -> Dict[str, Any]:
        """Fetch generated analysis code."""

        analysis_id = self._validate_id(
            analysis_id,
            "analysis_id",
        )

        return self._request(
            "GET",
            f"/api/v1/analysis/"
            f"{analysis_id}/code",
        )

    def ask_question(
        self,
        query: str,
        dataset_id: Optional[DatasetID] = None,
    ) -> Dict[str, Any]:
        """Ask a natural-language AI question."""

        payload: Dict[str, Any] = {
            "query": self._validate_text(
                query,
                "query",
            )
        }

        if dataset_id is not None:

            payload["dataset_id"] = (
                self._validate_id(
                    dataset_id,
                    "dataset_id",
                )
            )

        return self._request(
            "POST",
            "/api/v1/ask",
            json=payload,
        )

    # =====================================================
    # 4. MACHINE LEARNING
    # =====================================================

    def train_regression(
        self,
        dataset_id: DatasetID,
        target_column: str,
    ) -> Dict[str, Any]:
        """Train and evaluate regression models."""

        return self._request(
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

    def train_classification(
        self,
        dataset_id: DatasetID,
        target_column: str,
    ) -> Dict[str, Any]:
        """Train and evaluate classification models."""

        return self._request(
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

    # =====================================================
    # 5. ASYNC PIPELINES
    # =====================================================

    def execute_pipeline(
        self,
        dataset_id: DatasetID,
        steps: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Dispatch an asynchronous pipeline job."""

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        if not isinstance(steps, list):
            raise TypeError(
                "steps must be a list."
            )

        if not steps:
            raise ValueError(
                "steps must be a non-empty list."
            )

        return self._request(
            "POST",
            "/api/v1/pipeline/execute",
            json={
                "dataset_id": dataset_id,
                "steps": steps,
            },
        )

    def get_pipeline_status(
        self,
        task_id: str,
    ) -> Dict[str, Any]:
        """Get the status of an asynchronous pipeline."""

        task_id = self._validate_text(
            task_id,
            "task_id",
        )

        return self._request(
            "GET",
            f"/api/v1/pipeline/status/{task_id}",
        )

    def wait_for_pipeline(
        self,
        task_id: str,
        *,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
        terminal_statuses: Optional[
            List[str]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Wait until a pipeline reaches a terminal state.

        Example:

            result = client.wait_for_pipeline(
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
            str(status).strip().lower()
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

        import time

        start_time = time.monotonic()

        while True:

            result = self.get_pipeline_status(
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

            if (
                time.monotonic() - start_time
                >= timeout
            ):
                raise TimeoutError(
                    f"Pipeline {task_id!r} did not "
                    f"finish within {timeout} seconds."
                )

            import time as _time

            _time.sleep(poll_interval)

    # =====================================================
    # 6. HIGH-LEVEL CONVENIENCE METHODS
    # =====================================================

    def analyze_dataset(
        self,
        dataset_id: DatasetID,
        *,
        question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run automated analysis and optionally ask
        an AI question about the dataset.

        This is a convenience method built from existing
        DataNova API endpoints.
        """

        dataset_id = self._validate_id(
            dataset_id,
            "dataset_id",
        )

        analysis_result = (
            self.run_auto_analysis(
                dataset_id
            )
        )

        if question is not None:

            analysis_result = dict(
                analysis_result
            )

            analysis_result["question"] = (
                self.ask_question(
                    question,
                    dataset_id=dataset_id,
                )
            )

        return analysis_result

    def upload_and_analyze(
        self,
        file_path: PathLike,
        *,
        question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a dataset and immediately run
        automated analysis.

        Example:

            result = client.upload_and_analyze(
                "sales.csv",
                question="What are the main trends?"
            )
        """

        upload_result = self.upload_dataset(
            file_path
        )

        dataset_id = (
            upload_result.get("dataset_id")
            or upload_result.get("id")
        )

        if dataset_id is None:

            raise DataNovaAPIError(
                "Upload succeeded but the API "
                "did not return a dataset_id.",
                payload=upload_result,
            )

        analysis_result = (
            self.analyze_dataset(
                dataset_id,
                question=question,
            )
        )

        return {
            "upload": upload_result,
            "analysis": analysis_result,
        }

    # =====================================================
    # 7. DEVELOPER & API KEY MANAGEMENT
    # =====================================================

    def generate_api_key(
        self,
        key_name: str,
        environment: str = "live",
        scopes: Optional[
            List[str]
        ] = None,
    ) -> Dict[str, Any]:
        """Generate a new DataNova developer API key."""

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

            if not isinstance(
                scopes,
                list,
            ):
                raise TypeError(
                    "scopes must be a list."
                )

            payload["scopes"] = scopes

        return self._request(
            "POST",
            "/api/developer/api_key/generate",
            json=payload,
        )

    def revoke_api_key(
        self,
        key_id: DatasetID,
    ) -> Dict[str, Any]:
        """Revoke an active DataNova API key."""

        return self._request(
            "POST",
            "/api/developer/api_key/revoke",
            json={
                "key_id": self._validate_id(
                    key_id,
                    "key_id",
                )
            },
        )
