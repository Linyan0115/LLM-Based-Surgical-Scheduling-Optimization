import pandas as pd
import plotly.express as px

# Read the new Excel file
production_data = pd.read_excel('production_records.xlsx')

# 确保产品按顺序排列
production_data = production_data.sort_values(by=['workshop', 'Product'], ascending=[True, False])  # 按照车间和产品降序排列

# 为每个车间分配颜色
color_map = {'Workshop 1': 'blue', 'Workshop 2': 'green', 'Workshop 3': 'red'}
production_data['Color'] = production_data['workshop'].map(color_map)

# 生成甘特图
fig = px.timeline(production_data, x_start='开始生产时间', x_end='结束时间', y='Product', color='workshop')
fig.update_xaxes(categoryorder='total descending')  # 确保产品按降序排列

