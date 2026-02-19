import random
import numpy as np
import torch

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

import os
import time
from fmugym import FMUGymConfig, VarSpace, State2Out, TargetValue
from sb3_contrib import RecurrentPPO
import pandas as pd

from training_FMUEnv import *
from functions.helper.callback import *
from functions.helper.training_helper_functions import *
from functions.fmu_scripts.generate_baseline_results import *
from functions.fmu_scripts.generate_agent_results import *
from functions.plot.plot_temperatures import *
from functions.plot.plot_control_signals import *
from functions.plot.plot_energy_usage import *
from functions.plot.plot_boptest_score import *
from functions.helper.curriculum_manager import *
from functions.plot.plot_audc import *


which_agents = 'perrys'
compare_baseline = True
compare_untrained_agent = True
setting_plot_audc = True
curriculum_max_difficulty_level = 2

results_dir = "temp/saved_results"
os.makedirs(results_dir, exist_ok=True)

'''
coloring scheme

lv0 -> blue
lv1 -> green
lv2 -> purple
heatcurve -> red
untrained -> grey
other -> orange, brown, pink, olive

'''

print(f'Agent(s): {which_agents}')
print(f'Max Level: {curriculum_max_difficulty_level}')

if which_agents == 'perrys':  # all the single perrys
    agents = {
        'Agent Stufe 0' : {
            'path':'agents/trained_models/perry/perry0.zip',
            'color':'blue'
            },
        'Agent Stufe 1' : {
            'path':'agents/trained_models/perry/perry1.zip',
            'color':'green'
            },
        'Agent Stufe 2' : {
            'path':'agents/trained_models/perry/perry2.zip',
            'color':'purple'
            },
    }

elif which_agents == '200k':  # 200 k training steps vs 30 k
    agents = {
        '30k Trainingsschritte' : {
            'path':'agents/trained_models/perry/perry0.zip',
            'color':'olive'
            },
        '200k Trainingsschritte' : {
            'path':'agents/trained_models/200k_steps_lv0_checkpoints/recurrent_ppo_agent_200000_steps.zip',
            'color':'orange'
            },
    }

elif which_agents == 'curriculum_metrics':  # curriculum metrics comparison
    agents = {
        'Curriculum nach Schritten' : {
            'path':'agents/trained_models/perry/perry1.zip',
            'color':'orange'
            },
        'Curriculum nach Reward' : {
            'path':'agents/trained_models/vergleich_metric_reward.zip',
            'color':'green'
            },
    }

elif which_agents == 'weather':  # just display weather data
    agents = {
        'Wetterdaten' : {
            'path':'agents/trained_models/perry/perry0.zip',
            'color':'skyblue'
            },
    }

elif which_agents == 'batch':
    agents = {
        'Agent Stufe 0: batch_size=64, n_epochs=4' : {
            'path':'agents/trained_models/perry/perry0.zip',
            'color':'blue'
            },
        'Agent Stufe 0: batch_size=128, n_epochs=10' : {
            'path':'agents/best_model.zip',
            'color':'orange'
            },
        }


clock_start_time = time.time()  # start clock

'''define variables and generate results'''
additional_output_vars = ['Q_WP',
                            'V_jun_RL_1.port_2.m_flow',
                            'CTRL_DWV.y',
                            'from_degC1.u',
                            'B_EG.surf_surBou[1].T',
                            'B_EG.surf_conBou[1].T',
                            'B_EG.surf_conBou[2].T',
                            'wP.port_a1.m_flow',  # m_flow through wp
                            'B_weaDat.weaBus.TDryBul',
                            'switch_control_setting1.y',  # T_VL_WP after switch
                            'heizkurve_gleitend.T_VL',  # T_VL_WP from heatcurve block
                            'T_sou_WP',
                            'T_VL_WP',
                            'T_VL_Gebaeude',
                            'T_RL_Gebaeude',
                            ]
stop_time = 24*3600  # episode time [s], used for start of training and evaluation
total_timesteps = 6e4  # total learning timesteps
additional_timesteps = 1e5  # steps for further training of existing agent
setpoint_temperature = 21.5 + 273.15  # T_set_room
sim_step_size = 60
action_step_size = 60
eval_freq = 5000  # steps between checkpoint

fixed_eval_days = [4, 92, 268]

inputs = VarSpace('inputs')
input_noise = VarSpace('input_noise')
inputs.add_var_box('agent_T_VL', 0.0, 1.0)
input_noise.add_var_box('agent_T_VL', 0.0, 0.0)

outputs = VarSpace('outputs')
output_noise = VarSpace("output_noise")
outputs.add_var_box('nSet_WP', 0.0, 1.0)
output_noise.add_var_box('nSet_WP', 0.0, 0.0)
outputs.add_var_box('T_room', 0.0, 1000)
outputs.add_var_box('T_RL_WP', 0.0, 1000)

#print('[STÖRUNG] T_room: -0.5, 0.5')
#output_noise.add_var_box('T_room', -0.5, 0.5)
output_noise.add_var_box('T_room', 0.0, 0.0)

print('[STÖRUNG] T_RL_WP: -0.29, 0.29')
output_noise.add_var_box('T_RL_WP', -0.29, 0.29)
#output_noise.add_var_box('T_RL_WP', 0.0, 0.0)

