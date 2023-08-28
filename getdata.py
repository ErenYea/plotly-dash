import asyncio
import websockets

async def connect_to_websocket():
    uri = "ws://localhost:8000/ws/BTCUSDT/1m"  # Replace with the WebSocket URL you want to connect to

    async with websockets.connect(uri) as websocket:
        while True:
            try:
                data = await websocket.recv()
                print("Received:", data)
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed.")
                break

# Run the event loop to start the WebSocket connection
asyncio.get_event_loop().run_until_complete(connect_to_websocket())
# if 'result' not in list(unicorn_fied_stream_data.keys()):
                
#                 ohlcv = OHLCVData(
#                         timestamp=datetime.fromtimestamp(unicorn_fied_stream_data['event_time'] / 1000.0),
#                         open=unicorn_fied_stream_data['kline']['open_price'],
#                         high=unicorn_fied_stream_data['kline']['high_price'],
#                         low=unicorn_fied_stream_data['kline']['low_price'],
#                         close=unicorn_fied_stream_data['kline']['close_price'],
#                         volume=unicorn_fied_stream_data['kline']['base_volume'],
#                         symbol=symbol,
#                         interval=interval
#                     )
#                 # print(unicorn_fied_stream_data)
#                 # print(datetime.fromtimestamp(unicorn_fied_stream_data['event_time']/1000.0))
#                 # dictionay = {'timestamp':datetime.fromtimestamp(unicorn_fied_stream_data['event_time']/1000.0),
#                 #                     'open':unicorn_fied_stream_data['kline']['open_price'],
#                 #                     'high':unicorn_fied_stream_data['kline']['high_price'],
#                 #                     'low':unicorn_fied_stream_data['kline']['low_price'],
#                 #                     'close':unicorn_fied_stream_data['kline']['close_price'],
#                 #                     'volume':unicorn_fied_stream_data['kline']['base_volume'],
#                 #                     'symbol':symbol,
#                 #                     'interval':interval}
#                 # # print(dictionay)
#                 # df2 = pd.DataFrame([dictionay])
#                 # df = pd.concat([df,df2],ignore_index=True)
#                 # df = df.append(df2,ignore_index = True)
#                 # db = SessionLocal()
#                 # db.add(ohlcv)
#                 # db.commit()
#                 # print(oldest_data_from_stream_buffer)