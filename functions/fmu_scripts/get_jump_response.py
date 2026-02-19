from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import shutil
import matplotlib.pyplot as plt
from functions.fmu_scripts.get_steady_state import get_steady_state
import numpy as np
import time
from functions.fmu_scripts.set_conditions import set_conditions

'''pid controller parameters:'''
# WP
# k -> CTRL_WP_k
# Ti -> CTRL_WP_Ti
# Td -> CTRL_WP_Td

# TWV
# k -> CTRL_TWV_k
# Ti -> CTRL_TWV_Ti
# Td -> CTRL_TWV_Td

def jump_val(time, start, end, jumptime=5000):
    '''Sprungfunktion'''
    if time < jumptime:
        return start
    else:
        return end

def get_jump_response(fmu_filepath, input_var, output_var, start, end, conditions=None, experimental_data=None, tolerance=5e-6, max_simtime=1000000, steady_vals=50, debug=False, use_preexisting_data=False, jumptime=10*3600):
    # label dictionary for better plot descriptions
    label_dict = {
        'WP_senT_VL.T': 'WP Vorlauftemperatur ist',
        'WP_T_VL': 'WP Vorlauftemperatur soll',
        'agent_T_VL': 'Gebäude Vorlauftemperatur soll',
        'VS_senT_VL.T': 'Gebäude Vorlauftemperatur ist'
    }

    model_description = read_model_description(fmu_filepath)

    # get steady state values for the start of the input function
    steady_state_values = get_steady_state(fmu_filepath, 'B_EG.T_room', conditions={'agent_T_VL':start, 'agent_control_setting':True}, use_preexisting_data=use_preexisting_data)

    # get value references
    vrs = {variable.name: variable.valueReference for variable in model_description.modelVariables}
    vr_input = vrs[input_var]
    vr_output = vrs[output_var]

    # extract and initialize fmu
    unzipdir = extract(fmu_filepath)
    fmu = FMU2Slave(guid=model_description.guid,
                    unzipDirectory=unzipdir,
                    modelIdentifier=model_description.coSimulation.modelIdentifier,
                    instanceName='instance1')
    fmu.instantiate()
    fmu.setupExperiment(startTime=0)
    fmu.enterInitializationMode()
    fmu.exitInitializationMode()

    clock_start_time = time.time()  # start clock

    simtime = 0
    # sim loop
    while simtime < max_simtime:

        if simtime == 0:  # initialize all variables and set all conditions
            step_size = 5
            rows = []
            steady_var_vals = []

            # initialize fmu in steady state
            for key, value in steady_state_values.items():
                try: fmu.setReal([vrs[key]], [value])
                except: pass
            
            fmu.setBoolean([vrs['agent_control_setting']], [False])  # deactivate agent control

            # enable given conditions for the sim
            set_conditions(conditions, fmu, vrs)

            fmu.setReal([vr_input], [start])  # set setpoint start value

        # input function -> jump function
        fmu.setReal([vr_input], [jump_val(simtime, start, end, jumptime=jumptime)])

        # simulation step
        fmu.doStep(currentCommunicationPoint=simtime, communicationStepSize=step_size)
        simtime += step_size

        # save values
        output_val = fmu.getReal([vr_output])[0]

        if simtime < jumptime:  # before jump
            rows.append((simtime, start, output_val))

        else:  # after jump
            rows.append((simtime, end, output_val))
            steady_var_vals.append(output_val)

            if len(steady_var_vals) > steady_vals:

                if len(rows) > steady_vals:
                    steady_var_vals.pop(0)  # remove oldest value

                if max([abs(val - np.mean(steady_var_vals)) for val in steady_var_vals]) <= tolerance:
                    break

    # end and clean up
    fmu.terminate()
    fmu.freeInstance()
    shutil.rmtree(unzipdir, ignore_errors=True)

    # convert results
    result = np.array(rows, dtype=[('time', np.float64), (input_var, np.float64), (output_var, np.float64)])
    
    clock_stop_time = time.time()  # stop clock
    
    '''plot the results'''
    time_vals = (result['time'] - jumptime)/ (60*60)
    input_vals = result[input_var]
    output_vals = result[output_var]

    print("CTRL parameters:")

    if 'CTRL_WP_k' in conditions:
        print(f"  CTRL_WP_k = {conditions['CTRL_WP_k']}")
        print(f"  CTRL_WP_Ti = {conditions['CTRL_WP_Ti']}")
        print(f"  CTRL_WP_Td = {conditions['CTRL_WP_Td']}")

    if 'CTRL_TWV_k' in conditions:
        print(f"  CTRL_TWV_k = {conditions['CTRL_TWV_k']}")
        print(f"  CTRL_TWV_Ti = {conditions['CTRL_TWV_Ti']}")
        print(f"  CTRL_TWV_Td = {conditions['CTRL_TWV_Td']}")

    print(f"  WP_nSet_min = {conditions['WP_nSet_min']}")
    print(f"  WP_dT_on    = {conditions['WP_dT_on']}")
    print(f"  WP_dT_off   = {conditions['WP_dT_off']}")
          
    print(f"CPU time: {clock_stop_time - clock_start_time:.2f} s")
    plt.plot(time_vals, output_vals-273.15, label=label_dict[output_var], color="b")  # fmu jump response
    plt.plot(time_vals, input_vals, label=label_dict[input_var], color="r", linestyle='--')  # jump function

    if experimental_data != None:
        # plot experimental data into the same figure
        pass  # to be added

    plt.ylabel('Temperatur [°C]')
    plt.xlabel('Zeit [h]')
    plt.xlim(left=-0.5)

    if 'CTRL_TWV_k' not in conditions:
        plt.title('Sprungantwort Vorlauftemperatur WP')
    else:
        plt.title('Sprungantwort Vorlauftemperatur Gebäude')

    plt.grid()
    plt.legend()

    plt.show()

    return result


