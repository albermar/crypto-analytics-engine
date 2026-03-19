# Crypto Analytics Engine API

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![pandas](https://img.shields.io/badge/pandas-time--series-orange)
![Matplotlib](https://img.shields.io/badge/Matplotlib-visualization-purple)
![httpx](https://img.shields.io/badge/httpx-HTTP--client-blue)
![pytest](https://img.shields.io/badge/tests-pytest-orange)
![Architecture](https://img.shields.io/badge/architecture-clean--architecture-red)

![Example Plot](./outputs/XRP_EUR_COINGECKO_enriched_all_analytics.png)

## Overview

Production-style **crypto analytics backend** built with **FastAPI**, **pandas**, and **Matplotlib**.

The system retrieves historical market data from external providers (**CoinGecko**), transforms it into validated **domain models**, and applies a flexible analytics pipeline including **returns, rolling statistics, volatility, normalization, and resampling**.

It exposes multiple outputs through a clean API:

- raw market data (JSON)
- statistical summaries (JSON)
- enriched time-series datasets (DataFrame)
- analytical visualizations (PNG plots)

A **Streamlit demo application** allows users to interactively explore the analytics engine and visualize results in real time.

Live Demo: https://app-crypto.alberto.network

Live API: https://api-crypto.alberto.network

API Docs: https://api-crypto.alberto.network/docs



## Index

- [Overview](#overview)
- [Core Features](#core-features)
- [Architecture](#architecture)
- [Pipelines](#pipelines)
- [API Endpoints](#api-endpoints)
- [Tech Stack](#tech-stack)
- [Quickstart](#quickstart)
- [License](#license)

## Core Features

- **Modular analytics pipeline**  
  Flexible processing of time-series data with configurable transformations.

- **External data integration**  
  Real-time market data retrieval from CoinGecko with validation and error handling.

- **Time-series analytics engine**  
  Built-in support for returns, accumulated returns, rolling statistics, volatility, normalization, and resampling.

- **Multiple output formats**  
  Access data as raw JSON, statistical summaries, enriched DataFrames, or analytical plots.

- **Enriched DataFrame endpoint**  
  Generate analysis-ready datasets for dashboards, data apps, or further processing.

- **Analytical visualization engine**  
  Produce high-quality PNG plots with overlays such as rolling mean, volatility, and normalized prices.

- **Clean architecture design**  
  Clear separation between domain, business logic, infrastructure, and API layers.

- **Interactive demo interface**  
  Streamlit application to explore parameters, run analytics, and visualize results in real time.

## Architecture

The system follows a Clean Architecture approach where business logic is isolated from infrastructure concerns.

                ┌───────────────┐
                │   Client / UI │
                │ (Streamlit /  │
                │  Swagger UI)  │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │     FastAPI   │
                │     Routers   │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │  Application  │
                │   Services    │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │     Domain    │
                │ Entities +    │
                │  Interfaces   │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Infrastructure│
                │               │
                │ CoinGecko API │
                │ HTTP Client   │
                │ Data Mapping  │
                └───────────────┘

The domain and service layers are independent of external providers, allowing the data source or analytics logic to be extended or replaced without affecting the rest of the system.

This structure keeps the system modular, testable, and easy to extend.

## Pipelines

The system follows an end-to-end data processing pipeline from raw market data to enriched analytics outputs.

### Market data retrieval

    Symbol + currency + days
      ↓
    Validate input parameters
      ↓
    Fetch data from CoinGecko API
      ↓
    Validate and map response
      ↓
    Transform into domain entities (MarketChartData)

### Analytics enrichment

    MarketChartData
      ↓
    Convert to pandas DataFrame
      ↓
    Apply transformations (optional):
      - returns / accumulated returns
      - rolling mean
      - volatility
      - normalization
      - resampling
      ↓
    Generate enriched DataFrame

### Output generation

    Enriched DataFrame
      ↓
    Branch depending on endpoint:

    → JSON (raw data / stats / dataframe)
    → PNG plot (Matplotlib visualization)

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|------------|
| GET | /api/v1/market_chart/ | Retrieve raw historical market data |
| GET | /api/v1/market_chart/stats | Compute summary statistics (mean, std, min, max, etc.) |
| GET | /api/v1/market_chart/dataframe | Return enriched dataset with analytics applied |
| GET | /api/v1/market_chart/{symbol}/{currency}/plot-enriched | Generate analytical PNG plot with overlays |

All endpoints support query parameters such as:

- symbol (e.g. bitcoin, ethereum)
- currency (e.g. usd, eur)
- days (integer)
- provider (coingecko)

Optional analytics parameters:

- window_size (rolling mean)
- volatility_window
- normalize_base
- frequency
- start / end (date filtering)

Interactive API documentation is available at `/docs` when the FastAPI server is running.

## Tech Stack

| Backend | Data & Analytics | Visualization | Tools |
|--------|------------------|--------------|------|
| Python 3.11 | pandas | Matplotlib | pytest |
| FastAPI | | | httpx |
| Uvicorn | | | Streamlit |
| Pydantic | | | python-dotenv |

## Quickstart

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```
macOS / Linux:
```bash
source .venv/bin/activate
```

Windows:
```bash
.venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Configure environment variables

Create a `.env` file based on `.env.example`:
```
COINGECKO_API_KEY_DEMO=
API_BASE_URL=
```
- `COINGECKO_API_KEY_DEMO`: API key for CoinGecko
- `API_BASE_URL`: base URL used by the Streamlit demo

### 4. Run the API
```
uvicorn app.api.main:app --reload
```
### 5. Open API documentation
```
http://localhost:8000/docs
```
### 6. Run the Streamlit demo
```
streamlit run streamlit_app.py
```

## License

This project is released under the MIT License.