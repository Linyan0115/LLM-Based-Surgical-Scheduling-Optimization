import pandas as pd
import plotly.express as px

# Read the new Excel file
df = pd.read_excel('production_records.xlsx')

# Create the Gantt Chart using Plotly
fig = px.timeline(df,
                  x_start='开始生产时间',
                  x_end='结束时间',
                  y='workshop',
                  title='Workshop Production Schedule',
                  labels={'Product': 'Product'},
                  hover_name='Product', color='workshop')  # 根据车间着色

# Update figure layout
fig.update_layout(xaxis_title='Time', yaxis_title='Workshop')

# Reverse the y-axis to have the chart display from top to bottom
fig.update_yaxes(categoryorder='total ascending')
