# This code solves the parallel machine scheduling problem with different arrival time, minimzing the makespan.
# A greedy algorithm is used in greedy_algo
# A LLM-based algorithm is then used in LLM_strategy
# @20240912 Linyan Li

import pandas as pd
from datetime import datetime, timedelta
from zhipuai import ZhipuAI

# LLM 配置
API_KEY = '57614e3d641655a4be9eac8f2d8bdc02.VtiLIRTosZu4cdwX'
client = ZhipuAI(api_key=API_KEY)

# 读取Excel文件
df = pd.read_excel("product_schedule.xlsx")

# 将到达时间转换为日期格式
df['到达时间'] = pd.to_datetime(df['到达时间'], format='%m/%d/%Y')

# 初始化三个车间的可用时间
num_workshops = 3
workshop_free_time = [datetime(2024, 6, 1)] * num_workshops

# 记录每个产品的分配结果
schedule_result = []

# 按到达时间排序
df = df.sort_values(by=['到达时间'])

def greedy_algo(df):
    # 第一部分：贪心算法分配产品到最早空闲的车间
    for index, row in df.iterrows():
        product_id = row['产品']
        arrival_time = row['到达时间']
        processing_days = row['生产天数']

        # 找到当前最空闲的车间（最早可用的车间）
        next_workshop = min(range(num_workshops), key=lambda i: workshop_free_time[i])

        # 计算该车间的开始时间，需确保产品的到达时间晚于当前车间空闲时间
        start_time = max(workshop_free_time[next_workshop], arrival_time)
        end_time = start_time + timedelta(days=processing_days)

        # 更新该车间的空闲时间
        workshop_free_time[next_workshop] = end_time

        # 记录分配情况
        schedule_result.append([product_id, next_workshop + 1, start_time, end_time])

    # 计算贪心算法的总完成时间
    greedy_completion_time = max(workshop_free_time)

    # 输出贪心算法分配结果和总完成时间
    print("贪心算法结果：")
    for result in schedule_result:
        print(f"产品: {result[0]}, 车间: {result[1]}, 开始时间: {result[2]}, 结束时间: {result[3]}")
    print(f"贪心算法所有产品完成的最早时间为: {greedy_completion_time}")



# 第二部分：调用LLM来获取优化策略
# 提取数据，格式化成 LLM 需要的格式
jobs_data = df.apply(lambda row: f"[{row['产品']}, {row['到达时间'].strftime('%Y-%m-%d')}, {row['生产天数']}]", axis=1).tolist()
data_string = ", ".join(jobs_data)

def LLM_strategy(num_workshops):
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {
                "role": "user",
                "content": f"你是一个并行机车间优化专家，data中给出了一个并行机生产车间的相关信息。"
                           f"数据集格式为：产品ID, 到达时间, 生产天数，分别表示工件名称，工件到达时间，该工件生产所需时间。"
                           f"每个工件可以选择任一机器上被加工，目标是尽快完成所有工件。车间数量为：{num_workshops}。"
                           f"数据如下：{data_string}。"
                           f"请确保输出包含所有工件在各机器的具体分配方案，且每个产品的分配方案在列表中仅出现一次。"
                           f"以及每个工件在机器上的开始时间和结束时间。请严格按照以下格式输出json列表，不要包含其他内容，不需要给出任何中间解答过程，直接给出json格式的答案，一定不要有其他任何信息："
                           f"[产品ID, 分配车间, 开始生产时间, 结束生产时间]"
            },
        ]
    )
    return response.choices[0].message.content



llm_result_json = LLM_strategy(num_workshops)
print("下面是大模型产生的json结果"+llm_result_json)
greedy_result_str = "贪心算法结果：\n"
for result in schedule_result:
    greedy_result_str += f"产品: {result[0]}, 车间: {result[1]}, 开始时间: {result[2]}, 结束时间: {result[3]}\n"

final_result_str = '这是贪心的算法的出的答案'+greedy_result_str + "这是大模型生成的答案"+llm_result_json
response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {
                "role": "user",
                "content":f"存在一个问题：有三个一样的车间，想把我这些产品分配到不同的车间，但希望车间效率利用到最高（生产完产品的总时间要尽量小），下面是贪心和llm得出的答案:{final_result_str},请你帮我比较之后得出llm更先进的结论"
            },
        ]
    )
print(response.choices[0].message.content)
