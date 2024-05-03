"""Proyect Energy planning 2"""
# -*- coding utf-8 -*-
#15/04/24
#%%
import math
import matplotlib.pyplot as plt
import numpy as np
"""""""""""""""""""""""""""""
         TASK 1

"""""""""""""""""""""""""""""
"""ASSIGMENT 9"""
"New fast charging stations properties"
#Charging station consumption
P_ch_car=0.055 #MW
#Number of charging stations
N_ch_points=52

"Demand before fast charging stations"
#Peak consumption WITHOUT taking into account cars charging consumption
Power_peak=3.5 #MW
#Valley consumption WITHOUT taking into account cars charging consumption
Power_valley=1.25 #MW
#Energy price for peak consumption
Price_peak= 325 #NOK/MWh
#Energy price for valley consumption
Price_valley= 210 #NOK/MWh
#Number of peak hours
h_peak= 6 #h
#Number of valley hours
h_valley= 18 #h

"Line properties"
#Cross section of the cable
A_25= 25 #mm^2
#Length of the line
L= 8 #km
#Resistivity of the line
Resistivity= 18 #ohm*mm^2/km
#Maximum current of the line
I_max_25= 255 #A
#Voltage of the power line
U= 0.01000 #MV
#Resistance of the line
R_25=L*Resistivity/A_25 #ohm
#Power of the line
Power_line_max= math.sqrt(3)*U*I_max_25 #MW

"""
Problem 1
"""
# Show that the maximum power demand (after installing the fast charging stations) is higher than the maximum power transport capacity for the line.

Power_cars= P_ch_car * N_ch_points #MW
Power_load_peak= Power_cars + Power_peak #MW
Power_excess= Power_load_peak-Power_line_max #MW

"""
Problem 2
"""
#Use marginal analysis to decide which of the two overhead lines you would select. 
"Properties of both lines"
#Lifetime
n=20 #Years
#Discount rate
r=0.085

"Line FeAl75"
#Cross section of the cable
A_75= 60 #mm^2
#Maximum current
I_max_75=424 #A
#Investment cost
F_75= 750000 #NOK/km

"Line FeAl90"
#Cross section of the cable
A_90= 90 #mm^2
#Maximum current
I_max_90=485 #A
#Investment cost
F_90= 900000 #NOK/km

#Annuity calculation
E= r/(1-(1+r)**(-n))

"Calculation of the annual total cost for FeAl75"
#Annual investment cost
f_75= F_75*L*E #NOK

#Line losses
R_75=L*Resistivity/A_75  #omhs  

#Losses during peak and off-peak hours
P_loss_peak_75= (R_75*(10**-6)*Power_load_peak**2)/U**2  #MW ( 10^-6 to convert omhs to mega omhs)
P_loss_valley_75= R_75*(10**-6)*Power_valley**2/U**2     #MW  

#Annual cost of losses
o_75=365*(Price_peak*P_loss_peak_75*h_peak+Price_valley*P_loss_valley_75*h_valley) #noks

#Annual total cost
c_75=f_75+o_75  #NOKS


"Calculation of the annual total cost for FeAl75"
#Annual investment cost
f_90= F_90*L*E #NOK

#Line losses
R_90=L*Resistivity/A_90

#Losses during peak and off-peak hours
P_loss_peak_90= R_90*(10**-6)*Power_load_peak**2/U**2
P_loss_valley_90= R_90*(10**-6)*Power_valley**2/U**2 

#Annual total cost of losses
o_90=365 * (Price_peak * P_loss_peak_90 * h_peak + Price_valley * P_loss_valley_90 * h_valley)

#Annual total cost
c_90 = f_90 + o_90

"""
Problem 3
"""
#a)Use the data given for the 60 mm^2 and 90 mm^2 lines to express the investment cost as a linear function of the cross-section.

#The linear function of the investment cost will be defined as F=a + bx [NOK/km]
#Using linearization
b=(F_90-F_75)/(A_90-A_75)

