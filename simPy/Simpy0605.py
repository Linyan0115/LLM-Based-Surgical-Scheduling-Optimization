import simpy
import pandas as pd

# read database
data = pd.read_excel('Simpy0605.xlsx')

# 转换 Arrival Time 为相对于模拟开始时间的天数
start_date = data['Arrival Time'].min()  # 获取最早的到达日期
data['Arrival Time'] = (pd.to_datetime(data['Arrival Time']) - pd.to_datetime(start_date)).dt.days

# 转换 Processing Time 为天数
data['Processing Time'] = data['Processing Time']  # 假设已经是天数


# 定义车间
class Workshop:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine = simpy.Resource(env, capacity=1)
        self.next_free_time = 0

    def process(self, job_id, production_time):
        print(f'Job {job_id} starts at {self.env.now} in {self.name}')
        yield self.env.timeout(production_time)
        self.next_free_time = self.env.now
        print(f'Job {job_id} finishes at {self.env.now} in {self.name}')


# 定义工厂
class Factory:
    def __init__(self, env, data, num_workshops):
        self.env = env
        self.data = data
        self.workshops = [Workshop(env, f'Workshop {i + 1}') for i in range(num_workshops)]

    def allocate_product(self):
        for index, row in self.data.iterrows():
            arrival_time = row['Arrival Time']
            production_time = row['Processing Time']
            job_id = row['Job ID']
            self.env.process(self.process_product(job_id, arrival_time, production_time))

    def process_product(self, job_id, arrival_time, production_time):
        yield self.env.timeout(arrival_time)

        while True:
            # 找到预计最早空闲的车间
            workshop = min(self.workshops, key=lambda ws: max(ws.next_free_time, self.env.now))
            if max(workshop.next_free_time, self.env.now) <= self.env.now:
                with workshop.machine.request() as request:
                    yield request
                    yield self.env.process(workshop.process(job_id, production_time))
                break
            else:
                # 如果没有空闲的车间，等待最早空闲的车间
                yield self.env.timeout(max(workshop.next_free_time, self.env.now) - self.env.now)


# 自定义车间数量
num_workshops = 3

# 创建模拟环境
env = simpy.Environment()

# 创建工厂实例（优化分配）
factory_optimized = Factory(env, data, num_workshops)

# 分配产品（优化分配）
factory_optimized.allocate_product()

# 运行模拟（优化分配）
env.run()
