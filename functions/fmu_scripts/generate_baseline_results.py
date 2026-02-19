from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import shutil
import pandas as pd
import os
import numpy as np

from functions.fmu_scripts.get_steady_state import get_steady_state
from functions.fmu_scripts.set_conditions import set_conditions
from functions.functions.heatcurves import heatcurve_boi
from functions.helper.training_helper_functions import *
from functions.fmu_scripts.sample_initial_conditions import *

def generate_baseline_results(env, eval_level, config, eval_params=None, 
                              additional_output_vars=None, agent_T_VL=100, 
                              days=None, corruption=False):

    os.environ["DYMOLA_RUNTIME_MESSAGES"] = "0"
    daytime = 24*3600
    env.curriculum.mode = 'evaluation'

    # set eval params
    if eval_params is None:
        env.curriculum.eval_level = eval_level
        eval_params = env.curriculum.get_episode_params()

    if days is None:
        day_count = 1
    else:
        day_count = len(days)
        eval_params['start_time'] = days[0]*daytime
        eval_params['stop_time'] = days[0]*daytime + daytime
        eval_params['episode_duration'] = daytime

    env.curriculum_params = eval_params

    # fmu setup
    fmu_filepath = config.fmu_path
    start_time, stop_time = eval_params['start_time'], eval_params['stop_time']
    step_size = config.sim_step_size

    model_description = read_model_description(fmu_filepath)
    vrs = {var.name: var.valueReference for var in model_description.modelVariables}

    # outputs
    if additional_output_vars is None:
        output_vars = [var.name for var in model_description.modelVariables if var.causality == 'output']
    else:
        if not isinstance(additional_output_vars, list):
            additional_output_vars = [additional_output_vars]
        fmu_outputs = [var.name for var in model_description.modelVariables if var.causality == 'output']
        output_vars = list(dict.fromkeys(additional_output_vars + fmu_outputs))

    vr_output = [vrs[vr] for vr in output_vars]

    columns = ['time', 'time_h'] + output_vars
    data = []
    total_steps = 0

    for i in range(day_count):
        if days is not None and i > 0:
            start_time = days[i]*daytime
            stop_time = days[i]*daytime + daytime
            env.curriculum_params = {
                'start_time': start_time,
                'stop_time': stop_time,
                'episode_duration': daytime,
            }

        obs, _ = env.reset()

        with suppress_fmu_output_context():
            unzipdir = extract(fmu_filepath)
            fmu = FMU2Slave(
                guid=model_description.guid,
                unzipDirectory=unzipdir,
                modelIdentifier=model_description.coSimulation.modelIdentifier,
                instanceName='instance1'
            )
            fmu.instantiate()
            fmu.setupExperiment(startTime=start_time, stopTime=stop_time)
            fmu.enterInitializationMode()
            fmu.exitInitializationMode()

            simtime = start_time

            # set initial conditions
            T_outside = fmu.getReal([vrs['T_sou_WP']])[0] - 273.15
            initial_conditions = sample_initial_conditions(fmu_filepath=config.fmu_path, T_outside=T_outside, use_preexisting_data=True)
            initial_conditions['WP_manual_control_setting'] = True
            initial_conditions['agent_control_setting'] = True
            initial_conditions['agent_T_VL'] = agent_T_VL
            set_conditions(initial_conditions, fmu, vrs, initial_conditions=True)

            # sim loop
            while simtime < stop_time:
                # heatcurve control
                T_outside = fmu.getReal([vrs['T_sou_WP']])[0] - 273.15
                WP_T_VL = heatcurve_boi(T_outside)
                set_conditions({'WP_T_VL': WP_T_VL}, fmu, vrs)

                fmu.doStep(currentCommunicationPoint=simtime, communicationStepSize=step_size)
                simtime += step_size

                # corruption
                if corruption:
                    noise_dict = {}
                    for out_name in output_vars:
                        sigma = 0.0
                        if out_name == 'T_RL_WP':
                            sigma = 0.29
                            single_noise = np.random.normal(0.0, sigma) + 0.15  # Bias
                        else:
                            single_noise = 0.0
                        noise_dict[out_name] = single_noise
                else:
                    noise_dict = {out_name: 0.0 for out_name in output_vars}

                row = [simtime]
                if days is None:
                    current_time_h = (total_steps * step_size + eval_params['start_time']) / 3600.0
                else:
                    current_time_h = (total_steps * step_size) / 3600.0
                total_steps += 1
                row.append(current_time_h)

                for idx, vr in enumerate(output_vars):
                    val = fmu.getReal([vrs[vr]])[0] + noise_dict.get(vr, 0.0)
                    row.append(val)

                data.append(row)

            fmu.terminate()
            fmu.freeInstance()
            shutil.rmtree(unzipdir, ignore_errors=True)

    env.curriculum.mode = 'training'

    result = pd.DataFrame(data, columns=columns)
    return result
