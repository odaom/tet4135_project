"""Proyect Energy planning"""
# -*- coding utf-8 -*-
#Sergio, Eugenia, Oscar and Oda
#15/04/24
#%%
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
import matplotlib.pyplot as plt
import math
#%%

# Declare the model
model = pyo.ConcreteModel()

# Declare sets 
load_demand = [30, 20, 20, 30, 50, 80, 100, 140, 120, 100, 90, 80, 70, 80, 120, 160, 220, 200, 180, 160, 120, 100, 80, 40]

modes = ["coal", "gas", "wind", "solar", "wind2"]
model.modes = pyo.Set(initialize=modes)

hours = [i for i, load in enumerate(load_demand)]
model.hours = pyo.Set(initialize=hours)

# Declare model parameters
model.load_demand = pyo.Param(model.hours, initialize=load_demand)

costs_fixed = {
    "coal": 200,
    "gas": 500,
    "wind": 800,
    "solar": 1000,
    "wind2": 800
    }
model.costs_fixed = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_fixed[mode], domain=pyo.NonNegativeReals)  

costs_variable = {
    "coal": 65,
    "gas": 120,
    "wind": 40,
    "solar": 35,
    "wind2": 40
}
model.costs_variable = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_variable[mode], domain=pyo.NonNegativeReals)  


co2_emissions = { # [tons/MWh]
    "coal": 2,
    "gas": 0.5,
    "wind": 0,
    "solar": 0,
    "wind2": 0
}
model.co2_emissions = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: co2_emissions[mode], domain=pyo.NonNegativeReals)

cost_co2 = 80  # [EUR/ton CO2]
model.cost_co2 = pyo.Param(model.hours, initialize=cost_co2)


max_limits = {
    "coal": [120] * len(hours),
    "gas": [200] * len(hours),
    "wind": [32, 51, 19, 25, 19, 4, 2, 1, 0, 0, 0, 0, 2, 4, 9, 1, 41, 32, 14, 14, 19, 32, 32, 41],
    "solar": [0, 0, 0, 0, 2, 5, 8, 10, 12, 15, 18, 22, 25, 28, 30, 30, 30, 25, 20, 15, 10, 5, 0, 0],
    "wind2": [0, 1, 0, 4, 7, 13, 21, 25, 31, 32, 41, 40, 31, 20 ,14 , 21, 26, 29, 42, 43, 45, 41, 40, 29]
}
model.max_limits = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: max_limits[mode][hour], domain=pyo.NonNegativeReals)


max_unit_counts = {
    "coal": 1,
    "gas": 1,
    "wind": 100,
    "solar": 1,
    "wind2": 100
}
model.max_unit_counts = pyo.Param(model.modes, initialize=max_unit_counts, domain=pyo.PositiveIntegers)
 
# Declare model variables
model.power_production = pyo.Var(model.hours, model.modes, within=pyo.NonNegativeReals)

model.production_unit_count = pyo.Var(model.modes, within=pyo.PositiveIntegers)


# Declare objective
def objective(model):
    return sum(
        sum(model.costs_fixed[hour, mode] 
            + model.costs_variable[hour, mode] * model.power_production[hour, mode] 
            + model.cost_co2[hour] * model.co2_emissions[hour, mode] * model.power_production[hour, mode] for hour in model.hours) 
        * model.production_unit_count[mode] for mode in model.modes)



model.objective = pyo.Objective(rule=objective, sense=pyo.minimize) 

# Declare constraints
def production_limits(model, hour, mode):
    return  model.power_production[hour, mode] <= model.max_limits[hour, mode]
model.production_limit_constraint = pyo.Constraint(model.hours, model.modes, rule=production_limits)


def demand(model, hour):
    return sum(model.power_production[hour, mode] * model.production_unit_count[mode] for mode in model.modes) == model.load_demand[hour]
model.demand_constraint = pyo.Constraint(model.hours, rule=demand)

def unit_count(model, mode):
    return model.production_unit_count[mode] <= model.max_unit_counts[mode]
model.unit_count_constraint = pyo.Constraint(model.modes, rule=unit_count)  


# Solve the model
opt = pyo.SolverFactory("gurobi", solver_io="python")
opt.solve(model, load_solutions=True)

model.pprint()

model.display()


# Generate output 
output = [pyo.value(model.power_production[key]) * pyo.value(model.production_unit_count[key[1]]) for key in model.power_production]
output_dict =  {
    "coal": output[0::5],
    "gas": output[1::5],
    "wind": output[2::5],
    "solar": output[3::5],
    "wind2": output[4::5]
}
df = pd.DataFrame(output_dict)

df.columns = pd.CategoricalIndex(df.columns.values, ordered=True, categories=["coal", "solar", "wind2", "wind", "gas"])
df = df.sort_index(axis=1)
bar = df.plot.bar(stacked=True, color=["C0", "C6", "C9", "C8", "C1"])

plt.title("Optimal production profile (with optimal sizing of wind power plants)")
plt.xlabel("Time [h]")
plt.ylabel("Generation [MW]")
plt.legend()

plt.savefig("problem3_task9.png")
