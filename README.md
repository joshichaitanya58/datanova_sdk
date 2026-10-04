# DataNova Python SDK (`datanova-sdk`)

The official Python client library for the **DataNova Smart Analytics Platform** REST API. Supports both synchronous (`requests`) and asynchronous (`httpx`) execution modes with automatic retries, context manager resource cleanup, and safe error handling.

---

## 🚀 Quick Installation

```bash
# Standard local installation:
pip install ./datanova-sdk

# Install with Async support (httpx):
pip install ./datanova-sdk[async]

# Install in editable mode for local SDK development:
pip install -e ./datanova-sdk[dev]
```

---

## ⚡ Quickstart Example (Synchronous)

```python
import logging
from datanova_sdk import DataNovaClient, DataNovaAPIError

# Optional: Enable logging for SDK debugging
logging.basicConfig(level=logging.INFO)

# Use context manager for automatic session cleanup & resource management
with DataNovaClient(
    api_key="dn_live_your_secret_key_here",
    base_url="https://datanova-fude.onrender.com",
    max_retries=3
) as client:
    try:
        # 1. System Health Check
        health = client.health()
        print("System Status:", health.get("status"))

        # 2. Upload Dataset with MIME Type auto-detection
        upload_res = client.upload_dataset("sample_data.csv")
        dataset_id = upload_res.get("dataset_id")
        
        if dataset_id:
            print("Uploaded Dataset ID:", dataset_id)

            # 3. Run Automated Exploratory Data Analysis (EDA)
            eda_results = client.run_eda(dataset_id=dataset_id)
            print("EDA Summary:", eda_results)

            # 4. Train Classification ML Model
            ml_results = client.train_classification(dataset_id=dataset_id, target_column="Purchased")
            print("ML Model Accuracy:", ml_results.get("accuracy"))
        else:
            print("Upload completed without dataset_id key:", upload_res)

    except DataNovaAPIError as err:
        print(f"API Error ({err.status_code}): {err}")
```

---

## ⚡ Async Quickstart Example (FastAPI / Asyncio)

```python
import asyncio
from datanova_sdk import AsyncDataNovaClient

async def main():
    async with AsyncDataNovaClient(
        api_key="dn_live_your_secret_key_here",
        base_url="https://datanova-fude.onrender.com"
    ) as client:
        health = await client.health()
        print("Async Status:", health.get("status"))

        datasets = await client.list_datasets()
        print("Datasets:", datasets)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🛡️ Production Features

- **API Key Validation**: Ensures client initialization requires a valid non-empty API key.
- **Safe JSON & Response Parsing**: Soft fallback for non-JSON or HTML error responses (`raw_response`).
- **MIME Type Auto-Detection**: Guesses content types dynamically (`.csv`, `.xlsx`, `.xls`, etc.) using `mimetypes`.
- **Automatic Retry Mechanism**: Built-in exponential backoff retries for status codes `429`, `502`, `503`, and `504`.
- **Session Resource Management**: Implements `close()` and Python context manager protocol (`__enter__` / `__exit__`).
- **Dynamic Version User-Agent**: Headers include `DataNova-Python-SDK/1.0.0` or `DataNova-Python-SDK-Async/1.0.0`.
- **Integrated Logging**: Debug logs and trace logging via standard Python `logging.getLogger("datanova")`.

---

## 🛠️ Supported REST API Endpoints (All 17 APIs)

| Category | Method / Function | REST Endpoint |
| :--- | :--- | :--- |
| **System** | `client.health()` | `GET /api/v1/health` |
| **Datasets** | `client.list_datasets()` | `GET /api/v1/datasets` |
| **Datasets** | `client.upload_dataset(file_path)` | `POST /api/v1/datasets/upload` |
| **Datasets** | `client.preview_dataset(id)` | `GET /api/v1/datasets/{id}/preview` |
| **Analytics** | `client.run_eda(id, target_column)` | `POST /api/v1/analysis/eda` |
| **Analytics** | `client.clean_dataset(id, strategies)` | `POST /api/v1/analysis/clean` |
| **Analytics** | `client.generate_visualizations(id)` | `POST /api/v1/analysis/visualizations` |
| **Analytics** | `client.run_auto_analysis(id)` | `POST /api/v1/analysis/auto` |
| **Analytics** | `client.get_analysis_report(id)` | `GET /api/v1/analysis/{id}/report` |
| **Analytics** | `client.get_analysis_code(id)` | `GET /api/v1/analysis/{id}/code` |
| **AI Q&A** | `client.ask_question(query, id)` | `POST /api/v1/ask` |
| **Machine Learning** | `client.train_regression(id, target)` | `POST /api/v1/ml/regression` |
| **Machine Learning** | `client.train_classification(id, target)`| `POST /api/v1/ml/classification` |
| **Pipelines** | `client.execute_pipeline(id, steps)` | `POST /api/v1/pipeline/execute` |
| **Pipelines** | `client.get_pipeline_status(task_id)` | `GET /api/v1/pipeline/status/{task_id}` |
| **Developer Keys** | `client.generate_api_key(name)` | `POST /api/developer/api_key/generate` |
| **Developer Keys** | `client.revoke_api_key(key_id)` | `POST /api/developer/api_key/revoke` |

---


