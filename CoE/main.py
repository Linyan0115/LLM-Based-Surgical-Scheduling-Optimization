import json
from zhipuai import ZhipuAI
import re
from datetime import datetime
import numpy as np
import random

from LLMExpert import LLMExpert
from CommentPool import CommentPool
from CommentPool import Comment
from ExpertMaster import expert_master
from ModelingExpert import ModelingExpert
from ProgrammingExpert import ProgrammingExpert
from ExpertMaster import code_Return
from ExpertMaster import CodeReviewer

def extract_code_from_string(input_string):
    # Match code within ```python ... ``` or ``` ... ``` blocks
    pattern = r'```(?:python)?\s*(.*?)\s*```'

    # Find all matches in the input string
    code_blocks = re.findall(pattern, input_string, re.DOTALL)

    if len(code_blocks) == 0:
        # print(f'Parse code error! {input_string}')
        return input_string
    elif len(code_blocks) == 1:
        return code_blocks[0]

    code_blocks = [code for code in code_blocks if 'pip' not in code]
    return '\n'.join(code_blocks)



def chain_of_experts(problem, max_collaborate_nums, client, model_name, enable_reflection, max_trials):
    """Run Chain of Experts pipeline
    Args:
        problem: a dict of problem_description and code_example.
    Return:
        code: code of problem
    """
    all_experts = [
        ModelingExpert(model_name, client),
        ProgrammingExpert(model_name, client),
        CodeReviewer(model_name, client),
        # ProgrammingExampleProvider(model_name),
        # ModelingKnowledgeSupplementExpert(model_name),
    ]

    num_experts = len(all_experts)
    # build the class objects

    # this one is used to summarize all the codes, and give the final one. no chain again
    return_code = code_Return(model_name,client)

    comment_pool = CommentPool(all_experts, visible_matrix=np.ones((num_experts, num_experts)))

    master_Class = expert_master(model_name, client)

    expert_stack = []

    for _ in range(max_trials):
        for _ in range(max_collaborate_nums):
            # based on the problem and comment, choose the next expert
            next_expert = master_Class.forward(problem, comment_pool, max_collaborate_nums)
            print(f'Choose next expert: {next_expert.name}')

            # no matter which kind of expert it return, it need to execute the forward function, and return comment
            comment_text = next_expert.forward(problem, comment_pool)
            print(f'Given comment:\n{comment_text}')

            # add the comment dict into pool
            comment_pool.add_comment(Comment(next_expert, comment_text))
            expert_stack.append(next_expert)
        # return the code
        answer = return_code.forward(problem, comment_pool)
        code = extract_code_from_string(answer)
        with open('generated_code.py', 'w', encoding='utf-8') as f:
            f.write(code)

    return 0  # answer



def main():
    problem = '''
          我们有一个制造工厂，需要在2台相同的机器上加工5个不同的任务。每个任务都有一定的处理时间，目标是找到一种任务分配方案，使得所有任务完成的时间尽可能早，即最小化最大完成时间（makespan）。
          以下是五个任务与机器需要对这五个任务加工的时间:
          任务A: 10分钟,
          任务B: 6分钟,
          任务C: 8分钟,
          任务D: 12分钟,
          任务E: 5分钟,
          机器有机器1,机器2,
          所有的任务都可以从时刻0开始.
          目标设计一个调度方案，将上述5个任务分配给这2台机器，目标是最小化所有任务完成的最大时间（makespan）。
          '''

    #   {

    #     'problem':'A clinic makes batches of vitamin shots and pills. Each batch of vitamin shots requires 30 units of vitamin C and 40 units of vitamin D. Each batch of vitamin pills requires 50 units of vitamin C and 30 units of vitamin D. Since pills are more popular, the number of batches of vitamin pills must be larger than the number of batches of vitamin shots. Further, the clinic can make at most 10 batches of vitamin shots. The clinic has available 1200 units of vitamin C and 1500 units of vitamin D. If each batch of vitamin shots can supply 10 people and each batch of vitamin pills can supply 7 people, how many batches of each should be made to maximize the number of people that can be supplied?',
    #            'code_example':'pass'
    # }

    API_KEY = '57614e3d641655a4be9eac8f2d8bdc02.VtiLIRTosZu4cdwX'
    MODEL_NAME = "GLM-4-Flash"
    client = ZhipuAI(api_key=API_KEY)
    chain_of_experts(problem, 3, client, model_name=MODEL_NAME, enable_reflection=False, max_trials=1)

main()