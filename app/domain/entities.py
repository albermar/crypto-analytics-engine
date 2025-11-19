'''
Symbol
Currency
Provider
PricePoint
MarketDataChart
'''

from enum import Enum
from datetime import datetime


class Symbol(Enum):
    BTC = 'bitcoin'
    XRP = 'ripple'
    ETH = "ethereum"
    __UNMAPPED__ = "__unmapped__"
    

class Currency(Enum):
    USD = "usd"     
    EUR = "eur"   
    GBP = "gbp" 
    AUD = "aud"
    CHF = "chf"
    JPY = "jpy" 
    __UNMAPPED__ = "__unmapped__"

class Provider(Enum):
    COINGECKO   = 'coingecko'
    BINANCE     = 'binance'
    KRAKEN      = 'kraken'

#---

class PricePoint:
    timestamp: datetime
    price: float

class MarketChartData:
    symbol: Symbol
    currency: Currency
    points: list[PricePoint]
