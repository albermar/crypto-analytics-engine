#Here I'm going to create the function that will ask coingecko for market data and return the raw data as dictionary

from app.infrastructure import errors
from app.domain.entities import Symbol, Currency, Provider
from app.infrastructure.mapper import map_provider_currency_id, map_provider_symbol_id

import httpx 

def infra_get_market_chart_coingecko(    sym: Symbol,     curr: Currency,     days: int) -> dict:
    '''
    Fetch market chart data from CoinGecko API.
    '''
    # 1 ) First we need to map if the currency and symbol are supported by this provider:
    
    # Could raise errors.InfrastructureProviderNotCompatibleError. We let them go up
    id_curr = map_provider_currency_id(curr, Provider.COINGECKO) 
    id_sym = map_provider_symbol_id(sym, Provider.COINGECKO)
    
    # 2 ) Now we try to build the URL with the params. In this moment the URL construction won't have problems, but anyway I will create de error handling structure just in case later we need to check something about this URL construction:
    
    try:
        #Build the URL for the request:
        URL =  f'https://api.coingecko.com/api/v3/coins/{id_sym}/market_chart'
    except errors.InfrastructureBadURL as e: #this error would be raised by us if something is wrong with the URL construction. But in this moment there is no possible error here.
        raise e  
        
    
    # 3 ) Now we proceed with the httpx request
    params = {
        'vs_currency': id_curr, 
        'days': days
    }
    try:
        response = httpx.get(URL, params = params, timeout = 5.0) 
        #response2 = httpx.request("GET", URL, params = params, timeout = 5.0)
    except httpx.TimeoutException:
        raise errors.InfrastructureExternalApiTimeout
    except httpx.RequestError:
        raise errors.InfrastructureExternalApiError
    except Exception: #Generic exception for any other unexpected error
        raise errors.InfrastructureExternalApiError
    
    #the reason why we first catch timeout, then requestError and then generic exception is because TimeoutException is a subclass of RequestError (https://www.python-httpx.org/exceptions/), so if we catch first RequestError, TimeoutException will never be catched. Besides that, TimeoutException is a specific case that we want to handle separately. RequestError is a more general case that includes other types of request-related errors, such as connection errors, DNS resolution failures, etc. Anyway, it's important that whatever the error catcher structure is, we must be sure that all exceptions raised in the try block are catched, otherwise the function would fail without raising our defined Infrastructure errors.
    #The most simple way to catch all errors is:
    #except Exception: 
    # this would catch all exceptions, but we would lose granularity. So the best way is to catch first the specific exceptions we want to handle separately, and then a generic exception for any other unexpected error.
    #So always, for security, we must have a generic exception catcher at the end like except Exception: This will ensure that any unexpected error is caught and handled appropriately.
    #---
    #in this point we have the response, so there was communication. Now we need to evaluate the type of response (status code)
    #possible status codes in this point are:
    # 200: OK 
    # 4xx: Client errors (e.g., 400 Bad Request, 404 Not Found)
    # 5xx: Server errors (e.g., 500 Internal Server Error)
    # Everything that is not 200 means that the request was not successful.
    if response.status_code != 200:
        raise errors.InfrastructureExternalApiError
    #in this point the status code is 200, we need to parse the JSON response:    
    try:    
        parsed_data = response.json()
    except Exception as e:
        raise errors.InfrastructureExternalApiMalformedResponse(e)
    #in this point we have the parsed JSON data, we return it:
    return parsed_data

if __name__ == "__main__":
    data = infra_get_market_chart_coingecko(Symbol.BTC, Currency.USD, 7)
    for x in data['prices']:
        print(x)
