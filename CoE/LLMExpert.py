import json
from zhipuai import ZhipuAI
import re
from datetime import datetime
import numpy as np
import random


class LLMExpert(object):
    def __init__(self, name, description, model, client):
        self.name = name
        self.description = description
        self.model = model
        self.client = client
        self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK

        # if hasattr(self, 'BACKWARD_TASK'):
        #     self.backward_prompt_template = self.ROLE_DESCRIPTION + 'n' + self.BACKWARD_TASK

    def api_call(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}],
                tools=None,
                # max_tokens=150,  # Customize this as per your requirements
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error calling Zhipu AI: {e}")
            return ""

    # def forward(self, problem):
    #     # Format the forward prompt
    #     prompt = self.forward_prompt_template.format(problem=problem)
    #     return self.api_call(prompt)

    # def backward(self, **variables):
    #     if hasattr(self, 'backward_prompt_template'):
    #         # Format the backward prompt
    #         prompt = self.backward_prompt_template.format(**variables)
    #         return self.api_call(prompt)
    #     else:
    #         return "Backward task not defined."

    # def __str__(self):
    #     return f'{self.name}: {self.description}'
