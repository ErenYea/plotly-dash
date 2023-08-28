from fastapi import FastAPI, WebSocket
import httpx
import json
import requests
from datetime import datetime
import unicorn_fy
import unicorn_binance_websocket_api
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd

# from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
# from unicorn_binance_websocket_api_process_streams import BinanceWebSocketApiProcessStreams

app = FastAPI()
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
df = pd.DataFrame([],columns=['timestamp','open','high','low','close','volume','symbol','interval'])

class OHLCVData(Base):
    __tablename__ = "ohlcv_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    symbol = Column(String)
    interval = Column(String)

Base.metadata.create_all(bind=engine)

@app.websocket("/ws/{symbol}/{interval}")
async def websocket_endpoint(symbol: str, interval: str, websocket: WebSocket):
    await websocket.accept()
    unicornfy = unicorn_fy.UnicornFy()
    # url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}"
    # response = requests.get(url).json()
    binance_websocket_api_manager = unicorn_binance_websocket_api.BinanceWebSocketApiManager(exchange="binance.com")
    binance_websocket_api_manager.create_stream(channels=[f'kline_{interval}'], markets=[symbol])
    # print(response.text)
    # print(data)
    
    while True:
        oldest_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if oldest_data_from_stream_buffer:
            unicorn_fied_stream_data = unicornfy.binance_com_websocket(oldest_data_from_stream_buffer)
            print(unicorn_fied_stream_data)
            
            await websocket.send_json(unicorn_fied_stream_data)
  

@app.post("/analyze-cycle")
async def analyze_cycle(symbol: str, interval: str):
    global df
    
    # Fetch data from the local database based on symbol and interval
    # # Format the data as needed for the Cycle Scanner API
    # data = []  # Your formatted data

    # cycle_scanner_url = "YOUR_CYCLE_SCANNER_API_URL"
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(cycle_scanner_url, json=data)
    #     response_data = response.json()

        # Save the response_data to your local database
        # ...
    # df.to_json()
    return json.dumps(df.to_json())
