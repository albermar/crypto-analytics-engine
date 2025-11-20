from fastapi import FastAPI
from app.api.routes.market_chart import router as router_market_chart


app = FastAPI()

app.include_router(router_market_chart, prefix = '/api/v1')