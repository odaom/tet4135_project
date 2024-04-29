import pyomo.environ as pyo
import pandas as pd
import matplotlib.pyplot as plt

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
model.cost_co2 = pyo.Param(model.hours, initialize=cost_co2, mutable=True)

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
    return model.power_production[hour, mode] <= model.max_limits[hour, mode]

model.production_limit_constraint = pyo.Constraint(model.hours, model.modes, rule=production_limits)

def demand(model, hour):
    return sum(model.power_production[hour, mode] for mode in model.modes) == model.load_demand[hour]

model.demand_constraint = pyo.Constraint(model.hours, rule=demand)

# Solve the model
opt = pyo.SolverFactory("glpk")
opt.solve(model, load_solutions=True)

# Generate output 
output = {hour: {mode: pyo.value(model.power_production[hour, mode]) for mode in model.modes} for hour in model.hours}
df = pd.DataFrame(output)

# Plot the power production profile
df.plot(kind="bar", stacked=True)
plt.title("Optimal Power Production Profile")
plt.xlabel("Time [h]")
plt.ylabel("Generation [MW]")
plt.xticks(rotation=0)
plt.savefig("problem3_task3.png")

# Plot the hourly CO2 emissions
hourly_co2_emissions = [sum(model.co2_emissions[hour, mode] * pyo.value(model.power_production[hour, mode]) for mode in model.modes) for hour in model.hours]

plt.figure()
plt.plot(model.hours, hourly_co2_emissions, marker='o')
plt.title("Hourly CO2 Emissions")
plt.xlabel("Hour")
plt.ylabel("CO2 Emissions [tons]")
plt.grid(True)
plt.xticks(model.hours)
plt.savefig("hourly_co2_emissions.png")

# Calculate total CO2 emissions
total_co2_emissions = sum(hourly_co2_emissions)
print("Total CO2 emissions:", total_co2_emissions, "tons")
# Sensitivity analysis
co2_costs_range = range(10, 131, 20)
total_costs = []

for co2_cost in co2_costs_range:
    for hour in model.hours:
        model.cost_co2[hour] = co2_cost
        
        # Solve the model
    print([pyo.value(model.cost_co2[hour]) for hour in model.hours])
    opt.solve(model, load_solutions=True)
    
    # Calculate the total operation cost (objective function value)
    total_cost = pyo.value(model.objective)
    total_costs.append(total_cost)
    
    
   
# Plot the sensitivity analysis results for CO2 emissions cost variation
plt.figure()
plt.plot(co2_costs_range, total_costs, marker='o')
plt.title("Sensitivity Analysis of Total Operation Cost for CO2 Emissions Cost Variation")
plt.xlabel("Cost of CO2 Emissions [EUR/ton CO2]")
plt.ylabel("Total Operation Cost [EUR]")
plt.grid(True)
plt.savefig("co2_cost_sensitivity_analysis.png")

# Display the sensitivity analysis results
for co2_cost, total_cost in zip(co2_costs_range, total_costs):
    print(f"Cost of CO2 Emissions: {co2_cost} EUR/ton CO2, Total Operation Cost: {total_cost} EUR")
