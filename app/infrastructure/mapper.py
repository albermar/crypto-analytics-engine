from app.domain.entities import Symbol, Currency, Provider
from typing import Dict

SymbolMap   = Dict[Symbol, str]
CurrencyMap = Dict[Currency, str]

MAPPER_SYMBOL_PROVIDER: Dict[Provider, SymbolMap] = {
    Provider.COINGECKO : {
        Symbol.BTC : "bitcoin",     
        Symbol.XRP : "ripple",
        Symbol.ETH : "ethereum"
        }, 
    Provider.BINANCE : {
        Symbol.BTC : "??",     
        Symbol.XRP : "??",
        Symbol.ETH : "??"
        }
 }

MAPPER_CURRENCY_PROVIDER: Dict[Provider, CurrencyMap] = {
    Provider.COINGECKO : {
        Currency.USD : "usd",
        Currency.EUR : "eur",
        Currency.GBP : "gbp",
        Currency.AUD : "aud",
        Currency.CHF : "chf",
        Currency.JPY : "jpy"
        }, 
    Provider.BINANCE : {
        Currency.USD : "???",
        Currency.EUR : "???",
        Currency.GBP : "???",
        Currency.AUD : "???",
        Currency.CHF : "???",
        Currency.JPY : "???"
        }
    }