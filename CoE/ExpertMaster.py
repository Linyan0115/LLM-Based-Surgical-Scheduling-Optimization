import json
from zhipuai import ZhipuAI
import re
from datetime import datetime
import numpy as np
import random

from LLMExpert import LLMExpert
from CommentPool import CommentPool


#expert_master
# class expert_master(LLMExpert):
#     ROLE_DESCRIPTION = '''您将担任一个多专家系统的指挥官，这是一个艰巨的任务。'''
#     FORWARD_TASK = '''您正在处理一个运筹优化调度问题，具体问题描述如下：
#                       {problem_description}
#                       在解决这个问题的过程中，您有机会咨询多个领域的专家。每个专家在其特定领域具有专门知识，并可以帮助解决不同方面的问题。您的任务是选择下一位您认为对当前问题最有帮助的专家。
#
#                       以下是可供选择的专家及其专业领域：
#                       {experts_info}
#
#                       已经提供过意见的专家有：
#                       {commented_experts}
#
#                       您剩余可选择的专家包括：
#                       {remaining_experts}
#
#
#                      在决策时，请记住：
#                       - 一个调度优化问题的基本解决思路是：1， 了解问题 2，建立数学模型 3，编程调用数学求解器 4，获取结果
#                         这个过程中根据各个expert的comments，会有几次返回并重新调用的过程(例如 程序写完后或者程序结果报错时，需要调用code review expert 进行分析改进)，直至最终得到满意的结果。
#                       - 如果当前comment pool为空，那么首先选择modelling expert，
#                       - 您最多可咨询 {max_collaborate_nums} 位专家
#                       - 您还可以咨询 {remaining_collaborate_nums} 次
#
#                       请根据问题的需求，选择您认为最合适的专家继续咨询。直接输出您选择的专家姓名：
#                       '''
class expert_master(LLMExpert):
    ROLE_DESCRIPTION = '''您将担任一个多专家系统的指挥官，这是一个艰巨的任务。'''
    FORWARD_TASK = '''您正在处理一个运筹优化调度问题，具体问题描述如下：
                      {problem_description}
                      在解决这个问题的过程中，您有机会咨询多个领域的专家。每个专家在其特定领域具有专门知识，并可以帮助解决不同方面的问题。您的任务是选择下一位您认为对当前问题最有帮助的专家。

                      以下是可供选择的专家及其专业领域：
                      {experts_info}

                      已经提供过意见的专家有：
                      {commented_experts}

                      您剩余可选择的专家包括：
                      {remaining_experts}

                    
                    决策逻辑：
                    - 一个调度优化问题的基本解决思路是：1， 了解问题 2，建立数学模型 3，编程调用数学求解器 4，验证和改进，直至获得满意的结果
                        这个过程中根据各个expert的comments，会有几次返回并重新调用的过程(例如 程序写完后或者程序结果报错时，需要调用code review expert 进行分析改进)，直至最终得到满意的结果。
                    - 如果当前comment pool为空，那么首先选择modelling expert，
                    - 您最多可咨询 {max_collaborate_nums} 位专家。
                    - 您还可以咨询 {remaining_collaborate_nums} 次。

                    任务要求：
                      - 准确无误地解析问题的目标函数。
                      - 专家应当精确提取问题中给出的所有具体参数，例如任务处理时间等，专家应该严格按照问题描述中的定义进行建模，以确保模型的准确性。
                      - 对于任务处理时间等具体参数，专家应该严格按照问题描述中的定义进行建模，不得进行假设。
                      - 在编程阶段，programming expert应当使用问题描述中给出的具体参数值，而不是假设任何未明确指出的时间或条件。
                      - 完成编程工作后，必须由code reviewer检查代码的质量和准确性，确保代码符合最佳实践并且没有逻辑错误

                      请根据问题的需求和当前状态，选择您认为最合适的专家继续咨询。直接输出您选择的专家姓名：
                      '''


    def __init__(self, model, client):
        super().__init__(
            name='Conductor',
            description='An special expert that collaborates all other experts.',
            model=model,
            client=client
        )
        # self.llm.max_tokens = 10

    def forward(self, problem, comment_pool, max_collaborate_nums):
        all_experts = comment_pool.all_experts
        all_experts_name = [e.name for e in all_experts]
        commented_experts_name = [c.expert.name for c in comment_pool.comments]

        experts_info = '\n'.join([str(e) for e in all_experts])
        commented_experts = str(commented_experts_name)
        remaining_experts = str(list(set(all_experts_name) - set(commented_experts_name)))

        prompt = self.forward_prompt_template.format(problem_description=problem,
                                                     experts_info=experts_info,
                                                     commented_experts=commented_experts,
                                                     remaining_experts=remaining_experts,
                                                     max_collaborate_nums=max_collaborate_nums,
                                                     remaining_collaborate_nums=max_collaborate_nums - len(
                                                         commented_experts)
                                                     )
        answer = self.api_call(prompt)

        expert_name_to_obj = {e.name: e for e in all_experts}
        for name, expert in expert_name_to_obj.items():
            if name in answer:
                return expert

        print('Can not find expert, random choice!')
        return random.choice(list(expert_name_to_obj.values()))


