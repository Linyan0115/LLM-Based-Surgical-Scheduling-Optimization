import sys
sys.path.append("/usr/local/lib/python3.8/site-packages")  # simpy 模块的安装路径
import simpy
import pandas as pd

# 读取数据库
data = pd.read_excel('Simpy0613.xlsx', dtype={'Arrival Time': 'datetime64[ns]'})

# 转换 Arrival Time 为相对于模拟开始时间的秒数
start_time = pd.to_datetime('2024-06-01')
data['Arrival Time'] = (pd.to_datetime(data['Arrival Time']) - start_time).dt.days

# 增加一个唯一标识符列
data['Unique ID'] = data.index

# 定义车间
class Workshop:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine = simpy.Resource(env, capacity=1)  # 每个车间只有一台机器
        self.next_available_time = 0  # 记录车间的下一个可用时间点
        self.production_records = []  # 用于记录生产信息

    def process(self, job_id, production_time):
        start_time = self.env.now
        # print(f'Job {job_id} starts at {start_time} in {self.name}')
        yield self.env.timeout(production_time)
        end_time = self.env.now
        # print(f'Job {job_id} finishes at {end_time} in {self.name}')
        # 记录生产信息
        self.production_records.append({
            "workshop": self.name,
            "Product": job_id,
            "开始生产时间": start_time,
            "结束时间": end_time
        })

# 定义工厂
class Factory:
    def __init__(self, env, data, num_workshops):
        self.env = env
        self.data = data
        self.workshops = [Workshop(env, f'Workshop {i+1}') for i in range(num_workshops)]

    def allocate_product(self):
        for index, row in self.data.iterrows():
            arrival_time = row['Arrival Time']
            production_time = row['Processing Time']
            job_id = row['Job ID']

            # Wait until the arrival time of the current job
            yield self.env.timeout(arrival_time - self.env.now)

            # Select the earliest available workshop
            workshop = min(self.workshops, key=lambda w: max(w.next_available_time, self.env.now))
            start_time = max(workshop.next_available_time, self.env.now)
            workshop.next_available_time = start_time + production_time
            self.env.process(self.process_product(workshop, job_id, production_time))

    def process_product(self, workshop, job_id, production_time):
        with workshop.machine.request() as request:
            yield request
            yield self.env.process(workshop.process(job_id, production_time))

# 模拟参数
num_workshops = 3

# 创建 SimPy 环境
env = simpy.Environment()

# 创建工厂
factory = Factory(env, data, num_workshops)

# 分配产品
env.process(factory.allocate_product())

# 运行模拟
env.run()

# 创建生产记录的 DataFrame
records = []
for workshop in factory.workshops:
    records.extend(workshop.production_records)

# 创建 DataFrame
df = pd.DataFrame(records)

# 转换 '开始生产时间' 和 '结束时间' 为 datetime 格式
df['开始生产时间'] = start_time + pd.to_timedelta(df['开始生产时间'], unit='D')
df['结束时间'] = start_time + pd.to_timedelta(df['结束时间'], unit='D')

# 按产品 ID 排序
df = df[['Product', 'workshop', '开始生产时间', '结束时间']].sort_values(by='Product')

# 保存 DataFrame 到 Excel
df.to_excel('production_records.xlsx', index=False)