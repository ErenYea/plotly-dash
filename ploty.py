import dash
from dash import dcc, html, Input, Output
from dash.dependencies import Input, Output
from datetime import datetime as dt
import pandas as pd
import plotly.graph_objs as go
import requests
external_stylesheets = ['styles.css']
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
start_time = ''
end_time = ''
symbol = ''
interval = ''
df = ''
# app.css.append_css({'external_url': 'https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css'})
# Define your layout
app.layout = html.Div([
    html.H1("Cryptocurrency Analysis Dashboard"),
    dcc.Graph(id='main-chart'),
    html.Label("Select Cryptocurrency Pair Symbol:"),
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[
            {'label': 'BTCUSDT', 'value': 'btcusdt'},
            {'label': 'ETHUSDT', 'value': 'ethusdt'},
            # Add more cryptocurrency pairs
        ],
        value='btcusdt'
    ),
    html.Label("Select Timeframe:"),
    dcc.Dropdown(
        id='timeframe-dropdown',
        options=[
            {'label': '1m', 'value': '1m'},
            {'label': '5m', 'value': '5m'},
            {'label': '1h', 'value': '1h'},
            # Add more timeframes
        ],
        value='1m'
    ),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=dt(2023, 1, 1),
        end_date=dt(2023, 8, 1),
    ),
    html.Button("Fetch and Save Data", id="save-data-button"),
    html.Button("Analyze Cycles", id="analyze-button"),
    html.Table(id='cycle-table',className="table")
])

# Define callback to update the main chart
@app.callback(
    Output('main-chart', 'figure'),
    Input('symbol-dropdown', 'value'),
    Input('timeframe-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def update_main_chart(selected_symbol, selected_timeframe, start_date, end_date):
    global start_time,end_time,symbol,interval,df
    # Implement code to fetch data from local database based on inputs
    # Create a candlestick chart with OLHC visualization
    # Return the chart figure
    # print('startdate',start_date)
    startdate = dt.strptime(start_date.split('T')[0], '%Y-%m-%d')
    enddate = dt.strptime(end_date.split('T')[0], '%Y-%m-%d')
    epoch_start = dt(1970, 1, 1).date()
    delta1 = startdate.date() - epoch_start
    epoch_timestamp_start_date = int(str(int(delta1.total_seconds()))+'000')
    delta2 = enddate.date() - epoch_start
    epoch_timestamp_end_date = int(str(int(delta2.total_seconds()))+'000')
    start_time = epoch_timestamp_start_date
    end_time = epoch_timestamp_end_date
    symbol = selected_symbol
    interval = selected_timeframe
    # print('symbol=>',selected_symbol)
    # print('interval=>',selected_timeframe)
    # print('epoch_timestamp_start_date=>',epoch_timestamp_start_date)
    # print('epoch_timestamp_end_date=>',epoch_timestamp_end_date)
    response = requests.post(f'http://127.0.0.1:5000/stream-data?symbol={selected_symbol}&interval={selected_timeframe}&start_time={epoch_timestamp_start_date}&end_time={epoch_timestamp_end_date}')
    data = response.json()
    datas = [
        {'timestamp': '2023-08-01 12:00:00', 'open': 43000, 'high': 44000, 'low': 42000, 'close': 43500},
        {'timestamp': '2023-08-01 13:00:00', 'open': 43500, 'high': 44500, 'low': 43000, 'close': 44000},
        # Add more data points
    ]

    if data['message'] == 'Streaming data started.':
        datas = data['data']
        
    # print(datetime.fromtimestamp(epoch_timestamp))


    
    df = pd.DataFrame(datas)
    df['openTime'] = pd.to_datetime(df['openTime'])
    
    figure = go.Figure(data=[go.Candlestick(x=df['openTime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
    
    
    return figure

# Define callback to save data to local database
@app.callback(
    Output('save-data-button', 'n_clicks'),
    
    Input('save-data-button', 'n_clicks')
)
def save_data_to_database(n_clicks):
    # Implement code to fetch data from Binance based on inputs
    # Store the data in the local database
    if n_clicks is not None:
        response = requests.post(f'http://127.0.0.1:5000/stream-data?symbol={symbol}&interval={interval}&start_time={start_time}&end_time={end_time}')
        data = response.json()
        df = pd.DataFrame(data['data'])
        df.to_csv('saved_data.csv')
        
    return n_clicks

# Define callback to analyze cycles and display results
@app.callback(
    Output('cycle-table', 'children'),
    Output('main-chart', 'figure',allow_duplicate=True),
    Input('analyze-button', 'n_clicks'),
    prevent_initial_call=True
)
def analyze_cycles(n_clicks):
    # Implement code to fetch data from local database and send to Cycle Scanner API
    # Process the response and extract cycle information
    # Create a table to display the results
    if n_clicks is None:
        return None  # No analysis done yet
    
    response = requests.post(f'http://127.0.0.1:5000/analyze-cycles?symbol={symbol}&interval={interval}&start_time={start_time}&end_time={end_time}')
    data = response.json()
    keys = list(data['data']['peaks'][0].keys())
    # Placeholder example data for cycle analysis results
    analysis_results = [
        {"cycle_length": 90, "cycles_detected": 5},
        {"cycle_length": 120, "cycles_detected": 3},
        # Add more results
    ]

    # Create a table to display analysis results
    table_rows = [
    html.Tr([html.Th(i,className="") for i in keys])
    ]
    
    for result in data['data']['peaks']:
        row = html.Tr([html.Td(result[k]/2) if k=='cycleLength' else html.Td(result[k]) for k in keys],style={'background-color': 'white'})
        table_rows.append(row)

    cycle_table = html.Table(table_rows, className="table table-striped table-dark")
    min_bar_num = data['data']['peaks'][0]['minBarNum']
    cycle_length = data['data']['peaks'][0]['cycleLength']
    print('min_bar_num',min_bar_num,cycle_length)
    # Calculate half-cycle length for vertical lines
    half_cycle_length = cycle_length // 2

    # Generate vertical line coordinates based on minBarNum and half-cycle length
    vertical_line_coords = [min_bar_num + i * half_cycle_length for i in range(1, 10)]
    print('vertical_line_coords',vertical_line_coords)
    # Create a scatter plot for vertical lines
    vertical_lines = [go.Scatter(x=[x, x], y=[0, 1], mode='lines', name=f'Line at {x}') for x in vertical_line_coords]

    # Create the main chart with the data and vertical lines
    figure = go.Figure(data=[go.Candlestick(x=df['openTime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
    figure.add_traces(vertical_lines) 
    return cycle_table,figure


if __name__ == '__main__':
    app.run_server(debug=True)
