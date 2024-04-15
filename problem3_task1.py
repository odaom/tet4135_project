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

modes = ["coal", "gas", "nuclear", "biomass"]
model.modes = pyo.Set(initialize=modes)

hours = [i for i, load in enumerate(load_demand)]
model.hours = pyo.Set(initialize=hours)

# Declare model parameters
model.load_demand = pyo.Param(model.hours, initialize=load_demand)

costs_fixed = {
    "coal": 200,
    "gas": 500,
    "nuclear": 800,
    "biomass": 1000
    }
model.costs_fixed = pyo.Param(model.modes, model.hours, initialize=lambda model, mode, hour: costs_fixed[mode], domain=pyo.NonNegativeReals)  

costs_variable = {
    "coal": 60,
    "gas": 100,
    "nuclear": 120,
    "biomass": 150
}
model.costs_variable = pyo.Param(model.modes, model.hours, initialize=lambda model, mode, hour: costs_variable[mode], domain=pyo.NonNegativeReals)  

max_limits = {
    "coal": 120,
    "gas": 200,
    "nuclear": 50,
    "biomass": 30
}
model.max_limits = pyo.Param(model.modes, model.hours, initialize=lambda model, mode, hour: max_limits[mode], domain=pyo.NonNegativeReals)


# Declare model variables
model.power_producers = pyo.Var(model.modes, model.hours, within=pyo.NonNegativeReals)

# Declare objective
def objective(model):
    return sum(
        sum(model.costs_fixed[mode, hour] + model.costs_variable[mode, hour] * model.power_producers[mode, hour] for mode in model.modes)
        for hour in model.hours)

model.objective = pyo.Objective(rule=objective, sense=pyo.minimize) 

# Declare constraints
def production_limits(model, mode, hour):
    return  model.power_producers[mode, hour] <= model.max_limits[mode, hour]
model.production_limit_constraint = pyo.Constraint(model.modes, model.hours, rule=production_limits)


def demand(model, hour):
    return sum(model.power_producers[mode, hour] for mode in model.modes) == model.load_demand[hour]
model.demand_constraint = pyo.Constraint(model.hours, rule=demand)

# Solve the model
opt = pyo.SolverFactory("glpk")
opt.solve(model, load_solutions=True)

# Generate output 
model.display()
output = [pyo.value(model.power_producers[key]) for key in model.power_producers]
print(output)
output_dict =  {
    "coal": output[0:24],
    "gas": output[24:48],
    "nuclear": output[48:72],
    "biomass": output[72:96]
}
df = pd.DataFrame(output_dict)
df.plot(kind="bar", stacked=True)
plt.savefig("problem3_task1.png")
