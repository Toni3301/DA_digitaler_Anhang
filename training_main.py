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
import copy
import time
from fmugym import FMUGymConfig, VarSpace, State2Out, TargetValue
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from stable_baselines3.common.monitor import Monitor

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
from functions.helper.plot_helper import *


os.environ["DYMOLA_RUNTIME_MESAGES"] = "0"  # silence unnecessary dymola warnings

# start tensorboard: poetry run tensorboard --logdir agents/logs

'''##### training parameters #####'''
agent_path = 'agents/best_model.zip'
#agent_path = 'agents/trained_models/perry/perry0.zip'
#agent_path = 'agents/trained_models/perry/perry1.zip'
#agent_path = 'agents/trained_models/perry/perry2.zip'
#agent_path = 'temp/checkpoints/recurrent_ppo_agent_5000_steps.zip'
#agent_path = 'agents/trained_models/perry/perry0_checkpoints/recurrent_ppo_agent_5000_steps.zip'

print(f'agent_path = {agent_path}')

use_preexisting_agent = False
train_on = False
curriculum_max_difficulty_level = 0
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
                            ]
stop_time = 24*3600  # episode time [s], used for start of training and evaluation
total_timesteps = 6e4  # total training timesteps
additional_timesteps = 1e5  # steps for further training of existing agent
setpoint_temperature = 21.5 + 273.15  # T_set_room
sim_step_size = 60
action_step_size = 60
eval_freq = 5000  # steps between checkpoints

policy_kwargs = dict(
            lstm_hidden_size=128,
            n_lstm_layers=1,
            shared_lstm=False,  # if actor and critic use the same LSTM
            enable_critic_lstm=True,
            net_arch=dict(pi=[64, 64], vf=[64, 64])
        )

fixed_eval_days = [4, 92, 180, 268]  # winter, spring, summer, autumn
#fixed_eval_days = None

clock_start_time = time.time()  # start clock

'''I/O for training'''
# providing inputs, outputs and their noises with range of values
inputs = VarSpace('inputs')
inputs.add_var_box('agent_T_VL', 0.0, 1.0)

input_noise = VarSpace('input_noise')
input_noise.add_var_box('agent_T_VL', 0.0, 0.0)

outputs = VarSpace('outputs')
outputs.add_var_box('nSet_WP', 0.0, 1.0)
outputs.add_var_box('T_sou_WP', 0.0, 1000)
outputs.add_var_box('T_VL_WP', 0.0, 1000)
outputs.add_var_box('T_VL_Gebaeude', 0.0, 1000)
outputs.add_var_box('T_RL_Gebaeude', 0.0, 1000)
outputs.add_var_box('T_room', 0.0, 1000)
outputs.add_var_box('T_RL_WP', 0.0, 1000)

output_noise = VarSpace("output_noise")
output_noise.add_var_box('nSet_WP', 0.0, 0.0)
output_noise.add_var_box('T_sou_WP', 0.0, 0.0)
output_noise.add_var_box('T_VL_WP', 0.0, 0.0)
output_noise.add_var_box('T_VL_Gebaeude', 0.0, 0.0)
output_noise.add_var_box('T_RL_Gebaeude', 0.0, 0.0)
output_noise.add_var_box('T_room', 0.0, 0.0)
output_noise.add_var_box('T_RL_WP', -0.29, 0.29)  # corruption

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
                    terminations=terminations
                    ) 

# create curriculum manager
curriculum = CurriculumManager(
    episode_days=stop_time/(3600*24), 
    steps_per_level=15000,
    mode='training',
    max_difficulty_level=curriculum_max_difficulty_level,
    corrupted_variables=['T_RL_WP'],
    )

# create environments
env = FMUEnv(config)
env.curriculum = curriculum
eval_env_training = FMUEnv(config)
eval_env_training.curriculum = copy.deepcopy(curriculum)
eval_env_training.curriculum.mode = 'evaluation'
eval_env_training = Monitor(eval_env_training)

