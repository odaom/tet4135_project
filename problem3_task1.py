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
modes = ["coal", "gas", "nuclear", "biomass"]
model.modes = pyo.Set(initialize=modes)

# Declare model parameters

costs_fixed = {
    "coal": 200,
    "gas": 500,
    "nuclear": 800,
    "biomass": 1000
    }

costs_variable = {
    "coal": 60,
    "gas": 100,
    "nuclear": 120,
    "biomass": 150
}

max_limits = {
    "coal": 120,
    "gas": 200,
    "nuclear": 50,
    "biomass": 30
}

load_demand = [30, 20, 20, 30, 50, 80, 100, 140, 120, 100, 90, 80, 70, 80, 120, 160, 220, 200, 180, 160, 120, 100, 80, 40]
hours = [i for i, load in enumerate(load_demand)]
# print(hours)
load_demand = {i:load for i, load in enumerate(load_demand)}


model.hours = pyo.Set(initialize=hours)

# print(load_demand)

def costs_fixed_init(model, hour, mode):
    return costs_fixed[mode]

# def costs_variable

def initalize(params):
    return 

model.costs_fixed = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_fixed[mode], domain=pyo.NonNegativeReals)  
print(model.costs_fixed.display())
model.costs_variable = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_variable[mode], domain=pyo.NonNegativeReals)  
model.max_limits = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: max_limits[mode], domain=pyo.NonNegativeReals)
model.load_demand = pyo.Param(model.hours, initialize=load_demand)

# t0 = model.hours.first()
# data = {
#    model.costs_fixed[t0, j].name: [model.costs_fixed[i, j].value for i in model.hours]
#    for j in model.modes
# }
# print(data)


# Declare model variables
model.power_producers = pyo.Var(model.hours, model.modes, within=pyo.NonNegativeReals)

# Declare objective
def objective(model):
    return sum(
        sum(model.costs_fixed[hour, key] + model.costs_variable[hour, key] * model.power_producers[hour, key] for key in model.modes)
        for hour in model.hours)

model.OBJ = pyo.Objective(rule=objective, sense=pyo.minimize) 

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
output = [pyo.value(model.power_producers[key]) for key in model.power_producers]

output_dict =  {
    "coal": output[0::4],
    "gas": output[1::4],
    "nuclear": output[2::4],
    "biomass": output[3::4]
}

df = pd.DataFrame(output_dict)

print(df)
# opt.solve
# load_demand = [30, 20, 20, 30, 50, 80, 100, 140, 120, 100, 90, 80, 70, 80, 120, 160, 220, 200, 180, 160, 120, 100, 80, 40]
# solution = []
# for i, load in enumerate(load_demand):
#     model.load_demand = load
#     opt.solve(model, load_solutions=True)
#     solution.append({
#         "load_demand": load, 
#         "cost": pyo.value(model.OBJ), 
#         "coal": pyo.value(model.power_producers['coal']), 
#         "gas": pyo.value(model.power_producers['gas']),
#         "nuclear": pyo.value(model.power_producers['nuclear']),
#         "biomass": pyo.value(model.power_producers['biomass'])
#         })

# total_cost = 0
# for sol in solution:
#     total_cost += sol["cost"]


# df = pd.DataFrame(solution, columns=modes)

df.plot(kind="bar", stacked=True)
plt.savefig("problem3_task1_second.png")
# print(total_cost)
