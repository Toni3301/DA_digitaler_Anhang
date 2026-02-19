import numpy as np
import matplotlib.pyplot as plt
from collections import deque

def moving_average_decorator(num_values=3*60):
    """Decorator to use the moving average of the last inputs as input to the function."""
    def decorator(func):
        recent_inputs = deque(maxlen=num_values)  # Store the last `num_values` inputs
        
        def wrapper(T_outside):
            if isinstance(T_outside, (list, np.ndarray)):
                T_outside = T_outside[0]
            
            recent_inputs.append(T_outside)  # Add the new input to the deque

            if len(recent_inputs) == 0:
                avg_input = T_outside
            else:
                avg_input = sum(recent_inputs) / len(recent_inputs)  # Compute the moving average
            
            return func(avg_input)  # Call the original function with the averaged input
        
        wrapper.single_value = func

        return wrapper
    return decorator


@moving_average_decorator()
def heatcurve_hp(T_outside):
    '''heatcurve of the heatpump in the HIL lab'''
    if T_outside < 15:
        T_VL = -0.59 * T_outside + 31.79
    elif T_outside >= 15:
        T_VL = -0.60 * T_outside + 32
    else:
        T_VL = None

    if T_VL == None:
        return T_VL
    elif T_VL >= 20: 
        return T_VL 
    else: 
        return 20
        

@moving_average_decorator()
def heatcurve_boi(T_outside):
    '''heatcurve of the boiler in the HIL lab'''
    if T_outside < -14: 
        T_outside = -14
    if T_outside < 15:
        T_VL = -1.41 * T_outside + 56.26
    elif T_outside >= 15:
        T_VL = -3.00 * T_outside + 80.00
    else:
        T_VL = None
    
    if T_VL == None:
        return T_VL
    elif T_VL >= 20: 
        return T_VL 
    else: 
        return 20


@moving_average_decorator()
def heatcurve_presim(T_outside):
    offset = - 10
    if T_outside < -14: 
        T_outside = -14
    if T_outside < 15:
        T_VL = -1.41 * T_outside + 56.26 + offset
    elif T_outside >= 15:
        T_VL = -3.00 * T_outside + 80.00 + offset
    else:
        T_VL = None
    
    if T_VL == None:
        return T_VL
    elif T_VL >= 20: 
        return T_VL 
    else: 
        return 20


if __name__ == '__main__':
    testtemp = np.linspace(-20, 20, 41).tolist()
    heatcurve_hp_vals = []
    heatcurve_boi_vals = []
    heatcurve_presim_vals = []

    for temp in testtemp:
        heatcurve_hp_vals.append(heatcurve_hp.single_value(temp))
        heatcurve_boi_vals.append(heatcurve_boi.single_value(temp))
        heatcurve_presim_vals.append(heatcurve_presim.single_value(temp))

    plt.plot(testtemp, heatcurve_hp_vals, label='Wärmepumpe', color='green')
    plt.plot(testtemp, heatcurve_boi_vals, label='Heizkessel', color='red')
    #plt.plot(testtemp, heatcurve_presim_vals, label='Präsimulation', color='green', linestyle='--')
    plt.legend()
    plt.xlabel('Außentemperatur [°C]')
    plt.ylabel('Vorlauftemperatur [°C]')
    plt.title('Hinterlegte Heizkurven im Versuchsstand')
    #plt.title('Heizkurve für die Präsimulation')
    plt.grid()
    plt.show()
