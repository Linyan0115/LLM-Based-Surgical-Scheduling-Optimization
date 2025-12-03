import simpy
import pandas as pd

# Load data from Excel
data = pd.read_excel('data.xlsx')

def job(env, name, machine, processing_time):
    # ""Process job."""
    print(f'{name} starts processing at {env.now}')
    yield env.timeout(processing_time)
    print(f"{name} completed at {env.now}")

def setup(env, num_machines, job_data):
    # ""Initialize the simulation and create jobs according to the Excel data."""
    machine = simpy.Resource(env, capacity=num_machines)

    for index, row in job_data.iterrows():
        # Delay the job creation based on the arrival time from Excel
        yield env.timeout(row['Arrival Time'])
        env.process(job(env, row['Job ID'], machine, row['Processing Time']))

# Simulation parameters
num_machines = 2  # Number of parallel machines

# Create the SimPy environment
env = simpy.Environment()
# Start the setup process
env.process(setup(env, num_machines, data))
# Run the simulation
env.run()
