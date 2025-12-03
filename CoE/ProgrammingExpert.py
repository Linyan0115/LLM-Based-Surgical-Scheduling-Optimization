import json
from zhipuai import ZhipuAI
import re
from datetime import datetime
import numpy as np
import random

from LLMExpert import LLMExpert

class ProgrammingExpert(LLMExpert):
# Here is a starter code:{code_example}
    ROLE_DESCRIPTION = 'You are a Python programmer in the field of operations research and optimization. Your proficiency in utilizing IBM ILOG Cplex is essential. In addition to your expertise in Cplex, it would be great if you could also provide some background in related libraries or tools, like NumPy, SciPy.'
    FORWARD_TASK = '''
                    给你一个特定的问题。你的目标是开发一个有效的 Python+DoCplex 程序来解决给定的问题。
                    现在原始数学模型以及其他experts的评论如下:
                    {comments_text}
                    让我们一步一步分析数学模型，综合其他experts的评论，然后给出你的 Python 代码，导入包需要时DoCplex+Cplex。
                    请直接给出你的 Python 代码。
                    除了导入包（无测试代码）之外，函数之外不需要任何代码。在你的代码中，模型必须是可解的 LP 或 MIP 模型。
                  '''

    BACKWARD_TASK = '''
                当你在解决问题时，你会得到来自外部环境的反馈，你需要判断这个问题是你造成的，还是其他专家造成的（其他专家在你之前已经给出了一些结果），如果是你的问题，你需要给出解决方案和精炼代码。
                你之前给出的答案如下：
                {previous_answer}

                反馈如下：
                {feedback}

                输出格式为 JSON 结构，后跟精炼代码：
                {{
                'is_caused_by_you': false,
                'reason': '如果问题不是你造成的，请留空字符串',
                'refined_code': '你的精炼答案...'
                }}
            '''

    def __init__(self, model, client):
        super().__init__(
            name='Programming Expert',
            description='Skilled in programming and coding, capable of implementing the optimization solution in a programming language.',
            model=model,
            client = client
        )

    def forward(self, problem, comment_pool):
        self.problem = problem
        comments_text = comment_pool.get_current_comment_text()
        prompt = self.FORWARD_TASK.format(
            problem_description=problem,
            comments_text=comments_text
        )
        output = self.api_call(prompt)
        self.previous_code = output

        return output

    def backward(self, feedback_pool):
        if not hasattr(self, 'problem'):
            raise NotImplementedError('Please call foward first!')
        prompt = self.BACKWARD_TASK.format(
            previous_code=self.previous_code,
            feedback=feedback_pool.get_current_comment_text()
        )
        output = self.api_call(prompt)

        return output

