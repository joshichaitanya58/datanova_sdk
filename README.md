# DataNova Python SDK

**Official Python SDK for the DataNova Smart Analytics Platform REST API.**

[![PyPI Version](https://img.shields.io/pypi/v/datanova-sdk.svg)](https://pypi.org/project/datanova-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/datanova-sdk.svg)](https://pypi.org/project/datanova-sdk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

DataNova SDK provides a simple and production-ready Python interface for
interacting with the DataNova Smart Analytics Platform.

It supports:

- Dataset upload and management
- Dataset preview and inspection
- Automated EDA
- Data cleaning
- Automatic visualizations
- Automated data analysis
- AI-powered questions
- Machine learning
- Asynchronous pipelines
- Pipeline status monitoring
- Developer API key management
- Synchronous and asynchronous API clients

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Async Usage](#async-usage)
- [Dataset Operations](#dataset-operations)
- [Analytics](#analytics)
- [AI Q&A](#ai-qa)
- [Machine Learning](#machine-learning)
- [Pipelines](#pipelines)
- [High-Level Convenience Methods](#high-level-convenience-methods)
- [API Key Management](#api-key-management)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [Supported API Endpoints](#supported-api-endpoints)
- [Development](#development)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Security](#security)
- [License](#license)

---

# Features

### Core

- Synchronous client powered by `requests`
- Asynchronous client powered by `httpx`
- Automatic retry support
- Configurable request timeout
- SSL verification support
- Environment variable configuration
- Context manager support
- Safe JSON response parsing
- Structured API exceptions
- Request/correlation ID support
- Automatic MIME type detection
- Python `Path` and string file-path support

### Data Analytics

- Dataset upload
- Dataset listing
- Dataset preview
- Exploratory Data Analysis
- Data cleaning
- Automatic visualizations
- Automated end-to-end analysis
- Analysis reports
- Generated analysis code

### AI

- Natural-language questions about datasets
- Optional dataset-aware AI queries
- Combined automated analysis + AI question workflow

### Machine Learning

- Regression
- Classification

### Pipelines

- Execute asynchronous pipelines
- Check pipeline status
- Wait for pipeline completion automatically

---

# Requirements

DataNova SDK requires:

- Python **3.8 or newer**
- Internet access to the DataNova API

The SDK does not restrict itself to a specific future Python 3.x version.

For example:

```text
Python 3.8+
Python 3.9+
Python 3.10+
Python 3.11+
Python 3.12+
Python 3.13+
Python 3.14+
Future Python 3.x versions
```

Actual compatibility with a future Python release may still depend on the
underlying third-party dependencies used by the SDK.

---

# Installation

## Install from PyPI

The recommended installation method is:

```bash
pip install datanova-sdk
```

Verify the installation:

```bash
pip show datanova-sdk
```

Check the installed version:

```bash
python -c "import datanova; print(datanova.__version__)"
```

---

## Install with Async Support

If you want to use `AsyncDataNovaClient`:

```bash
pip install "datanova-sdk[async]"
```

This installs the optional `httpx` dependency.

---

## Install for Development

For SDK development and testing:

```bash
pip install "datanova-sdk[dev]"
```

---

## Install from Local Source

If you cloned or downloaded the SDK source:

```bash
pip install ./datanova-sdk
```

For async support:

```bash
pip install "./datanova-sdk[async]"
```

For development:

```bash
pip install "./datanova-sdk[dev]"
```

---

## Editable Development Installation

When actively modifying the SDK source:

```bash
pip install -e "./datanova-sdk[dev]"
```

Changes to the source code will then be reflected immediately without
reinstalling the package.

---

# Configuration

DataNova SDK accepts the API key directly or through an environment variable.

## Option 1 — Pass API Key Directly

```python
from datanova import DataNovaClient

client = DataNovaClient(
    api_key="dn_live_your_api_key"
)
```

---

## Option 2 — Environment Variable

### Windows CMD

```cmd
set DATANOVA_API_KEY=dn_live_your_api_key
```

### Windows PowerShell

```powershell
$env:DATANOVA_API_KEY="dn_live_your_api_key"
```

### Linux / macOS

```bash
export DATANOVA_API_KEY="dn_live_your_api_key"
```

Then:

```python
from datanova import DataNovaClient

client = DataNovaClient()
```

This is the recommended approach for production applications.

---

## Custom API Base URL

The default API URL is:

```text
https://datanova-fude.onrender.com
```

You can override it:

```python
client = DataNovaClient(
    api_key="dn_live_your_api_key",
    base_url="https://your-api.example.com"
)
```

Or:

```bash
export DATANOVA_BASE_URL="https://your-api.example.com"
```

---

# Quick Start

## Synchronous Client

```python
from datanova import DataNovaClient, DataNovaAPIError

try:

    with DataNovaClient(
        api_key="dn_live_your_api_key"
    ) as client:

        # Check API health
        health = client.health()

        print("API Status:")
        print(health)

except DataNovaAPIError as error:

    print("DataNova API Error:")
    print("Message:", error)
    print("Status Code:", error.status_code)
    print("Request ID:", error.request_id)
```

---

# Complete Dataset Workflow

The following example demonstrates a typical DataNova workflow.

```python
from datanova import DataNovaClient, DataNovaAPIError

try:

    with DataNovaClient(
        api_key="dn_live_your_api_key",
        max_retries=3,
        timeout=60
    ) as client:

        # 1. Check API health
        health = client.health()

        print("Health:", health)

        # 2. Upload dataset
        upload = client.upload_dataset(
            "sample_data.csv"
        )

        print("Upload response:")
        print(upload)

        dataset_id = (
            upload.get("dataset_id")
            or upload.get("id")
        )

        if dataset_id is None:
            raise RuntimeError(
                "Dataset ID was not returned by the API."
            )

        print("Dataset ID:", dataset_id)

        # 3. Preview dataset
        preview = client.preview_dataset(
            dataset_id
        )

        print("Dataset Preview:")
        print(preview)

        # 4. Run EDA
        eda = client.run_eda(
            dataset_id
        )

        print("EDA:")
        print(eda)

        # 5. Generate visualizations
        visualizations = client.generate_visualizations(
            dataset_id
        )

        print("Visualizations:")
        print(visualizations)

        # 6. Run complete automated analysis
        analysis = client.run_auto_analysis(
            dataset_id
        )

        print("Automated Analysis:")
        print(analysis)

except DataNovaAPIError as error:

    print(
        f"DataNova API Error "
        f"({error.status_code}): {error}"
    )
```

---

# Dataset Operations

## List Datasets

```python
datasets = client.list_datasets()

print(datasets)
```

### Function

```python
client.list_datasets()
```

### API

```text
GET /api/v1/datasets
```

---

## Upload Dataset

Supported files depend on the DataNova API configuration.

Example:

```python
result = client.upload_dataset(
    "sales.csv"
)

print(result)
```

Excel example:

```python
result = client.upload_dataset(
    "sales.xlsx"
)
```

### Function

```python
client.upload_dataset(file_path)
```

### API

```text
POST /api/v1/datasets/upload
```

The SDK automatically detects the MIME type from the filename.

---

## Preview Dataset

```python
preview = client.preview_dataset(
    dataset_id=35
)

print(preview)
```

### Function

```python
client.preview_dataset(dataset_id)
```

### API

```text
GET /api/v1/datasets/{id}/preview
```

---

# Analytics

## Run EDA

```python
result = client.run_eda(
    dataset_id=35
)

print(result)
```

With a target column:

```python
result = client.run_eda(
    dataset_id=35,
    target_column="Purchased"
)
```

### Function

```python
client.run_eda(
    dataset_id,
    target_column=None
)
```

### API

```text
POST /api/v1/analysis/eda
```

---

## Clean Dataset

Basic:

```python
result = client.clean_dataset(
    dataset_id=35
)
```

With strategies:

```python
result = client.clean_dataset(
    dataset_id=35,
    strategies={
        "missing_values": "mean",
        "duplicates": "remove"
    }
)
```

### Function

```python
client.clean_dataset(
    dataset_id,
    strategies=None
)
```

### API

```text
POST /api/v1/analysis/clean
```

---

## Generate Visualizations

Generate default visualizations:

```python
result = client.generate_visualizations(
    dataset_id=35
)

print(result)
```

Specify chart types:

```python
result = client.generate_visualizations(
    dataset_id=35,
    chart_types=[
        "bar",
        "line",
        "histogram",
        "scatter"
    ]
)
```

### Function

```python
client.generate_visualizations(
    dataset_id,
    chart_types=None
)
```

### API

```text
POST /api/v1/analysis/visualizations
```

---

## Run Automated Analysis

```python
result = client.run_auto_analysis(
    dataset_id=35
)

print(result)
```

### Function

```python
client.run_auto_analysis(dataset_id)
```

### API

```text
POST /api/v1/analysis/auto
```

---

## Get Analysis Report

```python
report = client.get_analysis_report(
    analysis_id=10
)

print(report)
```

### Function

```python
client.get_analysis_report(analysis_id)
```

### API

```text
GET /api/v1/analysis/{id}/report
```

---

## Get Generated Analysis Code

```python
code = client.get_analysis_code(
    analysis_id=10
)

print(code)
```

### Function

```python
client.get_analysis_code(analysis_id)
```

### API

```text
GET /api/v1/analysis/{id}/code
```

---

# AI Q&A

Ask a general DataNova AI question:

```python
answer = client.ask_question(
    "What are the most important trends in my data?"
)

print(answer)
```

Ask a question about a specific dataset:

```python
answer = client.ask_question(
    query="Which product category has the highest sales?",
    dataset_id=35
)

print(answer)
```

### Function

```python
client.ask_question(
    query,
    dataset_id=None
)
```

### API

```text
POST /api/v1/ask
```

---

# Machine Learning

## Regression

```python
result = client.train_regression(
    dataset_id=35,
    target_column="Sales"
)

print(result)
```

### Function

```python
client.train_regression(
    dataset_id,
    target_column
)
```

### API

```text
POST /api/v1/ml/regression
```

---

## Classification

```python
result = client.train_classification(
    dataset_id=35,
    target_column="Purchased"
)

print(result)
```

### Function

```python
client.train_classification(
    dataset_id,
    target_column
)
```

### API

```text
POST /api/v1/ml/classification
```

---

# Pipelines

## Execute Pipeline

Define pipeline steps:

```python
steps = [
    {
        "step": "clean"
    },
    {
        "step": "eda"
    },
    {
        "step": "visualizations"
    }
]

result = client.execute_pipeline(
    dataset_id=35,
    steps=steps
)

print(result)
```

### Function

```python
client.execute_pipeline(
    dataset_id,
    steps
)
```

### API

```text
POST /api/v1/pipeline/execute
```

---

## Check Pipeline Status

```python
status = client.get_pipeline_status(
    task_id="your_task_id"
)

print(status)
```

### Function

```python
client.get_pipeline_status(task_id)
```

### API

```text
GET /api/v1/pipeline/status/{task_id}
```

---

## Wait for Pipeline Completion

Instead of manually polling the API:

```python
result = client.wait_for_pipeline(
    task_id="your_task_id"
)

print(result)
```

Customize polling:

```python
result = client.wait_for_pipeline(
    task_id="your_task_id",
    poll_interval=3,
    timeout=300
)

print(result)
```

### Function

```python
client.wait_for_pipeline(
    task_id,
    poll_interval=2.0,
    timeout=300.0
)
```

The method automatically checks the pipeline status until it reaches a
terminal state such as:

```text
completed
success
succeeded
failed
error
cancelled
canceled
```

---

# High-Level Convenience Methods

DataNova SDK also provides higher-level methods that combine existing API
operations.

---

## Analyze Dataset

Run automated analysis and optionally ask an AI question:

```python
result = client.analyze_dataset(
    dataset_id=35
)

print(result)
```

With an AI question:

```python
result = client.analyze_dataset(
    dataset_id=35,
    question="What are the most important business insights?"
)

print(result)
```

### Function

```python
client.analyze_dataset(
    dataset_id,
    question=None
)
```

This internally uses existing DataNova API operations.

---

## Upload and Analyze

Upload a dataset and automatically start analysis:

```python
result = client.upload_and_analyze(
    "sales.csv"
)

print(result)
```

With an AI question:

```python
result = client.upload_and_analyze(
    "sales.csv",
    question="What are the main trends in this dataset?"
)

print(result)
```

### Function

```python
client.upload_and_analyze(
    file_path,
    question=None
)
```

The returned structure contains:

```python
{
    "upload": {...},
    "analysis": {...}
}
```

---

# Async Usage

Install async support:

```bash
pip install "datanova-sdk[async]"
```

Then:

```python
import asyncio

from datanova import AsyncDataNovaClient


async def main():

    async with AsyncDataNovaClient(
        api_key="dn_live_your_api_key"
    ) as client:

        health = await client.health()

        print("Health:")
        print(health)

        datasets = await client.list_datasets()

        print("Datasets:")
        print(datasets)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Async Dataset Upload

```python
async with AsyncDataNovaClient(
    api_key="dn_live_your_api_key"
) as client:

    result = await client.upload_dataset(
        "sales.csv"
    )

    print(result)
```

---

## Async Automated Analysis

```python
async with AsyncDataNovaClient(
    api_key="dn_live_your_api_key"
) as client:

    result = await client.analyze_dataset(
        dataset_id=35,
        question="What are the major trends?"
    )

    print(result)
```

---

## Async Pipeline Waiting

```python
async with AsyncDataNovaClient(
    api_key="dn_live_your_api_key"
) as client:

    result = await client.wait_for_pipeline(
        task_id="your_task_id",
        poll_interval=2,
        timeout=300
    )

    print(result)
```

---

# API Key Management

## Generate API Key

```python
result = client.generate_api_key(
    key_name="My Application",
    environment="live"
)

print(result)
```

With scopes:

```python
result = client.generate_api_key(
    key_name="Analytics Application",
    environment="live",
    scopes=[
        "datasets",
        "analytics"
    ]
)

print(result)
```

### Function

```python
client.generate_api_key(
    key_name,
    environment="live",
    scopes=None
)
```

### API

```text
POST /api/developer/api_key/generate
```

---

## Revoke API Key

```python
result = client.revoke_api_key(
    key_id=123
)

print(result)
```

### Function

```python
client.revoke_api_key(key_id)
```

### API

```text
POST /api/developer/api_key/revoke
```

---

# Error Handling

DataNova SDK provides the `DataNovaAPIError` exception.

```python
from datanova import (
    DataNovaClient,
    DataNovaAPIError
)

try:

    with DataNovaClient(
        api_key="dn_live_your_api_key"
    ) as client:

        result = client.health()

except DataNovaAPIError as error:

    print("Message:", error)
    print("Status:", error.status_code)
    print("Payload:", error.payload)
    print("Request ID:", error.request_id)
```

Available error information:

```python
error.status_code
error.payload
error.request_id
```

For example:

```python
try:
    result = client.preview_dataset(999999)

except DataNovaAPIError as error:

    if error.status_code == 404:
        print("Dataset not found.")

    elif error.status_code == 401:
        print("Invalid API key.")

    elif error.status_code == 429:
        print("Rate limit exceeded.")
```

---

# Logging

The SDK uses Python's standard `logging` module.

Enable logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO
)
```

For detailed debugging:

```python
logging.basicConfig(
    level=logging.DEBUG
)
```

The synchronous client logger is:

```text
datanova
```

The asynchronous client logger is:

```text
datanova.async
```

---

# Client Configuration

The synchronous client supports:

```python
DataNovaClient(
    api_key=None,
    base_url=None,
    timeout=60,
    max_retries=3,
    backoff_factor=0.5,
    verify_ssl=True,
    user_agent=None
)
```

### Parameters

| Parameter | Description | Default |
|---|---|---:|
| `api_key` | DataNova API key | Environment variable |
| `base_url` | DataNova API base URL | Official API |
| `timeout` | Request timeout in seconds | `60` |
| `max_retries` | Retry attempts | `3` |
| `backoff_factor` | Retry backoff | `0.5` |
| `verify_ssl` | Verify HTTPS certificates | `True` |
| `user_agent` | Custom User-Agent | SDK default |

Example:

```python
client = DataNovaClient(
    api_key="dn_live_your_api_key",
    timeout=120,
    max_retries=5,
    backoff_factor=1.0,
    verify_ssl=True
)
```

---

# Automatic Retries

The SDK automatically retries supported transient HTTP failures.

Retryable status codes include:

```text
429
502
503
504
```

Example:

```python
client = DataNovaClient(
    api_key="dn_live_your_api_key",
    max_retries=3,
    backoff_factor=0.5
)
```

Retry behavior is handled by the underlying HTTP session.

---

# Context Manager

Using a context manager is recommended:

```python
with DataNovaClient(
    api_key="dn_live_your_api_key"
) as client:

    print(client.health())
```

The HTTP session is automatically closed when the block finishes.

You can also manually close the client:

```python
client = DataNovaClient(
    api_key="dn_live_your_api_key"
)

try:
    print(client.health())

finally:
    client.close()
```

---

# Supported API Endpoints

## Complete Endpoint Reference

| Category | Python Function | HTTP | REST Endpoint |
|---|---|---|---|
| System | `health()` | GET | `/api/v1/health` |
| Datasets | `list_datasets()` | GET | `/api/v1/datasets` |
| Datasets | `upload_dataset(file_path)` | POST | `/api/v1/datasets/upload` |
| Datasets | `preview_dataset(id)` | GET | `/api/v1/datasets/{id}/preview` |
| Analytics | `run_eda(id, target_column)` | POST | `/api/v1/analysis/eda` |
| Analytics | `clean_dataset(id, strategies)` | POST | `/api/v1/analysis/clean` |
| Analytics | `generate_visualizations(id)` | POST | `/api/v1/analysis/visualizations` |
| Analytics | `run_auto_analysis(id)` | POST | `/api/v1/analysis/auto` |
| Analytics | `get_analysis_report(id)` | GET | `/api/v1/analysis/{id}/report` |
| Analytics | `get_analysis_code(id)` | GET | `/api/v1/analysis/{id}/code` |
| AI | `ask_question(query, id)` | POST | `/api/v1/ask` |
| ML | `train_regression(id, target)` | POST | `/api/v1/ml/regression` |
| ML | `train_classification(id, target)` | POST | `/api/v1/ml/classification` |
| Pipelines | `execute_pipeline(id, steps)` | POST | `/api/v1/pipeline/execute` |
| Pipelines | `get_pipeline_status(task_id)` | GET | `/api/v1/pipeline/status/{task_id}` |
| Developer | `generate_api_key(name)` | POST | `/api/developer/api_key/generate` |
| Developer | `revoke_api_key(key_id)` | POST | `/api/developer/api_key/revoke` |

---

# SDK Convenience Methods

The following methods combine existing API operations and do not represent
additional REST endpoints:

| Method | Purpose |
|---|---|
| `wait_for_pipeline()` | Automatically poll pipeline status |
| `analyze_dataset()` | Run automated analysis + optional AI question |
| `upload_and_analyze()` | Upload dataset + run automated analysis |

---

# Production Recommendations

For production applications:

### 1. Use environment variables

Recommended:

```python
client = DataNovaClient()
```

with:

```text
DATANOVA_API_KEY
```

configured in the deployment environment.

---

### 2. Do not hard-code API keys

Avoid:

```python
api_key = "dn_live_real_secret_key"
```

Use:

```python
import os

api_key = os.getenv("DATANOVA_API_KEY")
```

---

### 3. Use context managers

Recommended:

```python
with DataNovaClient() as client:
    result = client.health()
```

---

### 4. Configure retries

For production workloads:

```python
client = DataNovaClient(
    max_retries=3,
    backoff_factor=0.5
)
```

---

### 5. Handle API errors

```python
try:
    result = client.health()

except DataNovaAPIError as error:
    print(error)
```

---

# Development

Clone the repository:

```bash
git clone https://github.com/joshichaitanya58/datanova.git
```

Move to the SDK directory:

```bash
cd datanova-sdk
```

Install development dependencies:

```bash
pip install -e ".[dev]"
```

---

# Run Tests

Run the complete test suite:

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/test_client.py
```

Run async tests:

```bash
pytest tests/test_async_client.py
```

---

# Build the Package

Install build tools:

```bash
python -m pip install --upgrade build twine
```

Build:

```bash
python -m build
```

This generates:

```text
dist/
├── datanova_sdk-1.1.1-py3-none-any.whl
└── datanova_sdk-1.1.1.tar.gz
```

---

# Validate the Package

Run:

```bash
python -m twine check dist/*
```

Expected result:

```text
Checking dist/...
PASSED
```

---

# Publish to PyPI

After validating the package:

```bash
python -m twine upload dist/*
```

PyPI will then allow users to install the SDK with:

```bash
pip install datanova-sdk
```

---

# Project Structure

```text
datanova-sdk/
│
├── datanova/
│   ├── __init__.py
│   ├── client.py
│   └── async_client.py
│
├── tests/
│   ├── test_client.py
│   └── test_async_client.py
│
├── README.md
├── LICENSE
├── pyproject.toml
└── setup.py
```

The `tests/` directory is used for development and CI testing and is not
required for normal SDK runtime usage.

---

# Security

Never commit real API keys to GitHub or other public repositories.

Use environment variables:

```bash
export DATANOVA_API_KEY="dn_live_your_api_key"
```

or configure the key through your cloud provider's environment-variable
settings.

If an API key is accidentally exposed, revoke it immediately and generate
a new one.

---

# Version

Current SDK version:

```text
1.1.1
```

Check it programmatically:

```python
import datanova

print(datanova.__version__)
```

---

# License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.

---

# DataNova

**Smart Analytics. Automated Insights. Data-Driven Decisions.**

Official API:

https://datanova-fude.onrender.com

GitHub:

https://github.com/joshichaitanya58/datanova
