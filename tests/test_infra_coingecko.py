from app.infrastructure.coingecko import infra_clean_raw_market_chart_coingecko, infra_get_raw_market_chart_coingecko
from app.domain.entities import PricePoint
from datetime import datetime
from app.infrastructure.errors import InfrastructureExternalApiMalformedResponse, InfrastructureExternalApiError
import pytest
import httpx
from app.domain.entities import Symbol, Currency


# 1 ) Test cleaner -> infra_clean_raw_market_chart_coingecko

def test_clean_raw_1_ok():
    TEST_CLEAN_RAW_OK = [
    (
        {   'prices': [
                [1622505600000, 35000.0],       
                [1622592000000, 36000.0],
                [1622678400000, 37000.0]
            ]
        },  
        [
            PricePoint(timestamp =  datetime.fromtimestamp(1622505600000 / 1000.0), price = 35000.0),
            PricePoint(timestamp =  datetime.fromtimestamp(1622592000000 / 1000.0), price = 36000.0),
            PricePoint(timestamp =  datetime.fromtimestamp(1622678400000 / 1000.0), price = 37000.0)
        ]
    )
]
    
    for raw_data, expected_clean in TEST_CLEAN_RAW_OK:
        clean_data = infra_clean_raw_market_chart_coingecko(raw_data)
        assert clean_data == expected_clean

def test_clean_raw_2_ok():
    raw = {
        'prices': [
            [1732032000000, 50000], 
            [1738118400000, 60500.57657],
            [1732411840000, 980500.5678],
        ]
    }    
    clean_points = infra_clean_raw_market_chart_coingecko(raw)    
    assert len(clean_points) == 3
    assert isinstance(clean_points[0], PricePoint)
    assert isinstance(clean_points[0].timestamp, datetime) 
    assert isinstance(clean_points[0].price, float) 
    assert clean_points[0].price == 50000.0
    assert clean_points[1].price == 60500.57657
    assert clean_points[2].timestamp == datetime.fromtimestamp(1732411840000 / 1000.0)
    assert clean_points[2].price == 980500.5678
    
def test_clean_raw_empty_ok():

    raw = {
        'nothing': [
            [1622505600000, 35000.0],       
            [1622592000000, 36000.0],
            [1622678400000, 37000.0]
        ], 
        'another nothing': [
            [1622505600000, 45000],       
            [1622592000000, 56000.2],
            [1622678400000, 67000.1]
        ]
    }
    with pytest.raises(InfrastructureExternalApiMalformedResponse):
        infra_clean_raw_market_chart_coingecko(raw)


# 2 ) Test HTTP -> infra_get_raw_market_chart_coingecko
# Use monketpatch to mock httpx.get and return predefined responses for different test cases.

def test_infra_get_raw_market_chart_coingecko_200(monkeypatch):
    # fake response object
    class FakeResponse_200:
        status_code = 200

        def json(self):
            return {"prices": [[1732032000000, 50000.0]]}

    def fake_get_200(url, params=None, timeout=None):
        return FakeResponse_200()

    # parcheamos httpx.get
    monkeypatch.setattr(httpx, "get", fake_get_200)
    # Now call the function
    raw_data = infra_get_raw_market_chart_coingecko(Symbol.BTC, Currency.USD, 1)
    #what is happening here? The fake_get function is called instead of httpx.get, returning our FakeResponse object.
    #why? Because we have patched httpx.get with monkeypatch.setattr.
    #inside python this is called "monkey patching", a technique to change or extend the behavior of libraries or modules at runtime.
    #it could be used with any library, not only httpx. for example:
    # monkeypatch.setattr(some_module, "some_function", fake_function)
    assert "prices" in raw_data
    assert raw_data["prices"] == [[1732032000000, 50000.0]]
    assert len(raw_data["prices"]) == 1
                                                
def test_infra_get_raw_market_chart_coingecko_404(monkeypatch):
    
    class FakeResponse_404:
        status_code = 404
        text = "Not Found"
    def fake_get_404(url, params=None, timeout=None):
        return FakeResponse_404()  
    monkeypatch.setattr(httpx, "get", fake_get_404)
    with pytest.raises(InfrastructureExternalApiError): 
        infra_get_raw_market_chart_coingecko(Symbol.BTC, Currency.USD, 1)   

def test_infra_get_raw_market_chart_coingecko_200_malformed(monkeypatch):
    #now test this part:
    '''
    try:    
        parsed_data = response.json()
    except Exception as e:
        raise errors.InfrastructureExternalApiMalformedResponse(e)
    '''
    class FakeResponse_200_BadJSON:
        status_code = 200

        def json(self):
            raise ValueError("Invalid JSON")
    def fake_get_200_badjson(url, params=None, timeout=None):
        return FakeResponse_200_BadJSON()   
    
    monkeypatch.setattr(httpx, "get", fake_get_200_badjson)
    with pytest.raises(InfrastructureExternalApiMalformedResponse):
        infra_get_raw_market_chart_coingecko(Symbol.BTC, Currency.USD, 1)
        
        