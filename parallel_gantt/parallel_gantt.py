import sys
sys.path.append("/usr/local/lib/python3.8/site-packages")  # simpy 模块的安装路径
import simpy
import pandas as pd
import plotly.express as px

class Workshop:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine = simpy.Resource(env, capacity=1)  # 每个车间只有一台机器
        self.production_records = []  # 用于记录生产信息
        self.total_production_time = 0  # 记录车间累计生产时间
        self.last_end_time = 0  # 上一个工序结束时间
        self.last_free_time = 0  # 上一个工序分配车间的空闲时间
        self.next_free_time = 0  # 车间下一个空闲时间

    def process(self, job_id, production_time, start_time):
        yield self.env.timeout(production_time)
        end_time = start_time + production_time  # 计算结束时间
        # 记录生产信息
        self.production_records.append({
            "workshop": self.name,
            "Product": job_id,
            "开始生产时间": start_time,
            "结束时间": end_time  # 结束时间为开始时间加生产天数
        })
        self.total_production_time = end_time  # 更新累计生产时间
        self.last_end_time = end_time  # 更新上一次结束时间
        print(f"产品 {job_id} 分配到 {self.name}")
        self.last_free_time = self.next_free_time  # 更新上一次分配车间的空闲时间


class Factory:
    def __init__(self, env, data, num_workshops):
        self.env = env
        self.data = data
        self.num_workshops = num_workshops
        self.workshops = [Workshop(env, f'Workshop {i + 1}') for i in range(num_workshops)]
        self.next_free_time = [0] * num_workshops  # 存储每个车间的最早空闲时间

    def allocate_product(self):
        for index, row in self.data.iterrows():
            job_id = row['产品']
            arrival_time = row['到达时间']
            production_time = row['生产天数']

            # 等待当前产品的到达时间
            if arrival_time > self.env.now:
                yield self.env.timeout(arrival_time - self.env.now)

            # 找到最空闲的车间
            least_busy_workshop_index = min(range(self.num_workshops),
                                            key=lambda i: self.next_free_time[i])
            least_busy_workshop = self.workshops[least_busy_workshop_index]

            with least_busy_workshop.machine.request() as request:
                yield request
                current_time = self.env.now
                start_time = max(arrival_time, self.next_free_time[least_busy_workshop_index])
                delay = max(0, start_time - current_time)
                yield self.env.timeout(delay)

                least_busy_workshop.next_free_time = start_time + production_time

                yield self.env.process(least_busy_workshop.process(job_id, production_time, start_time))

                self.next_free_time[least_busy_workshop_index] = start_time + production_time

            self.data = self.data.drop(index)


class GanttChart:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path)

    def preprocess_data(self, start_time):
        self.df['开始生产时间'] = pd.to_datetime(self.df['开始生产时间'])
        self.df['结束时间'] = pd.to_datetime(self.df['结束时间'])
        self.df = self.df[['Product', 'workshop', '开始生产时间', '结束时间']].sort_values(by=['Product'])
        self.products_sorted = self.df['Product'].unique()[::-1]

    def generate_chart(self):
        fig = px.timeline(
            self.df,
            x_start="开始生产时间",
            x_end="结束时间",
            y="Product",
            color="workshop",
            title="生产甘特图",
            hover_name="workshop",
            category_orders={'Product': self.products_sorted}
        )
        fig.update_layout(
            xaxis_title="时间",
            yaxis_title="产品",
            legend_title="车间",
            yaxis={'categoryorder': 'array', 'categoryarray': self.products_sorted},
            showlegend=True
        )
        fig.show()


def main():
    # 读取数据库
    data = pd.read_excel('product_schedule.xlsx', dtype={'到达时间': 'datetime64[ns]'})

    # 转换 到达时间 为相对于模拟开始时间的天数
    start_time = pd.to_datetime('2024-06-01')
    data['到达时间'] = (pd.to_datetime(data['到达时间']) - start_time).dt.days

    # 增加一个唯一标识符列
    data['Unique ID'] = data.index

    # 模拟参数
    num_workshops = 3

    # 创建 SimPy 环境
    env = simpy.Environment()

    # 创建工厂并分配产品
    factory = Factory(env, data, num_workshops)
    env.process(factory.allocate_product())
    env.run()

    # 创建生产记录的 DataFrame
    records = []
    for workshop in factory.workshops:
        records.extend(workshop.production_records)

    df = pd.DataFrame(records)
    df['开始生产时间'] = start_time + pd.to_timedelta(df['开始生产时间'], unit='D')
    df['结束时间'] = start_time + pd.to_timedelta(df['结束时间'], unit='D')

    df = df[['Product', 'workshop', '开始生产时间', '结束时间']].sort_values(by=['Product'])
    df.to_excel('production_records.xlsx', index=False)

    # 使用甘特图类生成图表
    gantt_chart = GanttChart('production_records.xlsx')
    gantt_chart.preprocess_data(start_time)
    gantt_chart.generate_chart()


if __name__ == "__main__":
    main()
