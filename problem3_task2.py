"""Proyect Energy planning"""
# -*- coding utf-8 -*-
#Sergio, Eugenia, Oscar and Oda
#15/04/24
#%%
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#%%

# Declare the model
model = pyo.ConcreteModel()

# Declare sets 
load_demand = [30, 20, 20, 30, 50, 80, 100, 140, 120, 100, 90, 80, 70, 80, 120, 160, 220, 200, 180, 160, 120, 100, 80, 40]

modes = ["coal", "gas", "nuclear", "biomass", "battery"]
model.modes = pyo.Set(initialize=modes)

hours = [i for i, load in enumerate(load_demand)]
model.hours = pyo.Set(initialize=hours)

# Declare model parameters
model.load_demand = pyo.Param(model.hours, initialize=load_demand)

costs_fixed = {
    "coal": 200,
    "gas": 500,
    "nuclear": 800,
    "biomass": 1000,
    "battery": 50
    }
model.costs_fixed = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_fixed[mode], domain=pyo.NonNegativeReals)  

costs_variable = {
    "coal": 60,
    "gas": 100,
    "nuclear": 120,
    "biomass": 150,
    "battery": 20
}
model.costs_variable = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: costs_variable[mode], domain=pyo.NonNegativeReals)  

max_limits = {
    "coal": 120,
    "gas": 200,
    "nuclear": 50,
    "biomass": 30,
    "battery": 25
}
model.max_limits = pyo.Param(model.hours, model.modes, initialize=lambda model, hour, mode: max_limits[mode], domain=pyo.NonNegativeReals)

model.battery_rate_max = pyo.Param(initialize=25, doc="Max power flow in or out [MW]")
model.battery_storage_max = pyo.Param(initialize=100, doc='Max storage (MWh)')

# Declare model variables
model.power_producers = pyo.Var(model.hours, model.modes, within=pyo.NonNegativeReals)


### battery variables
model.Ein = pyo.Var(model.hours, bounds=(0, model.battery_rate_max))
model.Eout = pyo.Var(model.hours, bounds=(0, model.battery_rate_max)) 
model.SOC = pyo.Var(model.hours, bounds=(0, model.battery_storage_max))  # State of charge
model.charge_this_hour = pyo.Var(model.hours, within=pyo.Binary)
model.discharge_this_hour = pyo.Var(model.hours, within=pyo.Binary)


# Declare objective
def objective(model):
    return sum(
        sum(model.costs_fixed[hour, key] + model.costs_variable[hour, key] * model.power_producers[hour, key] for key in model.modes)
        for hour in model.hours)

model.objective = pyo.Objective(rule=objective, sense=pyo.minimize) 

# Declare constraints
def production_limits(model, hour, mode):
    return model.power_producers[hour, mode] <= model.max_limits[hour, mode]
model.production_limit_constraint = pyo.Constraint(model.hours, model.modes, rule=production_limits)

def demand(model, hour):
    return sum(model.power_producers[hour, mode] for mode in model.modes) == model.load_demand[hour] + model.Ein[hour]
model.demand_constraint = pyo.Constraint(model.hours, rule=demand)

### battery constraints
def storage_state(model, hour):
    """Storage changes with flows in/out"""
    # Set first hour state of charge to empty
    previous_hour = hour - 1
    if hour == model.hours.first():
        return model.SOC[hour] == 0
    else:
        return (model.SOC[hour] == (model.SOC[previous_hour] 
                            + model.Ein[hour] 
                            - model.Eout[hour]))
model.charge_state = pyo.Constraint(model.hours, rule=storage_state)

# Without a constraint the model would discharge in the final hour
# even when SOC was 0.
def positive_charge(model, hour):
    """Limit discharge to the amount of charge in battery"""
    if hour == model.hours.first():
        return model.Eout[hour] == 0
    else:
        return model.Eout[hour] <= model.SOC[hour-1]
model.positive_charge = pyo.Constraint(model.hours, rule=positive_charge)

def battery_starts_empty(model, hours):
    return model.SOC[0] == 0 
model.battery_starts_empty = pyo.Constraint(model.hours, rule=battery_starts_empty)

model.C1 = pyo.ConstraintList()
model.C2 = pyo.ConstraintList()
model.C3 = pyo.ConstraintList()
model.C4 = pyo.ConstraintList()
for hour in model.hours:
    model.C1.add(model.Eout[hour] == model.power_producers[hour, "battery"])
    model.C2.add(model.charge_this_hour[hour] + model.discharge_this_hour[hour] <= 1)
    model.C3.add(model.Ein[hour] <= model.battery_rate_max * model.charge_this_hour[hour])
    model.C4.add(model.Eout[hour] <= model.battery_rate_max * model.discharge_this_hour[hour])


# Solve the model
opt = pyo.SolverFactory("glpk")
results = opt.solve(model, load_solutions=True)


model.display()
print(results.solver.status)
print(results.solver.termination_condition)

# Generate output 
output = [pyo.value(model.power_producers[key]) for key in model.power_producers]
output_dict =  {
    "coal": output[0::5],
    "gas": output[1::5],
    "nuclear": output[2::5],
    "biomass": output[3::5],
    "battery": output[4::5]
}
state_of_charge = [pyo.value(model.SOC[hour]) for hour in model.hours]
charge_quantity = [pyo.value(model.Ein[hour]) for hour in model.hours]
discharge_quantity = [pyo.value(model.Eout[hour]) for hour in model.hours]
df = pd.DataFrame(output_dict)
df.plot(kind="bar", stacked=True)
plt.plot(state_of_charge, color="purple")
plt.savefig("problem3_task2.png")


# %%
