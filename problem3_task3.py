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
model.costs_fixed = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_fixed[mode], domain=pyo.NonNegativeReals)  

costs_variable = {
    "coal": 60,
    "gas": 100,
    "nuclear": 120,
    "biomass": 150
}
model.costs_variable = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_variable[mode], domain=pyo.NonNegativeReals)  

max_limits = {
    "coal": 120,
    "gas": 200,
    "nuclear": 50,
    "biomass": 30
}
model.max_limits = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: max_limits[mode], domain=pyo.NonNegativeReals)


co2_emissions = { # tons of CO2 per MWh energy produced
    "coal": 1.5,
    "gas": 0.2,
    "nuclear": 0,
    "biomass": 0
}
model.co2_emissions = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: co2_emissions[mode], domain=pyo.NonNegativeReals)

cost_co2 = 60  # [EUR/ton CO2]
model.cost_co2 = pyo.Param(model.hours, initialize=cost_co2)

# Declare model variables
model.power_production = pyo.Var(model.hours, model.modes, within=pyo.NonNegativeReals)

# Declare objective
def objective(model):
    return sum(
        sum(model.costs_fixed[hour, mode] 
            + model.costs_variable[hour, mode] * model.power_production[hour, mode] 
            + model.cost_co2[hour] * model.co2_emissions[hour, mode] * model.power_production[hour, mode] for mode in model.modes)
        for hour in model.hours)

model.objective = pyo.Objective(rule=objective, sense=pyo.minimize) 

# Declare constraints
def production_limits(model, hour, mode):
    return  model.power_production[hour, mode] <= model.max_limits[hour, mode]
model.production_limit_constraint = pyo.Constraint(model.hours, model.modes, rule=production_limits)


def demand(model, hour):
    return sum(model.power_production[hour, mode] for mode in model.modes) == model.load_demand[hour]
model.demand_constraint = pyo.Constraint(model.hours, rule=demand)



# Solve the model
opt = pyo.SolverFactory("glpk")
opt.solve(model, load_solutions=True)

# model.display()
# print(pyo.value(model.power_production["coal"]))
print(list(model.power_production))
# Generate output 
output = [pyo.value(model.power_production[hour, mode]) for hour, mode in model.power_production]
print(output)
output_dict =  {
    "coal": output[0::4],
    "gas": output[1::4],
    "nuclear": output[2::4],
    "biomass": output[3::4]
}
df = pd.DataFrame(output_dict)
df.plot(kind="bar", stacked=True)
plt.savefig("problem3_task3.png")
