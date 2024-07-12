import tkinter as tk
from tkinter import messagebox
import pint
import numpy as np

def dynamic_viscosity_air(T):
    return (2.791 * 10**-7 * T**0.7355) *ureg('pascal * second')
    

# Create a unit registry
ureg = pint.UnitRegistry()

rho = 1.293 * ureg('kg/m^3') # density of air
lambd = 6.73 * 10**-8 * ureg('meter') #mean free path
k = 1.38 * 10**-23 *ureg('J/K') # boltzmann constant

# Function to handle the submit button click
def submit():
    try:

        valid_units = {
            'Particle Diameter': ['meter'],
            'Aerosol Temperature': ['kelvin', 'degC', 'degF'],
            'Flowrate': ['meter ** 3 / second'],
            'Tube Length': ['meter'],
            'Tube Diameter': ['meter'],
        }
        # Read and parse input values with units
        inputs = {
        'Particle Diameter': ureg(entry1.get()),
        'Aerosol Temperature': ureg(entry2.get()),
        'Flowrate': ureg(entry3.get()),
        'Tube Length': ureg(entry4.get()),
        'Tube Diameter': ureg(entry5.get())
        }
        for key, quantity in inputs.items():
            try:
                unit = str(quantity.to_base_units().units)
                if unit not in valid_units[key]:
                    raise pint.errors.UndefinedUnitError(f"Invalid unit '{unit}' for {key}")
            except (ValueError, AttributeError, pint.errors.UndefinedUnitError) as e:
                messagebox.showerror("Invalid input",
                                      f"Please enter valid floating point numbers with units. Error: {e}")
                break


        # Convert to SI units
        dp_si = inputs['Particle Diameter'].to_base_units()
        T_si = inputs['Aerosol Temperature'].to_base_units()
        Q_si = inputs['Flowrate'].to_base_units()
        L_si = inputs['Tube Length'].to_base_units()
        D_si = inputs['Tube Diameter'].to_base_units()
        flow_speed = Q_si/(np.pi*(D_si/2)**2)
        Re = (rho*flow_speed*D_si)/dynamic_viscosity_air(T_si.magnitude)
        Re = Re.to_base_units()

        #if flow is lamintar (i.e. Re < 2000), go on with the calculation
        # if not, ask user to make the flow laminar
        
        if Re.magnitude <= 2000:
            #begin calculating the transmission coefficient
            cunningham_correction = 1 + (lambd/dp_si)*(2.514+0.8*np.exp(-0.55*dp_si/lambd))
            diffusion_coefficient = (k * T_si * cunningham_correction) / (3 * np.pi * dynamic_viscosity_air(T_si.magnitude)*dp_si)
            alpha = (np.pi * diffusion_coefficient * L_si) / Q_si

            if alpha >= 0.0312:
                penetration_coefficient = 0.8191*np.exp(-3.657 * alpha) + 0.0975 * np.exp(-22.3 * alpha) + 0.0325 * np.exp(-57 * alpha)
            if alpha < 0.0312:
                penetration_coefficient = 1 - 2.56 * alpha**(2/3) + 1.8 * alpha + 0.177 * alpha**(4/3)
                
            messagebox.showinfo("Calculation", 
                    f"Laminar flow, Re: {round(Re.magnitude,3)}\n"
                    f"Penetration coefficient: {round(penetration_coefficient.magnitude,3)}")
        else:
            messagebox.showerror("Flow not laminar",'Please adjust the values to achieve a laminar flow with Re < 2000')

    except (ValueError, pint.errors.UndefinedUnitError) as e:
        messagebox.showerror("Invalid Input", f"Please enter valid floating point numbers with units. Error: {e}")

# Create the main window
root = tk.Tk()
root.title("Tube penetration coefficient calculator")

# Create labels and entry widgets
tk.Label(root, text="Enter parameters to calculate particle losses in a tube with spherical cross-section.\n The flow inside the tube must be laminar, i.e. Re < 2000").grid(row=0, columnspan=2)

tk.Label(root, text="Particle Diameter (e.g., 5 nm):").grid(row=1, column=0)
entry1 = tk.Entry(root)
entry1.grid(row=1, column=1)

tk.Label(root, text="Aerosol Temperature (e.g., 300 K):").grid(row=2, column=0)
entry2 = tk.Entry(root)
entry2.grid(row=2, column=1)

tk.Label(root, text="Flowrate (e.g., 10 L/min):").grid(row=3, column=0)
entry3 = tk.Entry(root)
entry3.grid(row=3, column=1)

tk.Label(root, text="Tube Length (e.g., 2 m):").grid(row=4, column=0)
entry4 = tk.Entry(root)
entry4.grid(row=4, column=1)

tk.Label(root, text="Tube Diameter (e.g., 7 cm):").grid(row=5, column=0)
entry5 = tk.Entry(root)
entry5.grid(row=5, column=1)

tk.Label(root, text="Number 6 (e.g., 50 mm):").grid(row=6, column=0)
entry6 = tk.Entry(root)
entry6.grid(row=6, column=1)

# Create submit and cancel buttons
tk.Button(root, text="Calculate", command=submit).grid(row=7, column=0)
tk.Button(root, text="Exit", command=root.quit).grid(row=7, column=1)

# Run the main event loop
root.mainloop()
