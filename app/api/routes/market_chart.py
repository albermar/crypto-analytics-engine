from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
import tempfile
import os
import re

from app.api.schemas import MarketChartResponse, StatsResponse, DataFrameResponse
from app.domain.entities import ResampleFrequency, Symbol, Currency, Provider
from app.domain.services import fetch_market_chart, compute_market_chart_stats, compute_enriched_market_chart
from app.domain import errors
from app.services.analytics import convert_market_chart_data_to_dataframe
from datetime import datetime

from app.reports.plots import plot_enriched_price


router = APIRouter(prefix='/market_chart', tags=['market-chart'])


def _hide_url(message: str) -> str:
    if not message:
        return message
    return re.sub(r"https?://\S+", "", message).strip()


@router.get('/',
            response_model=MarketChartResponse,
            summary='Fetch crypto data for market chart',
            description='Retrieve historical market chart data for a specified cryptocurrency, currency, and number of days.')
def get_market_chart(symbol: Symbol, currency: Currency, days: int, provider: Provider):

    try:
        data = fetch_market_chart(symbol, currency, days, provider)

    except errors.BusinessValidationError as e:
        raise HTTPException(status_code=400, detail=_hide_url(str(e)))

    except errors.BusinessProviderNotCompatible as e:
        raise HTTPException(status_code=400, detail=_hide_url(str(e)))

    except errors.BusinessProviderGeneralError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))

    except errors.BusinessMalformedDataError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))

    except errors.BusinessNoDataError as e:
        raise HTTPException(status_code=404, detail=_hide_url(str(e)))

    return MarketChartResponse.from_domain(data)


@router.get('/stats',
            response_model=StatsResponse,
            summary='Fetch statistics for market chart data',
            description='Retrieve statistical information (mean, median, std deviation) for historical market chart data of a specified cryptocurrency, currency, and number of days.')
def get_market_chart_stats(symbol: Symbol, currency: Currency, days: int, provider: Provider):

    try:
        stats = compute_market_chart_stats(symbol, currency, days, provider)
    except errors.BusinessValidationError as e:
        raise HTTPException(status_code=400, detail=_hide_url(str(e)))

    except errors.BusinessProviderNotCompatible as e:
        raise HTTPException(status_code=400, detail=_hide_url(str(e)))

    except errors.BusinessProviderGeneralError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))

    except errors.BusinessMalformedDataError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))

    except errors.BusinessNoDataError as e:
        raise HTTPException(status_code=404, detail=_hide_url(str(e)))

    except errors.BusinessComputationError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))

    stats = StatsResponse.from_dict(stats)

    return stats


@router.get('/dataframe', response_model=DataFrameResponse,
            summary='Fetch enriched market chart data as DataFrame',
            description='Retrieve enriched historical market chart data for a specified cryptocurrency, currency, and number of days, with optional analytics such as resampling frequency, rolling window, normalization, and volatility calculation.')
def get_market_chart_dataframe(
    symbol: Symbol,
    currency: Currency,
    days: int,
    provider: Provider,
    frequency: Optional[ResampleFrequency] = None,
    window_size: Optional[int] = None,
    normalize_base: Optional[float] = None,
    volatility_window: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
):
    try:
        df = compute_enriched_market_chart(
            symbol=symbol,
            currency=currency,
            days=days,
            provider=provider,
            frequency=frequency,
            window_size=window_size,
            normalize_base=normalize_base,
            volatility_window=volatility_window,
            start=start,
            end=end,
        )

    except errors.BusinessValidationError as e:
        raise HTTPException(status_code=400, detail=_hide_url(str(e)))

    except errors.BusinessProviderNotCompatible as e:
        raise HTTPException(status_code=400, detail=_hide_url(str(e)))

    except errors.BusinessProviderGeneralError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))

    except errors.BusinessMalformedDataError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))

    except errors.BusinessNoDataError as e:
        raise HTTPException(status_code=404, detail=_hide_url(str(e)))

    except errors.BusinessComputationError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))

    return DataFrameResponse.from_dataframe(df)


@router.get(
    "/{symbol}/{currency}/plot-enriched",
    summary="Get enriched market chart plot as PNG",
    description=(
        "Return an enriched PNG plot including: price with rolling mean, resampled series, "
        "daily returns, accumulated returns, normalized price and volatility."
    ),
    response_class=Response,
)
def get_market_chart_plot_enriched(
    symbol: Symbol,
    currency: Currency,
    days: int = Query(..., description="Number of historical days to fetch."),
    provider: Provider = Query(..., description="Data provider to use."),
    frequency: ResampleFrequency | None = Query(None, description="Optional resampling frequency (e.g. DAILY, WEEKLY)."),
    window_size: int | None = Query(None, gt=0, description="Rolling window size for moving average (if provided)."),
    normalize_base: float | None = Query(None, description="Base value for normalized price series (e.g. 100.0)."),
    volatility_window: int | None = Query(None, gt=1, description="Rolling window size for volatility calculation."),
    start: datetime | None = Query(None, description="Optional start datetime (ISO-8601) to trim the dataset."),
    end: datetime | None = Query(None, description="Optional end datetime (ISO-8601) to trim the dataset."),
):
    try:
        df = compute_enriched_market_chart(
            symbol=symbol,
            currency=currency,
            days=days,
            provider=provider,
            frequency=frequency,
            window_size=window_size,
            normalize_base=normalize_base,
            volatility_window=volatility_window,
            start=start,
            end=end,
        )

    except errors.BusinessValidationError as e:
        raise HTTPException(status_code=400, detail=_hide_url(str(e)))
    except errors.BusinessProviderNotCompatible as e:
        raise HTTPException(status_code=400, detail=_hide_url(str(e)))
    except errors.BusinessProviderGeneralError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))
    except errors.BusinessMalformedDataError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))
    except errors.BusinessNoDataError as e:
        raise HTTPException(status_code=404, detail=_hide_url(str(e)))
    except errors.BusinessComputationError as e:
        raise HTTPException(status_code=500, detail=_hide_url(str(e)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_hide_url(f"Unexpected error: {e}"))

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        plot_enriched_price(
            df=df,
            out_path=tmp_path,
            symbol=symbol,
            currency=currency,
            provider=provider,
            price_key="price",
            resample_frequency=frequency,
        )

        with open(tmp_path, "rb") as f:
            img_bytes = f.read()

        return Response(content=img_bytes, media_type="image/png")

    finally:
        if tmp_path is not None and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass