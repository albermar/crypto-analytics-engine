import os
from datetime import date
from typing import Any

import pandas as pd
import requests
import streamlit as st

from app.domain.entities import Symbol, Currency, ResampleFrequency


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
PROVIDER_VALUE = "coingecko"
REQUEST_TIMEOUT = 60


def _valid_enum_values(enum_cls):
    return [item for item in enum_cls if not item.name.startswith("__")]


def _format_value(value, decimals: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def _render_stats_list(stats: dict) -> None:
    st.subheader("Statistics")

    rows = [
        ("Count", _format_value(stats.get("count"), 0)),
        ("Min", _format_value(stats.get("min_price"), 2)),
        ("Max", _format_value(stats.get("max_price"), 2)),
        ("Mean", _format_value(stats.get("mean_price"), 2)),
        ("Median", _format_value(stats.get("median_price"), 2)),
        ("Std dev", _format_value(stats.get("std_dev"), 4)),
        ("Variance", _format_value(stats.get("variance"), 4)),
        ("First", _format_value(stats.get("first_price"), 2)),
        ("Last", _format_value(stats.get("last_price"), 2)),
        ("% Change", f"{_format_value(stats.get('percent_change'), 2)}%"),
    ]

    for label, value in rows:
        st.markdown(
            f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:16px;
                padding:8px 0;
                border-bottom:1px solid rgba(255,255,255,0.08);
            ">
                <span style="font-weight:600;">{label}</span>
                <span>{value}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_instructions() -> None:
    st.subheader("Instructions")
    st.markdown(
        """
This tool uses the API to fetch historical crypto market data and render an enriched PNG chart.

It can include:
- price, returns, resampling, rolling mean, volatility, normalization and date trimming

Configure the setup below and press **Load analytics**.
The current result stays visible until you load a new one.
"""
    )


def _build_common_params(config: dict) -> dict[str, Any]:
    params: dict[str, Any] = {
        "provider": PROVIDER_VALUE,
        "days": config["days"],
    }

    if config["frequency"] is not None:
        params["frequency"] = config["frequency"]

    if config["window_size"] is not None:
        params["window_size"] = config["window_size"]

    if config["volatility_window"] is not None:
        params["volatility_window"] = config["volatility_window"]

    if config["normalize_base"] is not None:
        params["normalize_base"] = config["normalize_base"]

    if config["use_trim"]:
        if config["start"] is not None:
            params["start"] = pd.to_datetime(config["start"]).isoformat()
        if config["end"] is not None:
            params["end"] = pd.to_datetime(config["end"]).isoformat()

    return params


def _raise_for_api_error(response: requests.Response) -> None:
    if response.ok:
        return

    detail = None
    try:
        payload = response.json()
        if isinstance(payload, dict):
            detail = payload.get("detail")
    except Exception:
        pass

    if detail:
        raise RuntimeError(str(detail))

    raise RuntimeError(f"API request failed with status {response.status_code}.")


def _parse_dataframe_payload(payload: Any) -> pd.DataFrame:
    if payload is None:
        return pd.DataFrame()

    if isinstance(payload, list):
        return pd.DataFrame(payload)

    if not isinstance(payload, dict):
        raise ValueError("Unsupported dataframe payload received from API.")

    for key in ("data", "records", "rows", "items", "dataframe", "result"):
        value = payload.get(key)
        if isinstance(value, list):
            return pd.DataFrame(value)

    if "columns" in payload and "rows" in payload:
        columns = payload["columns"]
        rows = payload["rows"]
        if isinstance(columns, list) and isinstance(rows, list):
            return pd.DataFrame(rows, columns=columns)

    dict_values = list(payload.values())
    if payload and all(isinstance(v, list) for v in dict_values):
        return pd.DataFrame(payload)

    return pd.DataFrame([payload])


def _fetch_stats(config: dict) -> dict:
    url = f"{API_BASE_URL}/market_chart/stats"
    params = {
        "symbol": config["symbol"],
        "currency": config["currency"],
        "days": config["days"],
        "provider": PROVIDER_VALUE,
    }

    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    _raise_for_api_error(response)
    return response.json()


def _fetch_dataframe(config: dict) -> pd.DataFrame:
    url = f"{API_BASE_URL}/market_chart/dataframe"
    params = {
        "symbol": config["symbol"],
        "currency": config["currency"],
        **_build_common_params(config),
    }

    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    _raise_for_api_error(response)

    df = _parse_dataframe_payload(response.json())
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return df


def _fetch_png(config: dict) -> bytes:
    url = f"{API_BASE_URL}/market_chart/{config['symbol']}/{config['currency']}/plot-enriched"
    params = _build_common_params(config)

    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    _raise_for_api_error(response)
    return response.content


def _compute_payload(config: dict) -> dict:
    stats = _fetch_stats(config)
    df = _fetch_dataframe(config)

    if df.empty:
        raise ValueError("No data returned.")

    image_bytes = _fetch_png(config)

    return {
        "stats": stats,
        "df": df,
        "image_bytes": image_bytes,
        "caption": f"{config['symbol']}/{config['currency']} enriched chart",
    }


def _render_setup_panel(valid_symbols, valid_currencies, valid_frequencies):
    st.subheader("Setup")

    top1, top2, top3 = st.columns([1.2, 1.0, 0.8])
    with top1:
        selected_symbol = st.selectbox(
            "Symbol",
            options=valid_symbols,
            format_func=lambda x: x.value,
            index=0,
            key="symbol",
        )
    with top2:
        selected_currency = st.selectbox(
            "Currency",
            options=valid_currencies,
            format_func=lambda x: x.value,
            index=0,
            key="currency",
        )
    with top3:
        days = st.number_input(
            "Days",
            min_value=1,
            value=365,
            step=1,
            key="days",
        )

    st.markdown("#### Optional analytics")

    left_opt, right_opt = st.columns(2)

    with left_opt:
        row = st.columns([1.1, 1.9])
        with row[0]:
            use_resampling = st.checkbox("Resampling", value=False, key="use_resampling")
        with row[1]:
            selected_frequency = st.selectbox(
                "Frequency",
                options=valid_frequencies,
                format_func=lambda x: x.value,
                disabled=not use_resampling,
                label_visibility="collapsed",
                key="frequency",
            )

        row = st.columns([1.1, 1.9])
        with row[0]:
            use_rolling = st.checkbox("Rolling mean", value=False, key="use_rolling")
        with row[1]:
            window_size = st.number_input(
                "Rolling window",
                min_value=1,
                value=7,
                step=1,
                disabled=not use_rolling,
                label_visibility="collapsed",
                key="window_size",
            )

        row = st.columns([1.1, 1.9])
        with row[0]:
            use_volatility = st.checkbox("Volatility", value=False, key="use_volatility")
        with row[1]:
            volatility_window = st.number_input(
                "Volatility window",
                min_value=2,
                value=7,
                step=1,
                disabled=not use_volatility,
                label_visibility="collapsed",
                key="volatility_window",
            )

    with right_opt:
        row = st.columns([1.1, 1.9])
        with row[0]:
            use_normalization = st.checkbox("Normalization", value=False, key="use_normalization")
        with row[1]:
            normalize_base = st.number_input(
                "Normalization base",
                min_value=1.0,
                value=100.0,
                step=1.0,
                disabled=not use_normalization,
                label_visibility="collapsed",
                key="normalize_base",
            )

        use_trim = st.checkbox("Trim dates", value=False, key="use_trim")
        d1, d2 = st.columns(2)
        with d1:
            start = st.date_input(
                "Start date",
                disabled=not use_trim,
                key="start_date",
                value=None,
            )
        with d2:
            end = st.date_input(
                "End date",
                disabled=not use_trim,
                key="end_date",
                value=None,
            )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        load_clicked = st.button("Load analytics", type="primary", use_container_width=True)

    return {
        "symbol": selected_symbol.value,
        "currency": selected_currency.value,
        "days": int(days),
        "frequency": selected_frequency.value if use_resampling else None,
        "window_size": int(window_size) if use_rolling else None,
        "volatility_window": int(volatility_window) if use_volatility else None,
        "normalize_base": float(normalize_base) if use_normalization else None,
        "use_trim": use_trim,
        "start": start if use_trim else None,
        "end": end if use_trim else None,
        "load_clicked": load_clicked,
    }


def _render_top_left(valid_symbols, valid_currencies, valid_frequencies):
    with st.container():
        _render_instructions()
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        return _render_setup_panel(valid_symbols, valid_currencies, valid_frequencies)


def _render_top_right(result: dict | None) -> None:
    st.subheader("Chart")

    if result is None:
        st.info("Load analytics to generate the PNG chart.")
        return

    st.image(result["image_bytes"], use_container_width=True)
    st.caption(result["caption"])


def _render_bottom(result: dict) -> None:
    st.divider()

    left_col, right_col = st.columns([3, 7], gap="large")

    with left_col:
        _render_stats_list(result["stats"])

    with right_col:
        st.subheader("Data")
        st.dataframe(result["df"], use_container_width=True, height=430)


def main() -> None:
    st.set_page_config(page_title="Market Analytics", layout="wide")
    st.title("Market Analytics")

    valid_symbols = _valid_enum_values(Symbol)
    valid_currencies = _valid_enum_values(Currency)
    valid_frequencies = _valid_enum_values(ResampleFrequency)

    if "analytics_result" not in st.session_state:
        st.session_state.analytics_result = None

    top_left, top_right = st.columns([4, 6], gap="large")

    with top_left:
        config = _render_top_left(
            valid_symbols=valid_symbols,
            valid_currencies=valid_currencies,
            valid_frequencies=valid_frequencies,
        )

    with top_right:
        _render_top_right(st.session_state.analytics_result)

    if config["load_clicked"]:
        try:
            st.session_state.analytics_result = _compute_payload(config)
            st.rerun()
        except Exception as e:
            st.error(str(e))

    if st.session_state.analytics_result is not None:
        _render_bottom(st.session_state.analytics_result)


main()