a=F_90-b*A_90

#b) Find the cross-section that minimizes the total cost of the system.
#To minimaze the total cost we will need to find the derivate of the total cost in function of the cross section
#Imported packages

"Way to solve it using optimization problems if the fuction didnt had nonlinear terms (maybe this can be useful in the future) "
#def Objective_function(model):
    
#    return((a+b*model.c_s)*L*E) + 365(h_valley*L/(model.c_s*math.pow(10,2))*math.pow(Power_load_peak,2)*Price_peak*h_valley+h_peak*L/(model.c_s*math.pow(10,2))*math.pow(Power_valley,2)*Price_valley*h_peak)
#model.OBJ = pyo.Objective(rule = Objective_function, sense = pyo.minimize)

"Way to solve th4e problem derivating by hand"

#dc/dx=0
#df/dx+do/dx=0
#L*E*b-K*x^-2=0
K=(L*Resistivity/(U*10**3)**2)*365*(Price_peak * Power_load_peak**2 * h_peak + Price_valley * Power_valley**2 * h_valley)

opt_cross_sect=math.sqrt(K/(L*E*b))

"""
a) Calculate the total battery capacity (MWh) needed from the fleet of vehicles to ensure that the power imported from the grid is constant over the day. You can assume that the battery will be fully charged in the low-demand period and fully discharged in the high-demand period.
"""
#Battery efficiency

efficiency_ch=0.94
efficiency_disch=.92


#Power imported from the grid is constant over the day. So energy discharged during peak
#periods should be equal to the energy charged during off-peak periods:
#                   Ech=Edisch
#    P_ch*efficiency_ch*h_valley=(P_disch*h_peak)/efficiency_disch

    
# Also, the power demanded in both periods is equal:  P_peak- Pdisch = P_valley + Pch


#Using both equations we obtain:
P_disch=(Power_load_peak-Power_valley)/(h_peak/(efficiency_ch*h_valley*efficiency_disch)+1)
P_ch=Power_load_peak-P_disch-Power_valley
#The total battery capacity will be given by:
E_bat=h_valley*P_ch*efficiency_ch



print()
print("TASK 1")
print()
print("a)")
print("Total battery capacity needed:", E_bat, "MWh")





"""
b) Consider the FeAl90 line as a reference case for dealing with the grid capacity problem. What maximum initial payment can be made to the taxi company to ensure a positive annual net benefit?

"""
#To get a positive net benefit, the annual operating cost + the annual fixed cost must be less
#than the total annual cost of the FeAl90.


"FeAl90 case"
#Cost of electricity delivery
o_90_load=365*(Price_peak*Power_load_peak*h_peak+Price_valley*Power_valley*h_valley) #noks
o_90_total=o_90+o_90_load

#Total cost
c_90_total = f_90+ o_90_total 


"Taxi battery case"
#Calculation of the load power when the load is constant over the day
Power_load_cte=Power_load_peak-P_disch 

#operational cost of the load
o_load_bat=365*Power_load_cte*(Price_peak*h_peak+Price_valley*h_valley)

#Losses of the FeAl25 line
R_25=L*Resistivity/A_25
P_loss_bat=R_25*(10**-6)*Power_load_cte**2/U**2

#Price of the battery losses
o_loss_bat= 365*P_loss_bat*(Price_peak*h_peak+Price_valley*h_valley)

#Total battery operational costs

o_total_bat= o_loss_bat + o_load_bat
#To obtain a positive annual net benefit then Fmaxbat<cAl90 being:

#Annuity calculations
E_5=r/(1-(1+r)**-5) #annuity for year 5
E_10=r/(1-(1+r)**-10) #annuity for year 10
E_15=r/(1-(1+r)**-15) #annuity for year 15

#To find the maximum cost the battery can have to be profitable:

