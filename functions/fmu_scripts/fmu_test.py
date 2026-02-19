import time
import pandas as pd
from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import numpy as np
import shutil
import matplotlib.pyplot as plt
from functions.fmu_scripts.get_steady_state import get_steady_state


def fmu_test(stop_time, output_var, use_preexisting_data=False, step_size=60, fmu_filepath='./fmu/simmodell.fmu'):
    # examine the fmu
    steady_state_values = get_steady_state(fmu_filepath, output_var, use_preexisting_data=use_preexisting_data, plot_dymola_values=True)

    # extract the FMU
    unzipdir = extract(fmu_filepath)
    model_description = read_model_description(fmu_filepath)

    # collect the value references
    vrs = {var.name: var.valueReference for var in model_description.modelVariables}

    # read the value references for the variables that will be written to the results file
    vr_out_sigbus_nset = vrs['sigBus.nSet']
    vr_out_T_source = vrs['WP_senT_VL_sou.T_degC']
    vr_out_WP_T_RL = vrs['WP_senT_RL.T_degC']
    vr_out_B_Qp_radiator = vrs["B_EG.Qp_radiator"]
    vr_out_B_T_room = vrs["B_EG.T_room"]

    # initialize the FMU
    fmu = FMU2Slave(guid=model_description.guid,
                    unzipDirectory=unzipdir,
                    modelIdentifier=model_description.coSimulation.modelIdentifier,
                    instanceName='instance1')

    fmu.instantiate()
    fmu.setupExperiment(startTime=0.0)
    fmu.enterInitializationMode()
    fmu.exitInitializationMode()

    # initialize fmu in steady state
    for key, value in steady_state_values.items():
        try:
            fmu.setReal([vrs[key]], [value])
            print(f"[Info] Initialized {key} with steady state value: {value[0]}")
        except:
            # print(f"COULDN'T INITIALIZE {key} with steady state value: {value[0]}")
            pass

    clock_start_time = time.time()  # start clock

    # simulation loop
    values = []
    simtime = 0.0
    while simtime < stop_time:
        # do one step
        fmu.doStep(currentCommunicationPoint=simtime, communicationStepSize=step_size)
        simtime += step_size

        # get the values for outputs
        vr_out_sigbus_nset_value, vr_out_T_source_value, vr_out_WP_T_RL_value, vr_out_B_qp_radiator_value, vr_out_B_T_room_value = \
            fmu.getReal([vr_out_sigbus_nset, vr_out_T_source, vr_out_WP_T_RL, vr_out_B_Qp_radiator, vr_out_B_T_room])

        # append the result
        values.append((simtime, vr_out_sigbus_nset_value, vr_out_T_source_value, vr_out_WP_T_RL_value, vr_out_B_qp_radiator_value, vr_out_B_T_room_value))

    # delete all variables and reset the FMU for the next round
    fmu.terminate()
    fmu.freeInstance()
    shutil.rmtree(unzipdir, ignore_errors=True)

    # convert the result to a structured NumPy array
    result = np.array(values, dtype=np.dtype([('time', np.float64), 
                                                ('sigBus.nSet', np.float64), 
                                                ('WP_T_source', np.float64), 
                                                ('WP_T_RL', np.float64), 
                                                ('B_Qp_radiator', np.float64), 
                                                ('B_T_room', np.float64)]))

    # structure and save result for evaluation
    result = pd.DataFrame(result)
    print(result)

    clock_stop_time = time.time()  # stop clock

    # plot fmpy results
    plt.plot(result['time']/(60*60), result['B_T_room'] - 273.15, label='fmpy', color='b')
    plt.xlabel('Zeit [h]')
    plt.ylabel('Temperatur [°C]')
    plt.title('Raumtemperatur über der Zeit')
    plt.axhline(y=23, color='red', linestyle='--', linewidth=1, label='T_set = 23 °C')
    plt.gca().spines['left'].set_position('zero')
    plt.legend()
    plt.grid()
    plt.show()

    # print end message to console
    execution_time = (clock_stop_time - clock_start_time)
    print(f"Finished run in {execution_time:.2f} seconds")


if __name__ == '__main__':
    stop_time = 24 * 3600  # [s] time to be simulated
    step_size = 60 # [s]
    output_var = 'heizkurve_gleitend.T_VL'
    fmu_filepath = 'fmu/simmodell.fmu'

    fmu_test(stop_time, output_var, use_preexisting_data=False, fmu_filepath=fmu_filepath)
