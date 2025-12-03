import simpy
import pandas as pd

# read database
data = pd.read_excel('Simpy0613.xlsx')

# 转换 Arrival Time 为相对于模拟开始时间的秒数
start_time = data['Arrival Time'].min()  # 获取最早的到达时间
data['Arrival Time'] = (pd.to_datetime(data['Arrival Time']) - pd.to_datetime(start_time)).dt.days

# 转换 Processing Time 为天数
data['Processing Time'] = data['Processing Time']

# Define the workshop
class Workshop:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine = simpy.Resource(env, capacity=1)  # 每个车间只有一台机器

    def process(self, job_id, production_time):
        print(f'Job {job_id} starts at {self.env.now} in {self.name}')
        yield self.env.timeout(production_time)
        print(f'Job {job_id} finishes at {self.env.now} in {self.name}')

# define the factory
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

            # choose a factory, simple rotational distribution
            workshop = self.workshops[index % len(self.workshops)]
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
