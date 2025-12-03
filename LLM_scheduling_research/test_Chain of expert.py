import pandas as pd
from datetime import datetime, timedelta
from zhipuai import ZhipuAI
import json

# Initialize the LLM client
API_KEY = "57614e3d641655a4be9eac8f2d8bdc02.VtiLIRTosZu4cdwX"
client = ZhipuAI(api_key=API_KEY)


# Data Processing Expert
class DataProcessingExpert:
    def __init__(self, client):
        self.client = client

    def process_data(self, raw_data):
        # Convert raw data to string
        data_string = json.dumps(raw_data)

        # Call LLM
        response = self.client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "user",
                    "content": f"You are a data processing expert. The raw data is: {data_string}. "
                               f"Please perform the following tasks: "
                               f"1. Ensure the time fields are in standard datetime format. "
                               f"2. Fill missing due dates (arrival time + production days). "
                               f"3. Sort the data by arrival time in ascending order. "
                               f"Return the processed data as a JSON list with the following keys: "
                               f"Product, ArrivalTime, ProductionDays, ExpiryTime. Do not include any explanations."
                },
            ]
        )

        response_content = response.choices[0].message.content.strip()
        print("LLM Response:", response_content)

        # Detect and execute Python code block
        if response_content.startswith("```python"):
            code_block = response_content.split("```python")[1].split("```")[0].strip()
            print("Executing Code Block:")
            print(code_block)

            # Execute the Python code to extract the JSON output
            exec_locals = {}
            exec(code_block, {}, exec_locals)

            # Retrieve the processed data from the code's execution
            processed_data = json.loads(exec_locals.get("json_data", "[]"))
            return processed_data

        # Attempt to parse directly as JSON if no code block is detected
        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            print("Invalid JSON response:", response_content)
            raise


# Allocation Expert
class AllocationExpert:
    def __init__(self, client):
        self.client = client

    def allocate_tasks(self, df, num_workshops):
        # Convert DataFrame to string format
        jobs_data = df.values.tolist()
        data_string = ", ".join(
            [f"[{row[0]}, {row[1]}, {row[2]}, {row[3]}]" for row in jobs_data]
        )

        # Call LLM
        response = self.client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "user",
                    "content": f"You are a task allocation expert. The data provided is: {data_string}."
                               f"The number of workshops is {num_workshops}."
                               f"Allocate tasks to workshops to minimize the total completion time while ensuring all tasks are completed before their expiry times."
                               f"Return the allocation as a JSON list with the following format: "
                               f"[Product, AssignedWorkshop, StartTime, EndTime]. Do not include any explanations."
                               f"Please show the whole products scheduling,not just partly."
                },
            ]
        )

        response_content = response.choices[0].message.content.strip()
        print("LLM Response:", response_content)

        # Clean backticks from JSON response
        if response_content.startswith("```json"):
            response_content = response_content[len("```json"):].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-len("```")].strip()

        # Parse JSON response
        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            print("Invalid JSON response:", response_content)
            raise


# Prediction Expert
class PredictionExpert:
    def __init__(self, client):
        self.client = client

    def predict_due_dates(self, historical_data):
        # Convert data to string format
        data_string = json.dumps(historical_data)

        # Call LLM
        response = self.client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "user",
                    "content": f"You are a prediction expert. Based on the historical data: {data_string}, "
                               f"Using Machine learning to predict the due dates for future tasks. "
                               f"Return the predictions as a JSON list with the following format: "
                               f"[Product, PredictedDueDate]. Do not include any explanations."
                },
            ]
        )

        response_content = response.choices[0].message.content.strip()
        print("LLM Response:", response_content)

        # Clean backticks from JSON response
        if response_content.startswith("```json"):
            response_content = response_content[len("```json"):].strip()
        if response_content.endswith("```"):
            response_content = response_content[:-len("```")].strip()

        # Parse JSON response
        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            print("Invalid JSON response:", response_content)
            raise


# Main Program
def main():
    # Raw data
    raw_data = [
        {"Product": "P1", "ArrivalTime": "2024-11-19T08:00:00Z", "ProductionDays": 3, "ExpiryTime": None},
        {"Product": "P2", "ArrivalTime": "2024-11-19T09:00:00Z", "ProductionDays": 2, "ExpiryTime": None},
        {"Product": "P3", "ArrivalTime": "2024-11-20T09:00:00Z", "ProductionDays": 2, "ExpiryTime": None},
        {"Product": "P4", "ArrivalTime": "2024-11-21T09:00:00Z", "ProductionDays": 4, "ExpiryTime": None},
        {"Product": "P5", "ArrivalTime": "2024-11-21T09:00:00Z", "ProductionDays": 2, "ExpiryTime": None},
        {"Product": "P6", "ArrivalTime": "2024-11-22T09:00:00Z", "ProductionDays": 3, "ExpiryTime": None},
        {"Product": "P7", "ArrivalTime": "2024-11-22T09:00:00Z", "ProductionDays": 2, "ExpiryTime": None},
        {"Product": "P8", "ArrivalTime": "2024-11-23T09:00:00Z", "ProductionDays": 1, "ExpiryTime": None},
        {"Product": "P9", "ArrivalTime": "2024-11-24T09:00:00Z", "ProductionDays": 5, "ExpiryTime": None},
        {"Product": "P10", "ArrivalTime": "2024-11-25T09:00:00Z", "ProductionDays": 2, "ExpiryTime": None}
    ]

    # Historical data
    historical_data = [
        {"Product": "P1", "ArrivalTime": "2024-11-18T08:00:00Z", "ProductionDays": 4, "ExpiryTime": "2024-11-22T08:00:00Z"},
        {"Product": "P2", "ArrivalTime": "2024-11-18T09:00:00Z", "ProductionDays": 3, "ExpiryTime": "2024-11-21T09:00:00Z"},
    ]

    # Initialize experts
    data_expert = DataProcessingExpert(client)
    allocation_expert = AllocationExpert(client)
    prediction_expert = PredictionExpert(client)

    # Process data
    processed_data = data_expert.process_data(raw_data)
    print("Processed Data:", processed_data)

    # Convert processed data to DataFrame
    processed_df = pd.DataFrame(processed_data)

    # Allocate tasks
    num_workshops = 3
    problem_description = "This is a parallel workshop machine scheduling problem."
    allocation_result = allocation_expert.allocate_tasks(processed_df, num_workshops)
    print("Allocation Result:", allocation_result)

    # Predict due dates
    prediction_result = prediction_expert.predict_due_dates(historical_data)
    print("Prediction Result:", prediction_result)


if __name__ == "__main__":
    main()