if __name__ == '__main__':
    fmu_filepath = 'fmu/simmodell.fmu'
    examined_ctrl = 'twv'

    CTRL_WP_k, CTRL_WP_Ti, CTRL_WP_Td = 5, 500, 0  # townhouse: 0.0001, 30, 1
    WP_nSet_min, WP_dT_on, WP_dT_off = 0.001, 10000, 10000  # townhouse: 0.3, 5, 10; my sim: 0.001, 2.8, -7.2; switch off: 0.001, 1000, 1000
    CTRL_TWV_k, CTRL_TWV_Ti, CTRL_TWV_Td = 0.02, 120, 0  # my sim: 0.05, 1200, 9

    jumptime = 10 * 3600

    for value in [1]:
        if examined_ctrl == 'wp':  # benötigt ein auf 0.5 gesetztes DWV!
            input_var, output_var = 'WP_T_VL', 'WP_senT_VL.T'
            start, end = 30, 60
            conditions = {
                'agent_control_setting':False,
                'WP_manual_control_setting':True,

                'CTRL_WP_k': CTRL_WP_k,
                'CTRL_WP_Ti': CTRL_WP_Ti,
                'CTRL_WP_Td': CTRL_WP_Td,
                'WP_nSet_min': WP_nSet_min,
                'WP_dT_on': WP_dT_on,  
                'WP_dT_off': WP_dT_off
            }

        elif examined_ctrl == 'twv':
            input_var, output_var = 'agent_T_VL', 'VS_senT_VL.T'
            start, end = 20, 35
            conditions = {
                'agent_control_setting':True,
                'WP_manual_control_setting':False,

                'CTRL_WP_k': CTRL_WP_k,
                'CTRL_WP_Ti': CTRL_WP_Ti,
                'CTRL_WP_Td': CTRL_WP_Td,

                'WP_nSet_min': WP_nSet_min,
                'WP_dT_on': WP_dT_on,  
                'WP_dT_off': WP_dT_off,

                # edit those:
                'CTRL_TWV_k': CTRL_TWV_k,
                'CTRL_TWV_Ti': CTRL_TWV_Ti,
                'CTRL_TWV_Td': CTRL_TWV_Td
            }


        get_jump_response(fmu_filepath, input_var, output_var, start, end, conditions, debug=True, use_preexisting_data=True, max_simtime=13*3600, tolerance=5e-3, jumptime=jumptime)

