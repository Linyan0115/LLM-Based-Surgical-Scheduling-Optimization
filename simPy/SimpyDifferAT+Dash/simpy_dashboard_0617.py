import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import subprocess

# 启动 Dash 应用程序
app = dash.Dash(__name__)

# 创建 Dash 应用程序布局
app.layout = html.Div([
    html.H1("Workshop Dashboard"),

    # 新增任务输入框和按钮
    html.Div([
        html.H2("Add New Task"),
        dcc.Input(id='product-id', type='text', placeholder='Enter Product ID...'),
        dcc.Input(id='start-time', type='text', placeholder='Enter Start Time...'),
        dcc.Input(id='duration', type='number', placeholder='Enter Duration...'),
        html.Button('Add Task', id='add-task-button', n_clicks=0)
    ]),

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
    [Input('add-task-button', 'n_clicks')],
    [State('product-id', 'value'),
     State('start-time', 'value'),
     State('duration', 'value')]
)
def update_data(n_clicks, product_id, start_time, duration):
    if n_clicks > 0 and all([product_id, start_time, duration]):
        # 读取原始表格
        df = pd.read_excel('Simpy0613.xlsx')

        # 添加新任务
        new_row = pd.DataFrame({'Job ID': [product_id], 'Arrival Time': [start_time], 'Processing Time': [duration]})
        df = pd.concat([df, new_row], ignore_index=True)

        # 写入到原始表格
        df.to_excel('Simpy0613.xlsx', index=False)

        # 运行脚本
        subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.8/bin/python3', 'simpy_0617.py'])
        subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.8/bin/python3', 'simpy_gantt1_0613.py'])
        subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.8/bin/python3', 'simpy_gantt2_0613.py'])

    # 更新数据
    df = pd.read_excel('production_records.xlsx')
    columns = [{'name': i, 'id': i} for i in df.columns]
    data = df.to_dict('records')

    # 更新甘特图
    df_gantt1 = pd.read_excel('production_records.xlsx')
    fig_gantt1 = px.timeline(df_gantt1, x_start='开始生产时间', x_end='结束时间', y='workshop', title='Gantt Chart 1',
                             labels={'Product': 'Product'}, hover_name='Product', color='workshop')
    fig_gantt1.update_layout(xaxis_title='Time', yaxis_title='Workshop')

    df_gantt2 = pd.read_excel('production_records.xlsx')
    df_sorted = df_gantt2.sort_values(by=['workshop', 'Product'], ascending=[True, False])
    color_map = {'Workshop 1': 'blue', 'Workshop 2': 'green', 'Workshop 3': 'red'}
    df_sorted['Color'] = df_sorted['workshop'].map(color_map)
    fig_gantt2 = px.timeline(df_sorted, x_start='开始生产时间', x_end='结束时间', y='Product', color='workshop',
                             title='Gantt Chart 2')
    fig_gantt2.update_xaxes(categoryorder='total descending')

    return columns, data, fig_gantt1, fig_gantt2


if __name__ == '__main__':
    app.run_server(port=8053, debug=True)