class code_Return(LLMExpert):
    ROLE_DESCRIPTION = 'You are an expert that responsible for summarize the comment of all other experts then conclude the final answer'
    FORWARD_TASK = '''
                  现在，您是一名运筹学专家，熟练掌握这个领域编程及实现。
                  您是这个experts system的最后一个expert，需要给出一个问题的最终代码。
                  问题的文字描述：{problem_description}
                  您的同事都是各个相关领域的专家。他们给出了自己的见解。我希望您在给出最终代码时仔细参考这些注释：
                  {comments_text}

                  除了导入包（无测试代码）外，函数外部不需要任何代码。
                  您的最终代码如下：
                      '''

    # Now, you are an expert of Operations Research.
    #               You are supposed to give the final code of an problem.
    #               Text description of the problem: {problem_description}
    #               Your colleagues are all experts in various related fields. They have given their own insights. I hope you will carefully refer to these comments when giving the final code:
    #               {comment_text}

    #               No code is required outside the function except for the import package (No test code).
    #               Your final code is as following:
    #               '''

    def __init__(self, model, client):
        super().__init__(
            name='Solver',
            description='Reduce all comments given by other experts',
            model=model,
            client=client
        )

    def forward(self, problem, comment_pool):
        self.problem = problem
        comments_text = comment_pool.get_current_comment_text()
        prompt = self.FORWARD_TASK.format(
            problem_description=problem,
            comments_text=comments_text
        )
        output = self.api_call(prompt)

        return output


class CodeReviewer(LLMExpert):
    ROLE_DESCRIPTION = 'You are a code reviewer that conducts thorough reviews of the implemented code to identify any errors, inef- ficiencies, or areas for improvement.'
    FORWARD_TASK = '''
                  作为代码审查员，您的职责是对已实施代码进行全面审查。
                  您将识别代码中可能的错误、效率低下或需要改进的地方，确保其遵循最佳实践并提供最佳结果。
                  这是使用python调用Cplex的code。其中的核心代码包含建立模型，建立决策变量，目标函数以及约束条件。
                  请你认真检查这份代码，确保其可以运行。
                  您应该参考同事从其他方面给出的评论：{comments_text}
                '''

    def __init__(self, model, client):
        super().__init__(
            name='Code Reviewer',
            description='Skilled in programming and coding, capable of implementing the optimization solution in python +cplex programming language.',
            model=model,
            client=client
        )

    def forward(self, problem, comment_pool):
        self.problem = problem
        comments_text = comment_pool.get_current_comment_text()
        prompt = self.FORWARD_TASK.format(
            problem_description=problem,
            comments_text=comments_text
        )
        output = self.api_call(prompt)

        return output