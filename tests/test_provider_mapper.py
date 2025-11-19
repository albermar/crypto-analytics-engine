##--- ERROR import
from app.infrastructure.errors import InfrastructureProviderNotCompatibleError
##--- Domain Entities Import
from app.domain.entities import Symbol, Currency, Provider

##--- Helper functions import
from app.infrastructure.helper import map_provider_symbol_id, map_provider_currency_id

import pytest

TEST_CASES_SYMBOL_ID_OK = [
    (Symbol.BTC, Provider.COINGECKO, 'bitcoin'),
    (Symbol.ETH, Provider.COINGECKO, 'ethereum'),
    (Symbol.XRP, Provider.COINGECKO, 'ripple')
]

TEST_CASES_SYMBOL_TYPES_STRING_OK = [
    (Symbol.BTC, Provider.COINGECKO),
    (Symbol.ETH, Provider.COINGECKO,),
    (Symbol.XRP, Provider.COINGECKO)
]


TEST_CASES_UNMAPPEDSYMBOL_ERROR = [
    (Provider.COINGECKO, InfrastructureProviderNotCompatibleError),
]

def test_symbol_id_ok():
    for sym, prov, expected_id in TEST_CASES_SYMBOL_ID_OK:
        result = map_provider_symbol_id(sym, prov)
        assert result == expected_id

def test_symbol_types_ok():
    for sym, prov in TEST_CASES_SYMBOL_TYPES_STRING_OK:
        result = map_provider_symbol_id(sym, prov)
        assert isinstance(result, str)
        
def test_unmapped_symbol_error():
    for prov, exc in TEST_CASES_UNMAPPEDSYMBOL_ERROR:
        #check if the error InfrastructureProviderNotCompatibleError is raised
        with pytest.raises(exc):
            map_provider_symbol_id(Symbol.__UNMAPPED__, prov)


##End Symbol Tests


TEST_CASES_CURRENCY_ID_OK = [
    (Currency.EUR, Provider.COINGECKO, 'eur'), 
    (Currency.USD, Provider.COINGECKO, 'usd'),
    (Currency.GBP, Provider.COINGECKO, 'gbp'),
    (Currency.AUD, Provider.COINGECKO, 'aud'),
    (Currency.CHF, Provider.COINGECKO, 'chf'),
    (Currency.JPY, Provider.COINGECKO, 'jpy')
]
TEST_CASES_CURRENCY_TYPES_STRING_OK = [
    (Currency.EUR, Provider.COINGECKO), 
    (Currency.USD, Provider.COINGECKO),
    (Currency.GBP, Provider.COINGECKO),
    (Currency.AUD, Provider.COINGECKO),
    (Currency.CHF, Provider.COINGECKO),
    (Currency.JPY, Provider.COINGECKO)
]

TEST_CASES_UNMAPPEDCURRENCY_ERROR = [
    (Provider.COINGECKO, InfrastructureProviderNotCompatibleError)
]

def test_currency_id_ok():
    for curr, prov, expected_id in TEST_CASES_CURRENCY_ID_OK:
        result = map_provider_currency_id(curr, prov)
        assert result == expected_id

def test_currency_type_string_ok():
    for curr, prov in TEST_CASES_CURRENCY_TYPES_STRING_OK:
        result = map_provider_currency_id(curr, prov)
        assert isinstance(result, str)

def test_unmappedcurrency_error():
    for prov, exc in TEST_CASES_UNMAPPEDCURRENCY_ERROR:
        with pytest.raises(exc):
            map_provider_currency_id(Currency.__UNMAPPED__, prov)
            
#everything ok? 
