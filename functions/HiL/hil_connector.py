## SETUP
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fmpy.fmi2 import FMU2Slave
from fmpy import read_model_description, extract
from functions.fmu_scripts.get_steady_state import get_steady_state


def gen_T_RL_Building(fmu_filepath, step_size=60, initial_VL_value=50, savefile='HIL_results.csv'):
    '''setup the simulation'''
    conditions = {
        'HIL_T_VL': initial_VL_value,
        'HIL_mode_setting': True
        }
    steady_state_values = get_steady_state(fmu_filepath, output_var='B_EG.T_room', conditions=conditions, use_preexisting_data=False, plot_dymola_values=False)

    unzipdir = extract(fmu_filepath)  # extract the FMU
    model_description = read_model_description(fmu_filepath)  # read model description
    vrs = {var.name: var.valueReference for var in model_description.modelVariables}  # collect the value references
    fmu = FMU2Slave(guid=model_description.guid,
                    unzipDirectory=unzipdir,
                    modelIdentifier=model_description.coSimulation.modelIdentifier,
                    instanceName='instance1')
    fmu.instantiate()  # initialize the FMU
    fmu.setupExperiment(startTime=0.0)
    fmu.enterInitializationMode()
    fmu.exitInitializationMode()

    # set steady state
    for key, value in steady_state_values.items():
        try:
            fmu.setReal([vrs[key]], [value])
            print(f"[Info] Initialized {key} with steady state value: {value[0]}")
        except: pass

    fmu.setBoolean([vrs['HIL_mode_setting']], [True])  # activate HIL mode of the fmu

    output_variables = {
        'HIL_T_VL': None,
        'T_room': None,
        'T_RL_Gebaeude': None
    }

    for key in output_variables.keys():
        output_variables[key] = vrs[key]  # read value references

    vr_T_RL_Building = vrs['T_RL_Gebaeude']
    vr_T_VL_Building = vrs['HIL_T_VL']
    results = {}
    simtime = 0.0
    '''enter simulation loop, yield a T_RL_Building value for every time step'''
    while True:
        yielded_val = yield  # take value from sensor as input
        if yielded_val != None:
            T_VL_Building = yielded_val

        fmu.setReal([vr_T_VL_Building], [T_VL_Building])
        
        # do one step
        fmu.doStep(currentCommunicationPoint=simtime, communicationStepSize=step_size)
        simtime += step_size

        # save results in file
        for key, value in output_variables.items():
            results[key] = np.round(fmu.getReal([value])[0], 2)
        results_df = pd.DataFrame(results, index=[simtime])

        if simtime == step_size:  # first step, create new savefile
            results_df.index.name = 'simtime'
            results_df.to_csv(savefile)

        else:  # savefile already exists -> add a new row
            results_df.to_csv(savefile, mode='a', header=False)

        T_RL_Building = fmu.getReal([vr_T_RL_Building])[0] - 273.15  # get the current value, convert to °C

        yield T_RL_Building
    
if __name__ == '__main__':
    # just for testing
    T_VL_Building_vals = np.linspace(50, 60, 1000).tolist()
    T_RL_Building_vals = []
    
    building = gen_T_RL_Building(fmu_filepath='fmu/simmodell.fmu', savefile='experiments/HIL_results.csv', step_size=60, initial_VL_value=T_VL_Building_vals[0])  # make building generator
    next(building)  # initialize generator

    for T_VL_Building in T_VL_Building_vals:  # in experiment call the generator every timestep with the real value
        T_RL_Building = None
        while T_RL_Building == None:
            T_RL_Building = building.send(T_VL_Building)
        T_RL_Building_vals.append(T_RL_Building)  # just for testing, otherwise use that value for the experiment

    # plot just for testing
    plt.plot(T_VL_Building_vals, label='T_VL', color='red')
    plt.plot(T_RL_Building_vals, label='T_RL', color='blue')
    plt.ylabel('Temperatur [°C]')
    plt.xlabel('Zeit [min]')
    plt.title('HIL Building Generator test')
    plt.legend()
    plt.show()
