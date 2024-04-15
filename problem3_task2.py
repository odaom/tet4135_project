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

# Declare the model
model = pyo.ConcreteModel()

# Declare sets 
modes = ["coal", "gas", "nuclear", "biomass", "battery"]
model.modes = pyo.Set(initialize=modes)

# Declare model parameters

costs_fixed = {
    "coal": 200,
    "gas": 500,
    "nuclear": 800,
    "biomass": 1000,
    "battery": 50
    }

costs_variable = {
    "coal": 60,
    "gas": 100,
    "nuclear": 120,
    "biomass": 150,
    "battery": 20
}

max_limits = {
    "coal": 120,
    "gas": 200,
    "nuclear": 50,
    "biomass": 30,
    "battery": math.inf # set to a large value, we'll define a separate contstraint specifically for battery
}

model.costs_fixed = pyo.Param(model.modes, initialize=costs_fixed, domain=pyo.NonNegativeReals)  
model.costs_variable = pyo.Param(model.modes, initialize=costs_variable, domain=pyo.NonNegativeReals)  
model.max_limits = pyo.Param(model.modes, initialize=max_limits, domain=pyo.NonNegativeReals)
model.load_demand = pyo.Param(mutable=True, domain=pyo.NonNegativeReals)

model.battery_charge = pyo.Param(mutable=True, domain=pyo.NonNegativeReals, initialize=0)
model.can_discharge = pyo.Param(initialize=0, mutable=True) 
model.can_charge = pyo.Param(initialize=1, mutable=True) 

# Declare model variables
model.power_producers = pyo.Var(model.modes, within=pyo.NonNegativeReals)

# Declare objective
def objective(model):
    # return sum((model.costs_fixed[key] + model.costs_variable[key] * model.power_producers[key]) * model.can_discharge[key] for key in model.modes)
    return sum(model.costs_fixed[key] + model.costs_variable[key] * model.power_producers[key] for key in model.modes)

model.OBJ = pyo.Objective(rule=objective, sense=pyo.minimize) 

# def objective_battery_charge_level(model):
#     return sum((model.costs_fixed[key] + model.costs_variable[key] * model.power_producers[key]) * model.can_discharge[key] for key in model.modes)



# def charging_objective(model):
#     min()
#     model.battery_charge + 
# model.objective

# Declare constraints
def production_limits(model, mode):
    return model.power_producers[mode] <= model.max_limits[mode]
model.production_limit_constraint = pyo.Constraint(model.modes, rule=production_limits)


def demand(model):
    max_charge_per_hour = 25
    total_demand = model.load_demand + max_charge_per_hour * model.can_charge
    return sum(model.power_producers[mode] for mode in model.modes) == total_demand
model.demand_constraint = pyo.Constraint(rule=demand)



def battery_limit(model):
    # available_battery_capacity = 100 - model.battery_charge
    # max_charge = max(25, available_battery_capacity)
    max_charge = 25
    return model.power_producers["battery"] <= max_charge * model.can_discharge
model.battery_limit = pyo.Constraint(rule=battery_limit)



# def battery_charge_limit(model):
#     return model.battery_charge <= 100
# model.battery_charge_limit = pyo.Constraint(rule=battery_charge_limit)

# def battery_charging(model):


def charging(battery_charge, load, hour):
    # return (can discharge, can charge)
    hours_left = 23 - hour
    # print(hours_left)
    if battery_charge < 100 and load < 120 - 25:
        can_discharge = 0
        can_charge = 1
    elif battery_charge > 0 and load > 120:
        can_discharge = 1
        can_charge = 0
    else: 
        can_discharge = 0
        can_charge = 0
    return can_discharge, can_charge


# Solve the model
opt = pyo.SolverFactory("glpk")
load_demand = [30, 20, 20, 30, 50, 80, 100, 140, 120, 100, 90, 80, 70, 80, 120, 160, 220, 200, 180, 160, 120, 100, 80, 40]
# load_demand = [30, 20, 40,  70, 70, 20, 10,  100, 200]
solution = []
battery_charge = 0
for hour, load in enumerate(load_demand):
    # if 
    # model.can_discharge["battery"] = 1 if model.battery_charge > 
    model.can_discharge, model.can_charge = charging(battery_charge, load, hour)
    if pyo.value(model.can_charge):
        battery_charge += 25


    model.load_demand = load
    opt.solve(model, load_solutions=True)

    if pyo.value(model.power_producers["battery"]) > 0:
        battery_charge -= pyo.value(model.power_producers["battery"])
    # battery_charge = pyo.value(model.battery_charge)


    solution.append({
        "load_demand": load, 
        "cost": pyo.value(model.OBJ), 
        "battery_charge": battery_charge,
        "coal": pyo.value(model.power_producers['coal']), 
        "gas": pyo.value(model.power_producers['gas']),
        "nuclear": pyo.value(model.power_producers['nuclear']),
        "biomass": pyo.value(model.power_producers['biomass']),
        "battery": pyo.value(model.power_producers['battery'])
        })
# model.display()

total_cost = 0
for sol in solution:
    print(sol)
    total_cost += sol["cost"]

print(total_cost)
df = pd.DataFrame(solution, columns=modes)



df.plot(kind="bar", stacked=True, title=f"total cost = {total_cost}")
plt.plot(range(24), [120] * 24)
plt.savefig("problem3_task2.png")
