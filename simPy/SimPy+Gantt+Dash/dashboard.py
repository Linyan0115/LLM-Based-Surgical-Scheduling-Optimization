import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import subprocess

# 启动 Dash 应用程序
app = dash.Dash(__name__)

# 创建 Dash 应用程序布局
app.layout = html.Div([
    html.H1("Workshop Dashboard"),

    # 展示原始 Excel 表格
    html.Div([
        html.H2("Excel Table"),
        dash_table.DataTable(
            id='table',
            columns=[],  # 空列，稍后将被更新
            data=[],
        )
    ], style={'width': '40%', 'float': 'right', 'overflowY': 'scroll', 'height': '600px'}),

    # 展示甘特图
    html.Div([
        html.Div([
            html.H2("Gantt Chart"),
            dcc.Graph(id='gantt1-graph'),
        ], style={'width': '60%', 'float': 'left', 'height': '400px'}),
        html.Div([
            html.H2("Gantt Chart 2"),
            dcc.Graph(id='gantt2-graph'),
        ], style={'width': '60%', 'float': 'left', 'height': '400px'})
    ])
])


# 回调函数来更新 Excel 表格和甘特图
@app.callback(
    [Output('table', 'columns'),
     Output('table', 'data'),
     Output('gantt1-graph', 'figure'),
     Output('gantt2-graph', 'figure')],
    [Input('table', 'id')]
)
def load_excel_data(_):
    df = pd.read_excel('production_records.xlsx')
    columns = [{'name': i, 'id': i} for i in df.columns]
    data = df.to_dict('records')

    subprocess.run(['python', 'step 2.1 simpy+Gantt1.py'])
    subprocess.run(['python', 'step 2.2 simpy+Gantt2.py'])

    df_gantt1 = pd.read_excel('production_records.xlsx')
    fig_gantt1 = px.timeline(df_gantt1, x_start='开始生产时间', x_end='结束时间', y='workshop', title='Gantt Chart 1',
                             labels={'Product': 'Product'}, hover_name='Product', color='workshop')
    fig_gantt1.update_layout(xaxis_title='Time', yaxis_title='Workshop')

    df_gantt2 = pd.read_excel('production_records.xlsx')
    df_sorted = df_gantt2.sort_values(by=['workshop', 'Product'], ascending=[True, False])
    color_map = {'Workshop 1': 'blue', 'Workshop 2': 'green', 'Workshop 3': 'red'}
    df_sorted['Color'] = df_sorted['workshop'].map(color_map)
    fig_gantt2 = px.timeline(df_sorted, x_start='开始生产时间', x_end='结束时间', y='Product', color='workshop', title='Gantt Chart 2')
    fig_gantt2.update_xaxes(categoryorder='total descending')

    return columns, data, fig_gantt1, fig_gantt2


if __name__ == '__main__':
    app.run_server(port=8051, debug=True)