"""Proyect Energy planning"""
# -*- coding utf-8 -*-
#Sergio, Eugenia, Oscar and Oda
#15/04/24
#%%
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
import matplotlib.pyplot as plt
#%%

# Declare the model
model = pyo.ConcreteModel()

# Declare sets 
load_demand = [30, 20, 20, 30, 50, 80, 100, 140, 120, 100, 90, 80, 70, 80, 120, 160, 220, 200, 180, 160, 120, 100, 80, 40]

modes = ["coal", "gas", "wind", "solar"]
model.modes = pyo.Set(initialize=modes)

hours = [i for i, load in enumerate(load_demand)]
model.hours = pyo.Set(initialize=hours)

# Declare model parameters
model.load_demand = pyo.Param(model.hours, initialize=load_demand)

costs_fixed = {
    "coal": 200,
    "gas": 500,
    "wind": 800,
    "solar": 1000
    }
model.costs_fixed = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_fixed[mode], domain=pyo.NonNegativeReals)  

costs_variable = {
    "coal": 65,
    "gas": 120,
    "wind": 40,
    "solar": 35
}
model.costs_variable = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_variable[mode], domain=pyo.NonNegativeReals)  

max_limits = {
    "coal": [120] * len(hours),
    "gas": [200] * len(hours),
            #  0   1   2   3   4  5  6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22  23
    "wind":  [32, 51, 19, 25, 19, 4, 2,  1,  0,  0,  0,  0,  2,  4,  9,  1, 41, 32, 14, 14, 19, 32, 32, 41],
    "solar": [ 0,  0,  0,  0,  2, 5, 8, 10, 12, 15, 18, 22, 25, 28, 30, 30, 30, 25, 20, 15, 10, 5, 0, 0]  
}
model.max_limits = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: max_limits[mode][hour], domain=pyo.NonNegativeReals)


# Declare model variables
model.power_producers = pyo.Var(model.hours, model.modes, within=pyo.NonNegativeReals)

# Declare objective
def objective(model):
    return sum(
        sum(model.costs_fixed[hour, key] + model.costs_variable[hour, key] * model.power_producers[hour, key] for key in model.modes)
        for hour in model.hours)

model.objective = pyo.Objective(rule=objective, sense=pyo.minimize) 

# Declare constraints
def production_limits(model, hour, mode):
    return  model.power_producers[hour, mode] <= model.max_limits[hour, mode]
model.production_limit_constraint = pyo.Constraint(model.hours, model.modes, rule=production_limits)


def demand(model, hour):
    return sum(model.power_producers[hour, mode] for mode in model.modes) == model.load_demand[hour]
model.demand_constraint = pyo.Constraint(model.hours, rule=demand)

# Solve the model
opt = pyo.SolverFactory("glpk")
opt.solve(model, load_solutions=True)

model.display()

# Generate output 
output = [pyo.value(model.power_producers[key]) for key in model.power_producers]
output_dict =  {
    "coal": output[0::4],
    "gas": output[1::4],
    "wind": output[2::4],
    "solar": output[3::4]
}
df = pd.DataFrame(output_dict)

df.columns = pd.CategoricalIndex(df.columns.values, ordered=True, categories=["coal", "solar", "wind", "gas"])
df = df.sort_index(axis=1)
bar = df.plot.bar(stacked=True, color=["C0", "C6", "C8", "C1"])

plt.title("Optimal production profile (with variable wind and solar power)")
plt.xlabel("Time [h]")
plt.ylabel("Generation [MW]")
plt.legend()

plt.savefig("problem3_task6.png")
