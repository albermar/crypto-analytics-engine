'''
General philosophy:
    1 ) Happy path 
    2 ) Edge cases / Boundaries (single row, constant price, minimal window, etc)
    3 ) Error behaviout (inputs that should raise ValueError, KeyError, etc)
    4 ) Side effects
        * Does it modify the DataFrame in place? Does it returns a new one?
        * Does it keep the index? Columns? Data types?

Functions to test:
    _validate_numeric_series
    convert_market_chart_data_to_dataframe
    
    calculate_stats
    
    compute_returns
    compute_rolling_window
    resample_price_series
    trim_date_range
    normalize_series
    compute_volatility

'''
import pytest
from datetime import datetime
import pandas as pd
from app.services.analytics import (
    _validate_numeric_series,
    convert_market_chart_data_to_dataframe,
    calculate_stats,
    compute_returns,
    compute_rolling_window,
    resample_price_series,
    trim_date_range,
    normalize_series,
    compute_volatility
)
from app.domain.entities import Symbol, Currency, PricePoint, MarketChartData, ResampleFrequency

# Testing steps (no code):
# 1) Create sample MarketChartData with known PricePoints
# 2) Convert to DataFrame using convert_market_chart_data_to_dataframe
# 3) Test each function with the DataFrame and verify outputs

# Sample MarketChartData for testing
def build_sample_marketchartdata():
    """
    Build a MarketChartData object for manual testing.
    This is NOT a pytest fixture — just a normal function.
    """
    points = [
        PricePoint(timestamp=datetime(2023, 1, 1), price=100.0),
        PricePoint(timestamp=datetime(2023, 1, 2), price=110.0),
        PricePoint(timestamp=datetime(2023, 1, 3), price=105.0),
        PricePoint(timestamp=datetime(2023, 1, 4), price=115.0),
        PricePoint(timestamp=datetime(2023, 1, 5), price=120.0),
    ]
    return MarketChartData(symbol=Symbol.BTC, currency=Currency.USD, points=points)

def build_sample_marketchartdata_2():
    """
    Build a MarketChartData object for manual testing.
    This is NOT a pytest fixture — just a normal function.
    """
    points = [
        PricePoint(timestamp=datetime(2025, 11, 17), price=1.0),
        PricePoint(timestamp=datetime(2025, 11, 18), price=2.0),
        PricePoint(timestamp=datetime(2025, 11, 19), price=3.0),
        PricePoint(timestamp=datetime(2025, 11, 20), price=4.0),
        PricePoint(timestamp=datetime(2025, 11, 21), price=5.0),
        PricePoint(timestamp=datetime(2025, 11, 22), price=6.0),
        PricePoint(timestamp=datetime(2025, 11, 23), price=7.0),
        PricePoint(timestamp=datetime(2025, 11, 24), price=8.0)
    ]
    return MarketChartData(symbol=Symbol.BTC, currency=Currency.USD, points=points)

# Test convert_market_chart_data_to_dataframe
def test_convert_market_chart_data_to_dataframe():
    sample_data = build_sample_marketchartdata()
    df = convert_market_chart_data_to_dataframe(sample_data)
    print(df)
    assert len(df) == 5
    assert list(df.columns) == ['timestamp', 'price']    
    assert df.iloc[0]['timestamp'] == datetime(2023, 1, 1)
    assert df.iloc[0]['price'] == 100.0
    assert df.iloc[4]['timestamp'] == datetime(2023, 1, 5)
    assert df.iloc[4]['price'] == 120.0

# Test _validate_numeric_series
def test_validate_numeric_series():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    
    series = _validate_numeric_series(df, 'price')
    assert series.equals(df['price'])
    
    # Test non-numeric column
    df['non_numeric'] = ['a', 'b', 'c', 'd', 'e']
    with pytest.raises(ValueError):
        _validate_numeric_series(df, 'non_numeric')
    
    # Test missing column
    with pytest.raises(KeyError):
        _validate_numeric_series(df, 'missing_column')
        
    #test all NaN column
    df['all_nan'] = [float('nan')] * len(df)
    with pytest.raises(ValueError):
        _validate_numeric_series(df, 'all_nan') 

# Test calculate_stats
def test_calculate_stats():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    stats = calculate_stats(df, 'price')
    
    assert stats['count'] == 5
    assert stats['min_price'] == 100.0
    assert stats['max_price'] == 120.0
    assert stats['mean_price'] == 110.0
    assert stats['median_price'] == 110.0
    assert round(stats['std_dev'], 5) == 7.90569
    assert round(stats['variance'], 5) == 62.5
    assert stats['first_price'] == 100.0
    assert stats['last_price'] == 120.0
    assert round(stats['percent_change'], 5) == 20.0

# Test compute_returns
def test_compute_returns():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    compute_returns(df, 'price')
    
    expected_pct_change = [float('nan'), 10.0, -4.54545, 9.52381, 4.34783]
    expected_acum_pct_change = [0.0, 10.0, 5.0, 15.0, 20.0]
    
    for i in range(len(df)):
        if i == 0:
            assert pd.isna(df.iloc[i]['pct_change'])
        else:
            assert round(df.iloc[i]['pct_change'], 5) == round(expected_pct_change[i], 5)
        assert round(df.iloc[i]['acum_pct_change'], 5) == round(expected_acum_pct_change[i], 5)

#test compute_rolling_window
def test_compute_rolling_window():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    compute_rolling_window(df, 3, 'price')
    
    expected_rolling_mean_3 = [float('nan'), float('nan'), 105.0, 110.0, 113.33333]
    
    for i in range(len(df)):
        if i < 2:
            assert pd.isna(df.iloc[i]['rolling_mean_3'])
        else:
            assert round(df.iloc[i]['rolling_mean_3'], 5) == round(expected_rolling_mean_3[i], 5)

#test resample_price_series
def test_resample_price_series():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata_2())    
    resampled_df = resample_price_series(df, 'price', ResampleFrequency.WEEKLY)
    assert len(resampled_df) == 2  # Two weeks
    assert resampled_df.iloc[0]['price'] == 7.0  # last of first week (1-4)
    assert resampled_df.iloc[1]['price'] == 8.0  # last of second week (5-8)
#test trim_date_range

#test trim_date_range
def test_trim_date_range():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata_2())    
    start_date = datetime(2025, 11, 19)
    end_date = datetime(2025, 11, 22)
    trimmed_df = trim_date_range(df, start_date, end_date)
    assert len(trimmed_df) == 4
    assert trimmed_df.iloc[0]['timestamp'] == start_date
    assert trimmed_df.iloc[3]['timestamp'] == end_date
    assert trimmed_df.iloc[0]['price'] == 3.0
    assert trimmed_df.iloc[3]['price'] == 6.0

#test normalize_series
def test_normalize_series():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    normalize_series(df, 'price', 200.0)
    
    expected_normalized_prices = [200.0, 220.0, 210.0, 230.0, 240.0]
    
    for i in range(len(df)):
        assert round(df.iloc[i]['price'], 5) == round(expected_normalized_prices[i], 5)


if __name__ == "__main__":
    # Manual test
    sample_data = build_sample_marketchartdata()
    df = convert_market_chart_data_to_dataframe(sample_data)
    stats = calculate_stats(df, 'price')
    print(stats)
    print(df)    