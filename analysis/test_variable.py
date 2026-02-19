from functions.fmu_scripts.get_steady_state import get_steady_state
import matplotlib.pyplot as plt

'''Script to test the impact of a single input variable on a single output variable.
currently working, but the used Variable Qp_HK_nom can't be varied in that way'''

fmu_filepath = './fmu/simmodell.fmu'
output_var = 'B_EG.T_room'
output_unit = '°C'
# conditions = {'agent_T_VL':40, 'agent_control_setting':True}
# conditions = {'Building_T_VL.y':50, 'agent_control_setting':False}
input_var = 'Qp_HK_nom'
input_vals = [100, 1000]

# generate results for every defined condition
output_values_list = []
conditions_list = [{input_var: val} for val in input_vals]
for conditions in conditions_list:
    steady_state_values, output_values, time_values = get_steady_state(fmu_filepath, output_var, conditions=conditions, use_preexisting_data=False, plot_dymola_values=False, debug=False, plot=False, full_output=True)
    output_values_list.append(output_values)

# plot results
for i in range(len(output_values_list)):
    label = ", ".join(f"{k}={v}" for k, v in conditions_list[i].items())
    plt.plot(time_values, output_values_list[i], label=label)

plt.xlabel('Zeit [h]')
plt.ylabel(output_var + " [" + output_unit +"]")
plt.title(f"Variation von {input_var}")
plt.legend()
plt.grid()
plt.show()
