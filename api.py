from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pymongo import MongoClient
import unicorn_fy
import unicorn_binance_websocket_api
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databases import DatabaseURL, Database
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import requests
import json

DATABASE_URL = "sqlite:///./test.db"
database = Database(DATABASE_URL)
# df = pd.DataFrame([],columns=['timestamp','open','high','low','close','volume','symbol','interval'])
Base = declarative_base()

class Candlestick(Base):
    __tablename__ = "candlesticks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)

class CandlestickData(BaseModel):
    symbol: str
    timestamp: float
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
def get_database(databaseName):

           # Provide the mongodb atlas url to connect python to mongodb using pymongo
            CONNECTION_STRING = "mongodb+srv://drstone:hamzaalikhan@cluster0.kjxeldw.mongodb.net/?retryWrites=true&w=majority"

           # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
            client = MongoClient(CONNECTION_STRING)

           # Create the database for our example (we will use the same database throughout the tutorial
            return client[databaseName]
# mongodb+srv://drstone:<password>@cluster0.kjxeldw.mongodb.net/?retryWrites=true&w=majority
def sendData(entry,dbname,collectionName):
    try:
        
        
        print('Sending Data to MongoDB!')
        
        
        collection_name = dbname[collectionName]
        # for index,instance in enumerate(mongo_insert_data):
        collection_name.insert_one(entry)
        collection_name.comm.csv
        # print('Data sent to MongoDB successfully')

    except Exception as e:
        print('Some error occured while sending data MongoDB! Following is the error.')
        print(e)
        print('-----------------------------------------')
app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_db_client():
    await database.disconnect()

async def handle_candlestick_data(data):
    candlestick = CandlestickData(**data)
    query = candlestick.insert().returning(candlestick)
    await database.execute(query)

@app.post("/stream-data/")
async def stream_data(symbol: str, interval: str,start_time:int,end_time:int):
    global df
    print('symbol=>',symbol)
    print('interval=>',interval)
    # Create a WebSocket connection to Binance
    unicornfy = unicorn_fy.UnicornFy()
    response = requests.get(f'https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}&startTime={start_time}&endTime={end_time}')
    data = response.json()
    # print(data)
    # binance_websocket_api_manager = unicorn_binance_websocket_api.BinanceWebSocketApiManager(exchange="binance.com")
    db = get_database('Binance')
    arr = []
    # print(data)
    for i in data:
        # print(i[0])
        dictionay = {'openTime':datetime.fromtimestamp(i[0]/1000.0),
                    'open':float(i[1]),
                    'high':float(i[2]),
                    'low':float(i[3]),
                    'close':float(i[4]),
                    'volume':float(i[5]),
                    'closeTime':datetime.fromtimestamp(i[6]/1000.0),
                    'assestVolume':float(i[7]),
                    'noOfTrades':int(i[8]),
                    'symbol':symbol,
                    'interval':interval}
        arr.append(dictionay)

    def handle_stream_data(stream_data):
        global df
        unicorn_fied_stream_data = unicornfy.binance_com_websocket(stream_data)
        if 'result' not in list(unicorn_fied_stream_data.keys()):
            print(datetime.fromtimestamp(unicorn_fied_stream_data['event_time']/1000.0).timestamp())
            dictionay = {'timestamp':datetime.fromtimestamp(unicorn_fied_stream_data['event_time']/1000.0),
                        'open':float(unicorn_fied_stream_data['kline']['open_price']),
                        'high':float(unicorn_fied_stream_data['kline']['high_price']),
                        'low':float(unicorn_fied_stream_data['kline']['low_price']),
                        'close':float(unicorn_fied_stream_data['kline']['close_price']),
                        'volume':float(unicorn_fied_stream_data['kline']['base_volume']),
                        'symbol':symbol,
                        'interval':interval}
            sendData(dictionay,db,symbol)
            # df2 = pd.DataFrame([dictionay])
            # df = pd.concat([df,df2],ignore_index=True)
            # # df = df.append(df2,ignore_index = True)
            # print(df.head())
        
    # binance_websocket_api_manager.create_stream(channels=[f'kline_{interval}'], markets=[symbol],process_stream_data=handle_stream_data)

    # manager.create_stream(["kline_{}_{}".format(symbol.lower(), interval)], "kline_{}_{}".format(symbol, interval), output="dict", callback=handle_stream_data)

    return {"message": "Streaming data started.","data":arr}

@app.post("/analyze-cycles/")
async def analyze_cycles(symbol: str, interval: str,start_time:int,end_time:int):
    client = TestClient(app)
    response = client.post(f"/stream-data?symbol={symbol}&interval={interval}&start_time={start_time}&end_time={end_time}")
    data = response.json()
    # print(data['message'])
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    }
    params = (
        ('amplitudeMulti', '1'),
        ('bartelsLimit', '49'),
        ('minCycleLength', '5'),
        ('maxCycleLength', '400'),
        ('cycleResolution', '1'),
        ('dType', '0'),
        ('epf', 'false'),
        ('savgolSmoothing', 'false'),
        ('sortByStrength', 'true'),
        ('dominantPeakFinder', 'false'),
        ('savgolSmoothingSpectrum', 'false'),
        ('includeSpectrum', 'false'),
        ('humanReadableText', 'false'),
        ('api_key', 'aqwR-ZuCPpFcrtXX5MNCEA'),
    )
    # df = pd.DateFrame(data['data'])
    # print(df['close'].to_array())
    close_values = list(d['close'] for d in data['data'])
    print('lenght of close',close_values[0:101])
    response = requests.post('https://api.cycle.tools/api/cycles/CycleScanner', headers=headers, params=params, data=f'{close_values}')
    # print(response)
    results = response.json()
    # print(results)
    # resp = requests.post(f"https://api.cycle.tools/api/cycles/CycleScanner?amplitudeMulti=1&bartelsLimit=49&minCycleLength=5&maxCycleLength=400&cycleResolution=1&dType=0&epf=false&savgolSmoothing=false&sortByStrength=true&dominantPeakFinder=false&savgolSmoothingSpectrum=false&includeSpectrum=false&humanReadableText=false&api_key=aqwR-ZuCPpFcrtXX5MNCEA",{
        
    # })
    # Retrieve data from the local database based on user's request
    # Perform analysis using the Cycle Scanner API
    # Save analysis results in the local database
    # Return analysis results
    return {"message": "Cycle analysis completed and saved.","data":results}