#f_max_bat+1.25 f_max_bat/E8.5,5 + 1.5 f_max_bat/E8.5,10 + 1.75 f_max_bat/E8.5,15 = (c_90_total)/E8.5,20

f_max_bat =  ((c_90_total)/E)/(1+ 1.25/E_5 +1.5/E_10 + 1.75/E_15)

F_max_bat=f_max_bat+ 1.25 * (f_max_bat/E_5 ) + 1.5 * (f_max_bat/E_10 ) + 1.75 * (f_max_bat/E_15 )



print()
print("b)")
print("Maximum initial payment to ensure a positive annual net benefit:", f_max_bat, "NOK")



"""""""""""""""""""""""""""""
         TASK 3

"""""""""""""""""""""""""""""

"a.The value of x for the additional component"


# Define the function

def f_max_bat_x(x, C_90_total, E_5, E_10, E_15):
    return ((c_90_total)/E)/(1 + (1 + x)/ E_5 + (1 + 2*x)/ E_10 + (1 + 3*x)/ E_15)

# Define the range of x values
x_values = np.linspace(0, 1, 21)  # Adjust the range and number of points as needed


f_values = f_max_bat_x(x_values, f_max_bat, E_5, E_10, E_15)

# Plot the function
plt.plot(x_values, f_values)
plt.xlabel('x (Multiplier for Additional Component)')
plt.ylabel('Maximum initial payment in NOKS')
plt.title('Additional component sensitivity')
plt.grid(True)
plt.show()

"b.Discount rate."
#r is dr here, because if not it mess up the code
#Define the function
def f_max_bat_r(dr, f_max_bat):
    return ((c_90_total)/(dr/(1-(1+dr)**-20)))/(1 + 1.25/ (dr/(1-(1+dr)**-5)) + 1.5/ (dr/(1-(1+dr)**-10)) + 1.75/(dr/(1-(1+dr)**-15)))
#f_max_bat+ 1.25 * (f_max_bat/(dr/(1-(1+dr)**-5)) ) + 1.5 * (f_max_bat/(dr/(1-(1+dr)**-10))) + 1.75 * (f_max_bat/(dr/(1-(1+dr)**-15)) )

# Define the range of r values
r_values = np.linspace(0, 0.2, 11)  # Adjust the range and number of points as needed

# Calculate the function values for the given r range
f_values2 = f_max_bat_r(r_values, f_max_bat)

# Plot the function
plt.plot(r_values, f_values2)
plt.xlabel('r (Discount rate)')
plt.ylabel('Maximum initial payment in NOKS')
plt.title('Discount rate sensitivity')
plt.grid(True)
plt.show()



"d.Cost of electricity during the peak hours / high demand hours." 


# Define the function

def f_max_bat_p(p,  E_5, E_10, E_15):
    
    
    o_90_p=365 * (p * P_loss_peak_90 * h_peak + Price_valley * P_loss_valley_90 * h_valley)
    o_90_load_p=365*(p*Power_load_peak*h_peak+Price_valley*Power_valley*h_valley) #noks
    o_90_total_p=o_90_p+o_90_load_p
    o_load_bat_p=365*Power_load_cte*(p*h_peak+Price_valley*h_valley) 
    o_loss_bat_p= 365*P_loss_bat*(p*h_peak+Price_valley*h_valley)
    o_total_bat_p=o_load_bat_p+o_loss_bat_p
    c_90_total_p= f_90 + o_90_total_p
    return ((c_90_total_p)/E)/(1+ 1.25/E_5 +1.5/E_10 + 1.75/E_15)

# Define the range of x values
p_values = np.linspace(0, 1000, 20)  


f_values_p = f_max_bat_p(p_values, E_5, E_10, E_15)

# Plot the function
plt.plot(p_values, f_values_p)
plt.xlabel('Peak price in  NOK/MWh')
plt.ylabel('Maximum initial payment in NOKS')
plt.title('Peak price sensitivity')
plt.grid(True)
plt.show()








# %%








# %%
