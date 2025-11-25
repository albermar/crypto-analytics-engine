import pandas as pd
import matplotlib.pyplot as plt
from app.domain.services import fetch_market_chart
from app.domain.entities import Symbol, Currency, Provider
from datetime import datetime, timedelta

from app.services.analytics import compute_rolling_window
from app.domain.services import compute_enriched_market_chart

#Use matplotlib and potly

def plot_price(df: pd.DataFrame, out_path: str) -> None:
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    #plot
    plt.figure(figsize=(12,6))
    plt.plot(df['timestamp'], df['price'], label='Price', color='blue', linewidth=2)
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.title('Price Series Over Time')
    plt.grid(True)
    
    # Save in png
    plt.savefig(out_path, format='png', dpi = 300, bbox_inches='tight')
    plt.close()

#plot enriched price with rolling window
def plot_enriched_price(df: pd.DataFrame, out_path: str, window_size: int | None = None) -> None:
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    plt.figure(figsize=(12,6))
    plt.plot(df['timestamp'], df['price'], label='Price', color='blue', linewidth=2)
    
    if window_size is not None:
        rolling_col = f'rolling_mean_{window_size}'
        if rolling_col in df.columns:
            plt.plot(df['timestamp'], df[rolling_col], label=f'Rolling Mean ({window_size})', color='orange', linewidth=2)
    
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.title('Enriched Price Series Over Time')
    plt.grid(True)
    plt.legend()
    
    # Save in png
    plt.savefig(out_path, format='png', dpi = 300, bbox_inches='tight')
    plt.close()
    
#plot volatility 
def plot_volatility(df: pd.DataFrame, out_path: str, volatility_window: int) -> None: 
    #price and volatility in two axes in the same plot, because they have different scales
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    volatility_col = f'volatility_{volatility_window}'
    fig, ax1 = plt.subplots(figsize=(12,6))
    ax1.plot(df['timestamp'], df['price'], label='Price', color='blue', linewidth=2)
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Price', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2 = ax1.twinx()
    if volatility_col in df.columns:
        ax2.plot(df['timestamp'], df[volatility_col], label='Volatility', color='red', linewidth=2)
    ax2.set_ylabel('Volatility', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    plt.title('Price and Volatility Over Time')
    fig.tight_layout()
    plt.grid(True)
    plt.legend()
    # Save in png
    plt.savefig(out_path, format='png', dpi = 300, bbox_inches='tight')
    plt.close()
    
#Test:

if __name__ == "__main__":
    #fetch bitcoin 100 points data from coingecko api using fetch_market_chart
    symbol = Symbol.BTC
    currency = Currency.USD
    days = 365
    provider = Provider.COINGECKO
    '''
    chart = fetch_market_chart(symbol, currency, days, provider)
    #convert the MarketChartData to a pandas DataFrame
    sample_points = [{'timestamp': point.timestamp, 'price': point.price} for point in chart.points]
    df = pd.DataFrame(sample_points)
    #plot the price series
    plot_price(df, 'price_series.png')
    '''
    #Enrich the DataFrame with a rolling window of size 7
    window_size = 15
    #use compute_enriched_market_chart from services.py to get enriched DataFrame
    enriched_df = compute_enriched_market_chart(
        symbol=symbol,
        currency=currency,
        days=days,
        provider=provider,
        window_size=window_size
    )
    #plot the enriched price series
    #plot_enriched_price(enriched_df, 'enriched_price_series.png', window_size=window_size)
    
    #plot volatility with window size 15
    volatility_window = 15
    enriched_df = compute_enriched_market_chart(
        symbol=symbol,
        currency=currency,
        days=days,
        provider=provider,
        volatility_window=volatility_window
    )
    print(enriched_df.head(30))
    plot_volatility(enriched_df, 'volatility_series.png', volatility_window=volatility_window)