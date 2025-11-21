import random
from app.domain.entities import Symbol, Currency, MarketChartData
import pandas as pd
from datetime import datetime
#Analytics layer services


def convert_market_chart_data_to_dataframe(marketchartdata: MarketChartData) -> pd.DataFrame:
    data = {
        'datetime'  : [p.timestamp for p in marketchartdata.points],
        'price'     : [p.price for p in marketchartdata.points]
    }  
    df = pd.DataFrame(data)
    return df
    

def compute_stats(df: pd.DataFrame, numeric_key: str):
    """
    Compute basic statistics for a numeric column in a price DataFrame.

    Expected df columns:
      - timestamp: datetime
      - <numeric_key>: float (e.g. "price")
    """
    if (df.empty):
        raise ValueError('Cannot compute stats on an empty DataFrame')
    if(numeric_key == '' or numeric_key is None):
        raise ValueError('numeric_key must be a non-empty string (e.g. "price")')
    if(numeric_key not in df):
        raise KeyError(f'{numeric_key} not found inside the DataFrame')
    
    series = df[numeric_key]
    
    result_dic = {
        'count':        len(df),
        'min':          series.min(),
        'max':          series.max(),
        'mean':         series.mean(),
        'median':       series.median(),
        'std':          series.std(),
        'first_price':  series.iloc[0],
        'last_price':   series.iloc[-1],
        'percent_change': ((series.iloc[-1] - series.iloc[0]) / series.iloc[0]) * 100
    }
    return result_dic    
    

if __name__ == "__main__":    
    #test convert_market_chart_data_to_dataframe witha  marketchart data example:
    from app.domain.entities import PricePoint
     #sample poins is a list[PricePoint] 
    sample_points = [ ]
    for i in range(100):
        p = PricePoint(timestamp=datetime(2024, 1, 1, 0, 0), price = random.random() + i**(1.25))
        sample_points.append(p)
        
    sample_chart = MarketChartData(Symbol.BTC, Currency.USD, sample_points)
    df = convert_market_chart_data_to_dataframe(sample_chart)   
    #compute stats:
    stats = compute_stats(df, 'price')
    for k, v in stats.items():
        print(f"{k}: {v}")