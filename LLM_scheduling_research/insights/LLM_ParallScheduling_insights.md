20.Nov

1.Experts

-   Data process expert: Organize the information: clean data, transfer data to correct JSON type.
-   Allocation expert:
-   Prediction expert

16.Oct

Problem Description

parallel machine scheduling

point of pain

Present:

Many products are overdue, and emergency products are difficult to schedule in workshops.

Future:

Non-future predictions & different parts are handled individually.

Part 1: Deterministic parallel machine scheduling

1.1 Different arrival time & unit date & no due date (Done)

Greedy (heuristic)

贪心算法，永远选择当前最空闲的车间安排生产

LLM(heuristic)

自由选择策略使得总生产时间尽可能的短

阶段总结：LLM provides a strategic product ending production earlier than the greedy algorithm

1.2 Different arrival time & unit date & different due date

Due date = （arrival time + process time）\* 系数

Why due date?

单纯比较贪心算法和LLM策略太单一，不能突出优势

greedy has a hard time fixing overruns

LLM might be able to fix it

优先分配临期产品 & 紧急产品（DDL = AT + PT）

根据产品类型总结超期概率，在预测的时候动态调整系数（比如刚开始默认商家的订单DDL的系数都是a，但是该类产品存在超期现象较严重，LLM解决当前超期问题后，在后续生产和预测的时候根据超期情况可以不断调整系数a，进一步优化schedule）（简之：在出现问题前解决问题）

Part 2: Online parallel machine scheduling

What is online: some jobs are processing, some are scheduled but not processing, some will come but don’t know detail information

Predict + CPLEX：

根据产品类型进行预测（ML）

使用LLM建议的系数和分配策略对未来一段时间内可能到来的产品进行分配

目前的初步思路是将LLM运用到ML和CPLEX中，如下图：

![](images/图片%201.png)

Part 3: AI Agent

Previously discussed

自语言处理

情景模拟

不确定预测

多目标化

调度策略

参数生成，改进

CPLEX

我的想法：参考paper “Chain-of-Experts”

Experts：

Terminology Interpreter：

Parameter Extraction Expert

Variable Extraction Expert

Constraint Extraction Expert

Code Reviewer

Conductor

Forward Thought Construction：选择合适的专家来完成不同的任务

backward Reflection Mechanism：错误回溯

结合我们的project，也许可以：

![](images/图片%202.png){width="620"}

只是一个探索的方向，还需要再多找一些paper

1.  Core Innovations of the Chain-of-Experts (CoE) Framework

Multi-Agent Collaboration: CoE introduces a multi-agent framework where each agent, referred to as an "expert," specializes in a specific aspect of OR problem-solving. Unlike traditional single-agent models that attempt to solve a problem holistically, CoE divides the task among specialized agents, such as terminology interpreters, modeling experts, and programming experts. Each expert focuses on one part of the problem-solving process, leading to more accurate and efficient solutions.

Role of the Conductor: The Conductor is a central coordinator that manages the sequence of interactions among the experts. It decides which expert to consult at each step, based on the current problem state and the contributions from previous experts. This orchestration ensures that the experts work together systematically, constructing a chain of reasoning that combines their specialized skills.

Forward Thought Construction and Backward Reflection:

Forward Thought Construction involves the sequential selection of experts to build a solution step by step. For example, a terminology expert may first clarify terms, followed by a modeling expert who converts this understanding into a mathematical model.

Backward Reflection allows the system to revise its previous steps based on external feedback or errors detected during execution. If a solution does not work as expected, experts review their steps and refine their output. This iterative refinement helps correct mistakes and improves the solution quality.

2.  Role of Large Language Models (LLMs)

The CoE framework relies on LLMs like GPT-3.5-turbo to implement the reasoning capabilities of each expert. Each expert is essentially a large language model fine-tuned or prompted to focus on specific tasks (e.g., interpreting terms, generating code). The LLM’s ability to understand natural language and generate text is leveraged to perform tasks like understanding problem descriptions, translating them into mathematical formulations, and generating code for optimization problems.

GPT-3.5-turbo as the Base Model: The system described in the paper uses GPT-3.5-turbo as the primary LLM for these expert roles. This LLM provides a robust base for tasks that require natural language understanding and generation, such as interpreting complex OR problem descriptions and generating Python code for optimization models.

Specialized Knowledge Integration: Each LLM-based expert can access domain-specific knowledge bases or documentation (e.g., Gurobi API documentation for programming experts), which helps it generate more accurate and contextually relevant responses. This is particularly useful in operations research, where external knowledge of optimization techniques is essential.

3.  Why is This Innovative?

Overcoming Single-Agent Limitations: Traditional LLMs or single-agent models struggle with complex problems that require deep domain knowledge, multi-step reasoning, and handling implicit constraints. CoE addresses these limitations by using multiple agents that each contribute their expertise to different aspects of the problem.

Structured Problem Solving: The structured approach of CoE, where experts are guided through a controlled process by the Conductor, allows for better handling of long chains of reasoning. This leads to more precise solutions, as each step can be reviewed and corrected if necessary.

Iterative Improvement Through Reflection: The backward reflection mechanism is particularly innovative because it allows the system to iteratively refine its output. This self-correcting feature makes CoE more adaptable and capable of improving its solutions over time, which is crucial for dealing with the intricacies of real-world OR problems.

Summary of the CoE System's Innovation

The Innovation: CoE introduces a novel way of solving complex problems by combining the power of multiple specialized LLM agents with a coordinating Conductor. It uses forward and backward reasoning to build solutions and correct errors dynamically.

Role of LLMs: LLMs like GPT-3.5-turbo power the individual experts, enabling them to perform specialized reasoning and knowledge retrieval. The Conductor coordinates these LLM-based experts to create a cohesive and dynamic problem-solving process.

Pull Request Test
