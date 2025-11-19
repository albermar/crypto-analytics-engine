from app.domain.entities import Symbol, Currency, Provider
from app.infrastructure.mapper import MAPPER_CURRENCY_PROVIDER, MAPPER_SYMBOL_PROVIDER
from app.infrastructure.errors import InfrastructureProviderNotCompatibleError


# -------- Mapping functions -------- #

def map_provider_symbol_id(sym: Symbol, prov: Provider) -> str:    
    try:
        id_sym = MAPPER_SYMBOL_PROVIDER[prov][sym]
        return id_sym
    except KeyError:
        raise InfrastructureProviderNotCompatibleError(f'Symbol: {sym} not supported by Provider: {prov}')

def map_provider_currency_id(cur: Currency, prov: Provider) -> str:    
    try:
        id_cur = MAPPER_CURRENCY_PROVIDER[prov][cur]
        return id_cur
    except KeyError:
        raise InfrastructureProviderNotCompatibleError(f'Currency: {cur} not supported by Provider: {prov}')

# -------- End of mapping functions -------- #
    
    
    
    
    
        