if use_preexisting_agent and os.path.isfile(agent_path):
    model = RecurrentPPO.load(agent_path, env=env, tensorboard_log='./agents/logs')
    total_timesteps = additional_timesteps

    if agent_path == 'agents/recurrent_ppo_best.zip':
        # load metadata for best agent
        meta_path = agent_path.replace(".zip", "_meta.npz")
        if os.path.isfile(meta_path):
            meta = np.load(meta_path)
            best_step = int(meta.get("best_step", -1))
            best_mean_reward = float(meta.get("best_mean_reward", np.nan))
            print(f"[Info] Loaded best agent: Step {best_step}, mean_reward={best_mean_reward:.2f}")
        else:
            print("[Warning] No metadata for the best agent was found.")

else:
    print("[Info] Initializing new Agent.")

    # my hyperparams
    model = RecurrentPPO(
        policy="MultiInputLstmPolicy",
        env=env,
        learning_rate=1e-4,
        vf_coef=0.25,
        n_steps=1440,
        #batch_size=64,
        #n_epochs=4,
        gamma=0.99,
        gae_lambda=0.95,
        ent_coef=0.001,
        verbose=1,
        tensorboard_log='./agents/logs',
        policy_kwargs=policy_kwargs,
    )


'''##### TRAINING #####'''
if train_on or not use_preexisting_agent:
    print(f'[Info] Training agent for {int(total_timesteps)} timesteps...')

    # delete old checkpoints
    checkpoint_dir = "./temp/checkpoints"
    if os.path.exists(checkpoint_dir):
        for filename in os.listdir(checkpoint_dir):
            file_path = os.path.join(checkpoint_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                pass
    else:
        os.makedirs(checkpoint_dir, exist_ok=True)

    eval_callback = CurriculumEvalCallback(
        curriculum=curriculum,
        eval_env=eval_env_training,
        n_eval_episodes=1,
        eval_freq=5000,
        deterministic=True,
        best_model_save_path="agents/",
        log_path="agents/logs",
        verbose=1
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=5000,
        save_path="temp/checkpoints",
        name_prefix="recurrent_ppo_agent"
    )


    model.learn(
        total_timesteps=total_timesteps,
        tb_log_name="log",
        callback=CallbackList([
            eval_callback,
            checkpoint_callback,
            RewardLoggingCallback(),
        ])
    )


'''##### EVALUATION #####'''
model = RecurrentPPO.load(agent_path, env=env, tensorboard_log='./agents/logs')  # load chosen agent
eval_level = curriculum_max_difficulty_level
if curriculum_max_difficulty_level == 0: fixed_eval_days = None

agent_results, eval_params, _ = generate_agent_results(env, eval_level, model=model, days=fixed_eval_days, SEED=SEED)
untrained_agent_results, _, _ = generate_agent_results(env, eval_level, policy_kwargs=policy_kwargs, eval_params=eval_params, days=fixed_eval_days, SEED=SEED)
baseline_results = generate_baseline_results(env, eval_level, config, eval_params=eval_params, additional_output_vars=additional_output_vars, days=fixed_eval_days)

results_total = {
    'Heizkurve' : {'results':baseline_results, 'color':'red'},
    'Agent untrainiert' : {'results':untrained_agent_results, 'color':'grey'},
    'Agent' : {'results':agent_results, 'color':'blue'},
}


'''##### plotting #####'''
plot_params = compute_plot_params(results_total)
plot_outside_temperature(results_total, plot_params)
plot_air_temperatures(results_total, plot_params)
plot_T_VL_Gebaeude(results_total, plot_params)
plot_control_signal_twv(results_total, plot_params)
plot_control_signal_wp(results_total, plot_params)
plot_energy_usage(config, results_total)
plot_thermal_discomfort_summenhaeufigkeit(results_total)


# print end message to console
clock_stop_time = time.time()
ges_time = (clock_stop_time - clock_start_time)
print(f"[Info] Finished run in {ges_time:.2f} s = {(ges_time/60):.2f} min = {(ges_time/3600):.2f} h ")  # complete time for run
