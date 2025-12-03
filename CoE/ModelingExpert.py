import json
from zhipuai import ZhipuAI
import re
from datetime import datetime
import numpy as np
import random

from LLMExpert import LLMExpert

class ModelingExpert(LLMExpert):

    ROLE_DESCRIPTION = '您是运筹学和优化领域的建模专家。您的专长是混合整数规划 (MIP) 模型，并且对运筹学领域的各种建模技术有着深入的了解。目前，您将面临一个运筹学领域的调度问题，以及其他专家提供的额外见解。目标是全面整合这些输入并设计一个解决给定生产调度的综合模型。'

    FORWARD_TASK = '''
      您是运筹学和优化领域的建模专家。您的专长是混合整数规划 (MIP) 模型，并且对运筹学领域的各种建模技术有着深入的了解。目前，您将面临一个运筹学领域的调度问题，以及其他专家提供的额外见解。目标是全面整合这些输入并设计一个解决给定生产调度的综合模型。
      现在原始问题如下：
      {problem_description}
      其他专家的评论如下：
      {comments_text}

      给出这个问题的混合整数规划(MIP)模型。另外，请注意，您的模型需要是可解的线性规划模型或混合整数规划模型。这也意味着约束条件的表达式只能是等于、大于或等于或小于或等于（> 或 < 不允许出现，应替换为 \geq 或 \leq）。
      
      # 要求：
      # - 准确解析问题描述：请严格依据问题描述中的具体内容进行建模，包括但不限于任务处理时间、机器数量等具体参数，不得进行任何未经证实的假设。
      # - 构建线性或混合整数线性规划模型：确保所构建的模型是一个可解的线性规划模型或混合整数规划模型。这意味着所有的约束条件必须为线性的，并且表达式只能是等于 ($=$)、大于或等于 ($\geq$) 或小于或等于 ($\leq$)。不允许出现严格的不等式符号 $>$ 或 $<$。
      # - 定义清晰的目标函数：基于问题描述中的目标（如最小化最大完成时间），定义一个精确的目标函数。
      
      您的输出格式应该是这样的 JSON：
      {{
      "VARIABLES": "关于变量的数学描述",
      "CONSTRAINS": "关于约束的数学描述",
      "OBJECTIVE": "关于目标的数学描述"
      }}
    '''

    BACKWARD_TASK = '''When you are solving a problem, you get a feedback from the external environment. You need to judge whether this is a problem caused by you or by other experts (other experts have given some results before you). If it is your problem, you need to give Come up with solutions and refined code.
      The original problem is as follow:
      {problem_description}

      The feedback is as follow:
      {feedback}

      The modeling you give previously is as follow:
      {previous_modeling}

      The output format is a JSON structure followed by refined code:
      {{
          "is_caused_by_you": false,
          "reason": "leave empty string if the problem is not caused by you",
          "refined_result": "Your refined result"
      }}
      '''

    def __init__(self,  model ,client):
        super().__init__(
            name='Modeling Expert',
            description='Proficient in constructing mathematical optimization models based on the extracted information.',
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

        # Meet the rule of MIP
        output = output.replace(' < ', ' \leq ').replace(' > ', ' \geq ')
        self.previous_answer = output
        return output

    def backward(self, feedback_pool):
        if not hasattr(self, 'problem'):
            raise NotImplementedError('Please call foward first!')
        output = self.backward_chain.predict(
            problem_description=self.problem['description'],
            previous_answer=self.previous_answer,
            feedback=feedback_pool.get_current_comment_text())
        return output

