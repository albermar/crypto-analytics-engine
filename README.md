# Crypto Market Data Fetcher (Clean Architecture)

Small backend project to fetch and visualize crypto market data from external providers (starting with **CoinGecko**), using a clean, layered architecture.

Current focus: **BTC/ETH price history endpoint**, with proper separation of concerns and professional error handling.

---

## Architecture Overview

```
app/
 ├── 1-api/             # FastAPI routes + Pydantic models 
 ├── 2-business/        # Use cases (application / business logic) 
 ├── 3-domain/          # Domain entities (dataclasses, value objects) 
 ├── 4-infrastructure/  # External providers (CoinGecko client) 
 └── 5-tests/           # Unit / integration tests
```

---

## Domain Entities

```python
from enum import Enum
from datetime import datetime

class Symbol(str, Enum):
    BTC = "bitcoin"
    ETH = "ethereum"
    XRP = "ripple"

class Currency(str, Enum):
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    AUD = "aud"
    CHF = "chf"
    JPY = "jpy"

class Provider(str, Enum):
    COINGECKO = "coingecko"


class PricePoint:
    timestamp: datetime
    price: float


class MarketChartData:
    symbol: Symbol
    currency: Currency
    points: list[PricePoint]
```

---

## API Pydantic Models

```python
from pydantic import BaseModel
from datetime import datetime

class PricePointResponse(BaseModel):
    timestamp: datetime
    price: float


class MarketChartDataResponse(BaseModel):
    symbol: Symbol
    currency: Currency
    points: list[PricePointResponse]


class MarketChartRequest(BaseModel):
    symbol: Symbol
    currency: Currency
    days: int
```

---

## How to Run

Use **uvicorn** to run the FastAPI app:

```bash
uvicorn app.main:app --reload
```

### Endpoints

- `GET /market-chart` — fetch historical market price data for a given symbol and currency.

