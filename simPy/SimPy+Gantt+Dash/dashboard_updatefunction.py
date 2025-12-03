import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import subprocess
import traceback
import sys


# Initialize Dash application
app = dash.Dash(__name__)

# Define Dash application layout
app.layout = html.Div([
    html.H1("Workshop Dashboard"),

    # Add new task input fields and button
    html.Div([
        html.H2("Add New Task"),
        dcc.Input(id='product-id', type='text', placeholder='Enter Product ID...'),
        dcc.Input(id='start-time', type='text', placeholder='Enter Start Time...'),
        dcc.Input(id='duration', type='number', placeholder='Enter Duration...'),
        html.Button('Add Task', id='add-task-button', n_clicks=0)
    ]),

    # Display original Excel table
    html.Div([
        html.H2("Excel Table"),
        dash_table.DataTable(
            id='table',
            columns=[],  # Will be updated later
            data=[],
        )
    ], style={'width': '40%', 'float': 'right', 'overflowY': 'scroll', 'height': '600px'}),

    # Display Gantt charts
    html.Div([
        html.Div([
            html.H2("Gantt Chart 1"),
            dcc.Graph(id='gantt1-graph'),
        ], style={'width': '60%', 'float': 'left', 'height': '400px'}),
        html.Div([
            html.H2("Gantt Chart 2"),
            dcc.Graph(id='gantt2-graph'),
        ], style={'width': '60%', 'float': 'left', 'height': '400px'})
    ])
])


# Callback function to update Excel table and Gantt charts
@app.callback(
    [Output('table', 'columns'),
     Output('table', 'data'),
     Output('gantt1-graph', 'figure'),
     Output('gantt2-graph', 'figure')],
    [Input('add-task-button', 'n_clicks')],
    [State('product-id', 'value'),
     State('start-time', 'value'),
     State('duration', 'value')]
)
def update_data(n_clicks, product_id, start_time, duration):
    try:
        if n_clicks > 0 and all([product_id, start_time, duration]):
            # Read original table
            df = pd.read_excel('Simpy0605.xlsx')

            # Add new task
            new_row = pd.DataFrame({'Job ID': [product_id], 'Arrival Time': [start_time], 'Processing Time': [duration]})
            df = pd.concat([df, new_row], ignore_index=True)

            # Write to original table
            df.to_excel('Simpy0605.xlsx', index=False)

            # Run subprocesses to update external data and charts
            subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.8/bin/python3', 'simpy_excel.py'])
            subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.8/bin/python3', 'simpy_gantt1.py'])
            subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.8/bin/python3', 'simpy_gantt2.py'])

        # Read updated production records
        df = pd.read_excel('production_records.xlsx')
        columns = [{'name': i, 'id': i} for i in df.columns]
        data = df.to_dict('records')

        # Update Gantt Chart 1
        fig_gantt1 = px.timeline(df, x_start='开始生产时间', x_end='结束时间', y='workshop', title='Gantt Chart 1',
                                 labels={'Product': 'Product'}, hover_name='Product', color='workshop')
        fig_gantt1.update_layout(xaxis_title='Time', yaxis_title='Workshop')

        # Update Gantt Chart 2
        df_sorted = df.sort_values(by=['workshop', 'Product'], ascending=[True, False])
        color_map = {'Workshop 1': 'blue', 'Workshop 2': 'green', 'Workshop 3': 'red'}
        df_sorted['Color'] = df_sorted['workshop'].map(color_map)
        fig_gantt2 = px.timeline(df_sorted, x_start='开始生产时间', x_end='结束时间', y='Product', color='workshop',
                                 title='Gantt Chart 2')
        fig_gantt2.update_xaxes(categoryorder='total descending')

        return columns, data, fig_gantt1, fig_gantt2

    except Exception as e:
        traceback.print_exc()
        return dash.no_update, dash.no_update, {}, {}


if __name__ == '__main__':
    app.run_server(port=8052, debug=True)
