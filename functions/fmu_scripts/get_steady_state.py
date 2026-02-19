## SETUP
import pandas as pd
from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import numpy as np
import matplotlib.pyplot as plt
import shutil
import pickle
import os
from functions.fmu_scripts.set_conditions import set_conditions
from functions.helper.training_helper_functions import *


def get_steady_state(fmu_filepath, output_var='B_EG.T_room', savefile='temp/steady_state_initialisation.pkl', dymola_simtime=108000, tolerance=5e-5, max_simtime=1000000, steady_vals=250, conditions=None, use_preexisting_data=False, plot_dymola_values=False, plot=True, full_output=False, verbose=True):
    os.environ["DYMOLA_RUNTIME_MESSAGES"] = "0"

    # check if there already is steady state data
    if savefile != None:
        if os.path.isfile(savefile) and use_preexisting_data:
            if verbose: print(f'Using preexisting steady state conditions. Delete file {savefile} to reset precalculations')
            with open(savefile, 'rb') as file:
                steady_state_values = pickle.load(file)
            return steady_state_values
    else:
        if verbose: print('[Info] Calculating steady state conditions...')

    with suppress_fmu_output_context():
        unzipdir = extract(fmu_filepath)  # extract the FMU
        model_description = read_model_description(fmu_filepath)  # read model description
        vrs = {var.name: var.valueReference for var in model_description.modelVariables}  # get value references
        fmu = FMU2Slave(guid=model_description.guid,
                        unzipDirectory=unzipdir,
                        modelIdentifier=model_description.coSimulation.modelIdentifier,
                        instanceName='instance1')
        
        # initialize fmu
        fmu.instantiate()
        fmu.setupExperiment(startTime=0.0)
        fmu.enterInitializationMode()
        fmu.exitInitializationMode()
        
        simtime = 0
        while simtime < max_simtime:

            if simtime == 0:  # initialize all variables and set all conditions
                step_size = 60
                steady_var_vals = []
                steady_state_reached = False
                time_values = []
                output_values = []

                # deactivate agent control
                fmu.setBoolean([vrs['agent_control_setting']], [False])

                # enable given conditions for the sim
                set_conditions(conditions, fmu, vrs)

            # do one step
            fmu.doStep(currentCommunicationPoint=simtime, communicationStepSize=step_size)
            simtime += step_size

            current_value = fmu.getReal([vrs[output_var]])[0]

            # save data for plotting
            time_values.append(simtime / (60*60))
            output_values.append(current_value - 273.15)

            '''check for steady state'''
            steady_var_vals.append(current_value)
            if len(steady_var_vals) > steady_vals:

                if len(steady_var_vals) > steady_vals:
                    steady_var_vals.pop(0)  # remove oldest value

                if max([abs(val - np.mean(steady_var_vals)) for val in steady_var_vals]) <= tolerance:
                    steady_state_reached = True
                    break

    if steady_state_reached:
        if verbose: print(f'[Info] Reached steady state after simulating {simtime:.2f} seconds.')
    else:
        if verbose: print("[Info] Didn't reach steady state, consider increasing the max simulation time or the tolerance")
    
    '''plot results of fmpy and dymola into one diagram'''
    if plot:
        if plot_dymola_values:
            # plot dymola results
            import DyMat
            dymola_T_room = DyMat.DyMatFile("fmu/dymola.mat").data(output_var)
            dymola_time = [i * (dymola_simtime/len(dymola_T_room)) / (60 * 60) for i in range(len(dymola_T_room))]  # timesteps [h]
            plt.plot(dymola_time, dymola_T_room - 273.15, label='dymola', color='r')

        plt.plot(time_values, output_values, label=f'fmu', color='b')  # output_var vs simulation time
        # plt.axhline(y=fmu.getReal([vrs['agent_T_VL']])[0]-273.15, color='r', linestyle='--', linewidth=1, label='T_Set')  # T_Set

        plt.xlabel('Simulation time [h]')
        plt.ylabel('Value')
        plt.title(f'{output_var} over time in dymola and fmu')
        plt.grid()
        plt.legend()
        plt.show()

    # retrieve steady state values for all variables
    steady_state_values = {}
    for vr, vr_value in vrs.items():
        if vr.startswith("B_EG.Solltemperatur.y"): continue
        steady_state_values[vr] = fmu.getReal([vr_value])[0]
    
    # save values to file
    if savefile != None:
        os.makedirs(os.path.dirname(savefile), exist_ok=True)
        with open(savefile, 'wb') as file:
            pickle.dump(steady_state_values, file)
        if verbose: print(f"[Info] Steady-state values saved to {savefile}\n")

    # clean up
    fmu.terminate()
    fmu.freeInstance()
    shutil.rmtree(unzipdir, ignore_errors=True)

    if full_output == True: return steady_state_values, output_values, time_values
    else: return steady_state_values


if __name__ == '__main__':
    fmu_filepath = '/fmu/simmodell.fmu'
    dymola_simtime = 108000  # [s]
    output_var = 'B_EG.T_room'
    # output_var = 'VS_senT_VL.T'
    # conditions = {'agent_T_VL':40, 'agent_control_setting':True}
    # conditions = {'Building_T_Set_VL.y':50, 'agent_control_setting':False}
    conditions = None
    debug = False

    get_steady_state(fmu_filepath, output_var, conditions=conditions, use_preexisting_data=False, plot_dymola_values=True, debug=debug, dymola_simtime=dymola_simtime)