for output_var in additional_output_vars:
    outputs.add_var_box(output_var, 0.0, 1000)
    output_noise.add_var_box(output_var, 0.0, 0.0)

random_vars = VarSpace("random_vars")  # randomized dynamics parameters and their range of values
set_point_map = State2Out("set_point_map")  # map state variables to corresponding outputs of Modelica Model

# set point values for the start and stop of the trajectory
set_point_nominal_start = TargetValue("set_point_nominal_start")
set_point_nominal_start.add_target('T_room', setpoint_temperature)
set_point_stop = VarSpace("set_point_stop")
set_point_stop.add_var_box("T_room", setpoint_temperature, setpoint_temperature)  # setpoint temperature stays constant

# allowed range of output values, if exceeded -> truncation of the episode
terminations = VarSpace("terminations")
truncation_tolerance = 8
terminations.add_var_box('T_room', setpoint_temperature - truncation_tolerance, setpoint_temperature + truncation_tolerance)

config = FMUGymConfig(fmu_path=os.path.abspath('fmu/simmodell.fmu'),
                    start_time=0.0,
                    stop_time=stop_time,
                    sim_step_size=sim_step_size,
                    action_step_size=action_step_size,
                    inputs=inputs,
                    input_noise=input_noise,
                    outputs=outputs,
                    output_noise=output_noise,
                    random_vars=random_vars,
                    set_point_map=set_point_map,
                    set_point_nominal_start=set_point_nominal_start,
                    set_point_stop=set_point_stop,
                    terminations=terminations,
                    )

policy_kwargs = dict(
            lstm_hidden_size=128,
            n_lstm_layers=1,
            shared_lstm=False,  # if actor and critic use the same LSTM
            enable_critic_lstm=True,
            net_arch=dict(pi=[64, 64], vf=[64, 64])
        )

# create curriculum manager
curriculum = CurriculumManager(
    episode_days=stop_time/(3600*24), 
    steps_per_level=15000,
    mode='training',
    max_difficulty_level=curriculum_max_difficulty_level,
    corrupted_variables=['T_RL_WP'],
    )

# create environment
env = FMUEnv(config)
env.curriculum = curriculum

# generate results for all selected agents
if curriculum_max_difficulty_level == 0: fixed_eval_days = None
eval_params = None

for _name, _data in agents.items():

    model = RecurrentPPO.load(_data['path'], env=env, device='cpu', print_system_info=False)
    model.set_random_seed(SEED)  # deterministic

    if eval_params == None:
        results, eval_params, _ = generate_agent_results(env=env, eval_level=curriculum_max_difficulty_level, model=model, days=fixed_eval_days, SEED=SEED)
    else:
        results, _, _ = generate_agent_results(env=env, eval_level=curriculum_max_difficulty_level, model=model, days=fixed_eval_days, eval_params=eval_params, SEED=SEED)

    agents[_name]['results'] = results

# generate results for comparison
if compare_untrained_agent:
    results, _, _ = generate_agent_results(env, curriculum_max_difficulty_level, policy_kwargs=policy_kwargs, eval_params=eval_params, days=fixed_eval_days, SEED=SEED)
    agents = {'Agent untrainiert': {'results' : results, 'color': 'grey'}, **agents}

    if setting_plot_audc:
        results_corruption_0, _, _ = generate_agent_results(env, curriculum_max_difficulty_level, policy_kwargs=policy_kwargs, eval_params=eval_params, SEED=SEED, corruption=False)
        results_corruption_1, _, _ = generate_agent_results(env, curriculum_max_difficulty_level, policy_kwargs=policy_kwargs, eval_params=eval_params, SEED=SEED, corruption=True)

        agents['Agent untrainiert']['results_corruption_0'] = results_corruption_0
        agents['Agent untrainiert']['results_corruption_1'] = results_corruption_1

if compare_baseline:
    results = generate_baseline_results(env, curriculum_max_difficulty_level, config, eval_params, additional_output_vars, days=fixed_eval_days)
    agents = {'Heizkurve': {'results' : results, 'color': 'red'}, **agents}

    if setting_plot_audc:
        results_corruption_0 = generate_baseline_results(env, curriculum_max_difficulty_level, config, eval_params, additional_output_vars, days=fixed_eval_days, corruption=False)
        results_corruption_1 = generate_baseline_results(env, curriculum_max_difficulty_level, config, eval_params, additional_output_vars, days=fixed_eval_days, corruption=True)
        agents['Heizkurve']['results_corruption_0'] = results_corruption_0
        agents['Heizkurve']['results_corruption_1'] = results_corruption_1

# plot results for all selected agents
if setting_plot_audc: plot_audc(agents, env, n_episodes=1)
plot_params = compute_plot_params(agents)
plot_outside_temperature(agents, plot_params)
plot_air_temperatures(agents, plot_params)
plot_T_VL_Gebaeude(agents, plot_params)
plot_control_signal_twv(agents, plot_params)
plot_control_signal_wp(agents, plot_params)
plot_energy_usage(config, agents)
plot_thermal_discomfort_summenhaeufigkeit(agents)


# print end message to console
clock_stop_time = time.time()
ges_time = (clock_stop_time - clock_start_time)
print(f"[Info] Finished run in {ges_time:.2f} s = {(ges_time/60):.2f} min = {(ges_time/3600):.2f} h ")  # complete time for run
