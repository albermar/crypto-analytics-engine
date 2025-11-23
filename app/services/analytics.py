import random
from app.domain.entities import Symbol, Currency, MarketChartData
import pandas as pd
from datetime import datetime
#Analytics layer services

def _validate_numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if df.empty:
        raise ValueError('Cannot compute stats on an empty DataFrame')
    if not column or not isinstance(column, str):
        raise ValueError('numeric_key must be a non-empty string (e.g. "price")')
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")
    
    series = df[column]

    if series.isna().all():
        raise ValueError(f'All values in the column {column} are NaN, cannot compute statistics.')

    return series

def convert_market_chart_data_to_dataframe(marketchartdata: MarketChartData) -> pd.DataFrame:
    data = {
        'timestamp'  : [p.timestamp for p in marketchartdata.points],
        'price'     : [p.price for p in marketchartdata.points]
    }
    return pd.DataFrame(data)

def compute_stats(df: pd.DataFrame, stats_key: str) -> dict:
    """
    Compute basic statistics for a numeric column in a price DataFrame.
    """
    series = _validate_numeric_series(df, stats_key)
    
    result_dic = {
        "count": int(series.count()),
        "min_price": float(series.min()),
        "max_price": float(series.max()),
        "mean_price": float(series.mean()),
        "median_price": float(series.median()),
        "std_dev": float(series.std()),
        "variance": float(series.var()),
        "first_price": float(series.iloc[0]),
        "last_price": float(series.iloc[-1]),
        "percent_change": float((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100),
    }
    
    return result_dic

def compute_returns (df: pd.DataFrame, stats_key: str) -> None:
    series = _validate_numeric_series(df, stats_key)

    df['pct_change'] = series.pct_change() * 100    
    df['acum_pct_change'] = (series - series.iloc[0]) / series.iloc[0] * 100

def compute_rolling_window(df: pd.DataFrame, window_size: int, stats_key: str) -> None:
    series = _validate_numeric_series(df, stats_key)
    df[f'rolling_mean_{window_size}'] = series.rolling(window=window_size).mean()

def resample_price_series(df: pd.DataFrame, stats_key: str, rule: str) -> pd.DataFrame:
    series = _validate_numeric_series(df, stats_key)
    #shall we make a copy? answer: yes, to avoid modifying the original df
    df_resampled = df.copy()
    df_resampled.set_index('timestamp', inplace=True) #Why inplace must be true? because we want to modify the df_resampled directly
    resampled_df = series.resample(rule).ohlc().reset_index()
        
    return resampled_df


if __name__ == "__main__":
    #test convert_market_chart_data_to_dataframe witha  marketchart data example:
    from app.domain.entities import PricePoint
     #sample poins is a list[PricePoint] 
    sample_points = [ ]
    for i in range(21):
        #ensure datetimes are increasing 1 day from each other
        p = PricePoint(timestamp=datetime(2024, 5, 11, 0, 0) + pd.Timedelta(days=i), price = 100+i)
        sample_points.append(p)
        
    sample_chart = MarketChartData(Symbol.BTC, Currency.USD, sample_points)
    df = convert_market_chart_data_to_dataframe(sample_chart)   
    #compute stats:
    
    stats = compute_stats(df, 'price')
    #for k, v in stats.items():
     #   print(f"{k}: {v}")
    
    #print df dataframe:
    #print(df)

    compute_returns(df, stats_key='price')    
    compute_rolling_window(df, window_size=7, stats_key='price')
    print(df)    
    
    df_resample_1W = df[['price', 'timestamp']].copy()
    df_resample_1W = df_resample_1W.resample('Y', on='timestamp').ohlc()
    print(df_resample_1W)
    #print(df_resample_1W)