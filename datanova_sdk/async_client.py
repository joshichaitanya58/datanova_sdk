import os
import mimetypes
import logging
from typing import Dict, Any, Optional, List, Union

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from .client import DataNovaAPIError, __version__

logger = logging.getLogger("datanova.async")

class AsyncDataNovaClient:
    """
    Asynchronous DataNova Python SDK Client using `httpx`.
    
    Example usage:
        async with AsyncDataNovaClient(api_key="dn_live_...", base_url="https://datanova-fude.onrender.com") as client:
            health = await client.health()
            datasets = await client.list_datasets()
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://datanova-fude.onrender.com",
        timeout: int = 60,
        max_retries: int = 3
    ):
        if not HTTPX_AVAILABLE:
            raise ImportError(
                "The 'httpx' library is required for AsyncDataNovaClient. "
                "Install it using `pip install datanova-sdk[async]` or `pip install httpx`."
            )

        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("API key is required and cannot be empty")

        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            "User-Agent": f"DataNova-Python-SDK-Async/{__version__}"
        }
        
        transport = httpx.AsyncHTTPTransport(retries=max_retries)
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=float(timeout),
            transport=transport
        )

    async def close(self) -> None:
        """Close the underlying HTTPX AsyncClient session."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        logger.debug("Executing async API request: %s %s", method, url)
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=json,
                files=files
            )
            
            # Safe JSON parsing with fallback
            try:
                data = response.json() if response.content else {}
            except (ValueError, Exception):
                data = {"raw_response": response.text}

            if not response.is_success:
                error_msg = data.get("error", f"HTTP {response.status_code} Error") if isinstance(data, dict) else f"HTTP {response.status_code} Error"
                logger.error("Async API error [%s]: %s (Status Code: %s)", method, error_msg, response.status_code)
                raise DataNovaAPIError(error_msg, status_code=response.status_code, payload=data if isinstance(data, dict) else {"raw_response": data})

            return data
        except httpx.HTTPError as exc:
            logger.error("Async network communication error with DataNova API: %s", str(exc))
            raise DataNovaAPIError(f"Network error communicating with DataNova API: {str(exc)}") from exc

    # ------------------------------------------------------------------
    # 1. System & Health
    # ------------------------------------------------------------------
    async def health(self) -> Dict[str, Any]:
        """Check system health, status, and API telemetry active status."""
        return await self._request("GET", "/api/v1/health")

    # ------------------------------------------------------------------
    # 2. Datasets
    # ------------------------------------------------------------------
    async def list_datasets(self) -> Dict[str, Any]:
        """List all datasets available for the authenticated user/account."""
        return await self._request("GET", "/api/v1/datasets")

    async def upload_dataset(self, file_path: str) -> Dict[str, Any]:
        """Upload a CSV, Excel, or tabular dataset file to DataNova."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found at path: {file_path}")
        
        filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"

        with open(file_path, "rb") as f:
            files = {"file": (filename, f, mime_type)}
            return await self._request("POST", "/api/v1/datasets/upload", files=files)

    async def preview_dataset(self, dataset_id: Union[int, str]) -> Dict[str, Any]:
        """Get column schema, sample rows, and summary metrics for a dataset."""
        return await self._request("GET", f"/api/v1/datasets/{dataset_id}/preview")

    # ------------------------------------------------------------------
    # 3. Data Analytics & AI
    # ------------------------------------------------------------------
    async def run_eda(self, dataset_id: Union[int, str], target_column: Optional[str] = None) -> Dict[str, Any]:
        """Perform Exploratory Data Analysis (EDA) on a dataset."""
        payload = {"dataset_id": dataset_id}
        if target_column:
            payload["target_column"] = target_column
        return await self._request("POST", "/api/v1/analysis/eda", json=payload)

    async def clean_dataset(self, dataset_id: Union[int, str], strategies: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply data cleaning, missing value imputation, and formatting."""
        payload = {"dataset_id": dataset_id}
        if strategies:
            payload["strategies"] = strategies
        return await self._request("POST", "/api/v1/analysis/clean", json=payload)

    async def generate_visualizations(self, dataset_id: Union[int, str], chart_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate interactive charts and statistical graphics."""
        payload = {"dataset_id": dataset_id}
        if chart_types:
            payload["chart_types"] = chart_types
        return await self._request("POST", "/api/v1/analysis/visualizations", json=payload)

    async def run_auto_analysis(self, dataset_id: Union[int, str]) -> Dict[str, Any]:
        """Run complete end-to-end automated data intelligence analysis."""
        return await self._request("POST", "/api/v1/analysis/auto", json={"dataset_id": dataset_id})

    async def get_analysis_report(self, analysis_id: Union[int, str]) -> Dict[str, Any]:
        """Fetch generated PDF report data for an analysis run."""
        return await self._request("GET", f"/api/v1/analysis/{analysis_id}/report")

    async def get_analysis_code(self, analysis_id: Union[int, str]) -> Dict[str, Any]:
        """Fetch auto-generated Python script for an analysis run."""
        return await self._request("GET", f"/api/v1/analysis/{analysis_id}/code")

    async def ask_question(self, query: str, dataset_id: Optional[Union[int, str]] = None) -> Dict[str, Any]:
        """Ask a natural language AI question on dataset analytics."""
        payload = {"query": query}
        if dataset_id:
            payload["dataset_id"] = dataset_id
        return await self._request("POST", "/api/v1/ask", json=payload)

    # ------------------------------------------------------------------
    # 4. Machine Learning
    # ------------------------------------------------------------------
    async def train_regression(self, dataset_id: Union[int, str], target_column: str) -> Dict[str, Any]:
        """Train and evaluate regression machine learning models."""
        return await self._request("POST", "/api/v1/ml/regression", json={"dataset_id": dataset_id, "target_column": target_column})

    async def train_classification(self, dataset_id: Union[int, str], target_column: str) -> Dict[str, Any]:
        """Train and evaluate classification machine learning models."""
        return await self._request("POST", "/api/v1/ml/classification", json={"dataset_id": dataset_id, "target_column": target_column})

    # ------------------------------------------------------------------
    # 5. Async Pipelines
    # ------------------------------------------------------------------
    async def execute_pipeline(self, dataset_id: Union[int, str], steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Dispatch asynchronous pipeline execution job."""
        return await self._request("POST", "/api/v1/pipeline/execute", json={"dataset_id": dataset_id, "steps": steps})

    async def get_pipeline_status(self, task_id: str) -> Dict[str, Any]:
        """Check status and results of an async background pipeline task."""
        return await self._request("GET", f"/api/v1/pipeline/status/{task_id}")

    # ------------------------------------------------------------------
    # 6. Developer & Key Management
    # ------------------------------------------------------------------
    async def generate_api_key(self, key_name: str, environment: str = "live", scopes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a new DataNova developer API key."""
        payload = {"key_name": key_name, "environment": environment}
        if scopes:
            payload["scopes"] = scopes
        return await self._request("POST", "/api/developer/api_key/generate", json=payload)

    async def revoke_api_key(self, key_id: Union[int, str]) -> Dict[str, Any]:
        """Revoke an active developer API key."""
        return await self._request("POST", "/api/developer/api_key/revoke", json={"key_id": key_id})
