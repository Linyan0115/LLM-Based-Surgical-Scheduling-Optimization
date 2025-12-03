from docplex.mp.model import Model

# Define the data
num_tasks = 5
num_machines = 2
task_times = [10, 6, 8, 12, 5]  # Task processing times

# Create a model
model = Model("Machine_Scheduling")

# Define binary variables
x = model.binary_var_dict((i, j) for i in range(num_tasks) for j in range(num_machines))

# Define completion times as expressions
T = [model.sum(task_times[i] * x[i, j] for i in range(num_tasks)) for j in range(num_machines)]

# Constraints
for i in range(num_tasks):
    model.addConstraint(model.sum(x[i, j] for j in range(num_machines)) == 1, "task Assignment Constraint {}".format(i))

for j in range(num_machines):
    model.addConstraint(T[j] == model.max(T), "machine Completion Time Constraint {}".format(j))

# Objective
model.minimize(model.max(T))

# Solve the problem
model.solve()

# Print the results
for i in range(num_tasks):
    for j in range(num_machines):
        if model.variables[x[i, j]].solution_value == 1:
            print("Task {} is assigned to Machine {} with completion time {}".format(i + 1, j + 1, T[j].solution_value))
print("Max completion time is: {}".format(model.objective_value))