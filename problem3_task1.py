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

model.costs_fixed = pyo.Param(model.modes, initialize=costs_fixed, domain=pyo.NonNegativeReals)  
model.costs_variable = pyo.Param(model.modes, initialize=costs_variable, domain=pyo.NonNegativeReals)  
model.max_limits = pyo.Param(model.modes, initialize=max_limits, domain=pyo.NonNegativeReals)
model.load_demand = pyo.Param(mutable=True, domain=pyo.NonNegativeReals)

# Declare model variables
model.power_producers = pyo.Var(model.modes, within=pyo.NonNegativeReals)

# Declare objective
def objective(model):
    return sum(model.costs_fixed[key] + model.costs_variable[key] * model.power_producers[key] for key in model.modes)

model.OBJ = pyo.Objective(rule=objective, sense=pyo.minimize) 

# Declare constraints
def production_limits(model, mode):
    return  model.power_producers[mode] <= model.max_limits[mode]

model.production_limit_constraint = pyo.Constraint(model.modes, rule=production_limits)


def demand(model):
    return sum(model.power_producers[mode] for mode in model.modes) == model.load_demand

model.demand_constraint = pyo.Constraint(rule=demand)


# Solve the model
opt = pyo.SolverFactory("glpk")
load_demand = [30, 20, 20, 30, 50, 80, 100, 140, 120, 100, 90, 80, 70, 80, 120, 160, 220, 200, 180, 160, 120, 100, 80, 40]
solution = []
for i, load in enumerate(load_demand):
    model.load_demand = load
    opt.solve(model, load_solutions=True)
    solution.append({
        "load_demand": load, 
        "cost": pyo.value(model.OBJ), 
        "coal": pyo.value(model.power_producers['coal']), 
        "gas": pyo.value(model.power_producers['gas']),
        "nuclear": pyo.value(model.power_producers['nuclear']),
        "biomass": pyo.value(model.power_producers['biomass'])
        })


df = pd.DataFrame(solution, columns=modes)

df.plot(kind="bar", stacked=True)
plt.savefig("problem3_task1.png")
