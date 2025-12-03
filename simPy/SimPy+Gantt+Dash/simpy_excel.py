import sys
sys.path.append("/usr/local/lib/python3.8/site-packages")  # simpy 模块的安装路径
import simpy
import pandas as pd


# read database
# data = pd.read_excel('Simpy0605.xlsx')
data = pd.read_excel('Simpy0605.xlsx', dtype={'Arrival Time': 'datetime64[ns]'})

# 转换 Arrival Time 为相对于模拟开始时间的秒数
start_time = pd.to_datetime('2024-06-01')
data['Arrival Time'] = (pd.to_datetime(data['Arrival Time']) - start_time).dt.days

# 转换 Processing Time 为天数
data['Processing Time'] = data['Processing Time']

# Define the workshop
class Workshop:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine = simpy.Resource(env, capacity=1)  # 每个车间只有一台机器
        self.total_processing_time = 0  # 记录车间的总处理时间
        self.production_records = []  # 用于记录生产信息

    def process(self, job_id, production_time):
        start_time = self.env.now
        #print(f'Job {job_id} starts at {start_time} in {self.name}')
        yield self.env.timeout(production_time)
        end_time = self.env.now
        self.total_processing_time -= production_time  # 减少当前任务的处理时间
        #print(f'Job {job_id} finishes at {end_time} in {self.name}')
        # 记录生产信息
        self.production_records.append({
            "workshop": self.name,
            "Product": job_id,
            "开始生产时间": start_time,
            "结束时间": end_time
        })

# Define the factory
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

            # choose a workshop with the minimum load
            workshop = min(self.workshops, key=lambda w: w.total_processing_time)
            workshop.total_processing_time += production_time  # 增加分配任务的处理时间
            env.process(self.process_product(workshop, job_id, arrival_time, production_time))

    def process_product(self, workshop, job_id, arrival_time, production_time):
        yield self.env.timeout(arrival_time)
        with workshop.machine.request() as request:
            yield request
            yield env.process(workshop.process(job_id, production_time))

# Simulation parameters
num_workshops = 3

# Create the SimPy environment
env = simpy.Environment()

# Create the factory
factory = Factory(env, data, num_workshops)

# allocate products
factory.allocate_product()

# Run the simulation
env.run()

# Create DataFrame for production records
records = []
for workshop in factory.workshops:
    records.extend(workshop.production_records)

# Create DataFrame
df = pd.DataFrame(records)

# Convert '开始生产时间' and '结束时间' to datetime format
df['开始生产时间'] = start_time + pd.to_timedelta(df['开始生产时间'], unit='D')
df['结束时间'] = start_time + pd.to_timedelta(df['结束时间'], unit='D')

# sort excel
df = df[['Product', 'workshop', '开始生产时间', '结束时间']].sort_values(by='Product')

# Save DataFrame to Excel
df.to_excel('production_records.xlsx', index=False)