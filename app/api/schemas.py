from datetime import datetime
from pydantic import BaseModel
from app.domain.entities import Symbol, Currency, MarketChartData, PricePoint

class PricePointResponse(BaseModel):
    timestamp: datetime
    price: float
    
    @classmethod
    def from_domain(cls, domain_price_point: PricePoint) -> 'PricePointResponse':
        timestamp = domain_price_point.timestamp
        price = domain_price_point.price 
        
        return cls(timestamp=timestamp, price=price)
        
        
        

class MarketChartResponse(BaseModel):
    symbol: Symbol
    currency: Currency
    points: list[PricePointResponse]
    
    @classmethod
    def from_domain(cls, domain_market_chart_data: MarketChartData) -> 'MarketChartResponse':
        sym = domain_market_chart_data.symbol
        cur = domain_market_chart_data.currency
        pts = []
        for price_point in domain_market_chart_data.points:
            #Convert to PricePointResponse and append to my list of PricePointResponse
            pts.append(PricePointResponse.from_domain(price_point))
        #WITH LIST COMPREHENSION
        #pts = [PricePointResponse.from_domain(p) for p in domain_market_chart_data.points]
        return cls(symbol=sym, currency=cur, points=pts)

            
            

