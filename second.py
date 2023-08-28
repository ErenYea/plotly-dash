import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# Create a Dash app instance
app = dash.Dash(__name__)

# Sample data
data = {'x': [1, 2, 3, 4, 5],
        'y': [5, 7, 1, 3, 8]}

df = pd.DataFrame(data)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Simple Dash Plotly App"),
    dcc.Graph(
        id='simple-graph',
        figure=px.line(df, x='x', y='y', title='Simple Line Plot')
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
