import numpy as np
import os
import sys
import pickle

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
from functions.fmu_scripts.get_steady_state import *
from functions.functions.heatcurves import heatcurve_presim

def sample_initial_conditions(fmu_filepath, T_outside, use_preexisting_data=True, verbose=False):
    '''Get useful initial conditions for T_outside [°C]'''
    folder_path = os.path.join(project_root, "temp", "initial_conditions")
    sample_temperatures = np.linspace(-10, 40, 11)
    
    if not os.path.exists(folder_path) or use_preexisting_data == False:
        os.makedirs(folder_path, exist_ok=True)
        print('[Info] Generating sample initial conditions...')

        for sample_temperature in sample_temperatures:
            file_path = os.path.join(folder_path, f"{sample_temperature:.1f}.pkl")
            T_VL_Gebaeude = heatcurve_presim.single_value(sample_temperature)
            conditions = {
                'agent_control_setting': True,
                'agent_T_VL': T_VL_Gebaeude,
                'WP_manual_control_setting': True,
                'WP_T_VL': T_VL_Gebaeude,
            }

            # generate initial conditions for sample temperature
            initial_conditions = get_steady_state(fmu_filepath, savefile=None, conditions=conditions, verbose=verbose, plot=verbose, max_simtime=10*3600)

            with open(file_path, 'wb') as file:
                pickle.dump(initial_conditions, file)
        
        print('[Info] Generating sample initial conditions done!')
    

    '''sample initial conditions from generated data'''
    # read in available temperatures
    available_files = [f for f in os.listdir(folder_path) if f.endswith('.pkl')]
    if not available_files: raise FileNotFoundError(f"Keine initial_conditions in '{folder_path}' gefunden!")
    available_temperatures = np.array([float(os.path.splitext(f)[0]) for f in available_files])

    # find closest match
    closest_temp = available_temperatures[np.argmin(np.abs(available_temperatures - T_outside))]
    closest_file = os.path.join(folder_path, f"{closest_temp:.1f}.pkl")

    # load data
    with open(closest_file, 'rb') as file:
        initial_conditions = pickle.load(file)

    print(f"[Info] Using initial conditions for {closest_temp:.1f} degC (Goal: {T_outside:.2f} degC)", flush=True)

    initial_conditions['WP_manual_control_setting'] = False  # heatpump is controlled by heatcurve again
    initial_conditions['agent_control_setting'] = False  # activate agent control

    return initial_conditions


if __name__ =='__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fmu_filepath = os.path.join(project_root, 'fmu', 'simmodell.fmu')
    T_outside = 11
    sample_initial_conditions(fmu_filepath, T_outside, use_preexisting_data=True, verbose=True)