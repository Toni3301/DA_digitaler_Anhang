import os
import copy
import numpy as np
from fmugym import FMUGymConfig
from fmugym import VarSpace, State2Out, TargetValue


from stable_baselines3.common.monitor import Monitor
from sb3_contrib import RecurrentPPO

from training_FMUEnv import FMUEnv
from functions.fmu_scripts.generate_agent_results import generate_agent_results
from functions.helper.training_helper_functions import *
from functions.helper.mat_reader import *
from functions.helper.calculate_energy import *
from functions.helper.curriculum_manager import *

# --- Konfiguration ---
agent_paths = [
    "agents/trained_models/perry/perry1_checkpoints/recurrent_ppo_agent_5000_steps.zip",
    "agents/trained_models/perry/perry1_checkpoints/recurrent_ppo_agent_60000_steps.zip"
]
window = 20  # for sliding mean

stop_time = 24*3600  # episode time [s], used for start of training and evaluation
total_timesteps = 6e4  # total learning timesteps
additional_timesteps = 1e5  # steps for further training of existing agent
setpoint_temperature = 21.5 + 273.15  # T_set_room
sim_step_size = 60
action_step_size = 60
eval_freq = 5000  # steps between checkpoints
curriculum_max_difficulty_level = 0

# --- I/0 ---
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

output_noise = VarSpace("output_noise")
output_noise.add_var_box('nSet_WP', 0.0, 0.0)
output_noise.add_var_box('T_sou_WP', 0.0, 0.0)
output_noise.add_var_box('T_VL_WP', 0.0, 0.0)
output_noise.add_var_box('T_VL_Gebaeude', 0.0, 0.0)
output_noise.add_var_box('T_RL_Gebaeude', 0.0, 0.0)
output_noise.add_var_box('T_room', 0.0, 0.0)

additional_output_vars = ['Q_WP',
                            'V_jun_RL_1.port_2.m_flow',
                            'CTRL_DWV.y',
                            'from_degC1.u',
                            'B_EG.surf_surBou[1].T',
                            'B_EG.surf_conBou[1].T',
                            'B_EG.surf_conBou[2].T',
                            'wP.port_a1.m_flow',  # m_flow through wp
                            'T_RL_WP',
                            'B_weaDat.weaBus.TDryBul',
                            'switch_control_setting1.y',  # T_VL_WP after switch
                            'heizkurve_gleitend.T_VL',  # T_VL_WP from heatcurve block
                            ]

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


# FMU Env Config laden oder erstellen
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
    reward_threshold_increase=-7800,
    reward_threshold_decrease=-9000,
    steps_per_level=20000,
    mode='training',
    max_difficulty_level=curriculum_max_difficulty_level,
    metric='steps',
    )

# create environment
env = FMUEnv(config)
env.curriculum = curriculum

# Ergebnisse Dictionary
results = {}

# --- Schleife über Agenten ---
for agent_path in agent_paths:
    if not os.path.isfile(agent_path):
        print(f"[Warning] Agent file not found: {agent_path}")
        continue

    print(f"\n=== Processing {agent_path} ===")
    model = RecurrentPPO.load(agent_path, env=None, device="cpu")  # env wird bei generate_agent_results gesetzt

    # Deterministic=True
    agent_results_det, _, return_det = generate_agent_results(
        env=env,
        eval_level=0,
        model=model,
        deterministic=True
    )

    # Deterministic=False
    agent_results_stoch, _, return_stoch = generate_agent_results(
        env=env,
        eval_level=0,
        model=model,
        deterministic=False
    )

    # Werte extrahieren
    sim_step_size = config.sim_step_size
    floor_area = 72

    def compute_energy_and_cop(results):
        T_sou = results['T_sou_WP'] - 273.15
        T_VL = results['T_VL_WP'] - 273.15
        nSet = results['nSet_WP']

        WP_tableP_ele = mat_reader_wp('fmu/WP_tableP_ele.mat')
        WP_tableP_ele = create_wp_interpolator(WP_tableP_ele)
        WP_tableQdot_con = mat_reader_wp('fmu/WP_tableQdot_con.mat')
        WP_tableQdot_con = create_wp_interpolator(WP_tableQdot_con)

        Q_use, P_use = calculate_energy(sim_step_size, T_VL, T_sou, nSet, WP_tableQdot_con, WP_tableP_ele)
        Q_sum = np.sum(Q_use) / floor_area
        P_sum = np.sum(P_use) / floor_area
        COP = Q_sum / P_sum
        return Q_sum, P_sum, COP

    Q_det, P_det, COP_det = compute_energy_and_cop(agent_results_det)
    Q_stoch, P_stoch, COP_stoch = compute_energy_and_cop(agent_results_stoch)

    results[agent_path] = {
        "deterministic": {
            "Q": Q_det, 
            "P": P_det, 
            "COP": COP_det, 
            "return": return_det,
            "actions": agent_results_det['action']  # hier die Aktionen speichern
        },
        "stochastic": {
            "Q": Q_stoch, 
            "P": P_stoch, 
            "COP": COP_stoch, 
            "return": return_stoch,
            "actions": agent_results_stoch['action']  # hier die Aktionen speichern
        }
    }

# --- Ausgabe ---
for agent_path, vals in results.items():
    print(f"\n=== Agent: {agent_path} ===")
    print("Stochastic (Gaussian head):")
    print(f"  Q [kWh/m²]: {vals['stochastic']['Q']:.5f}")
    print(f"  P [kWh/m²]: {vals['stochastic']['P']:.5f}")
    print(f"  COP: {vals['stochastic']['COP']:.3f}")
    print(f"  Episode Return: {vals['stochastic']['return']:.2f}")

    print("Deterministic:")
    print(f"  Q [kWh/m²]: {vals['deterministic']['Q']:.5f}")
    print(f"  P [kWh/m²]: {vals['deterministic']['P']:.5f}")
    print(f"  COP: {vals['deterministic']['COP']:.3f}")
    print(f"  Episode Return: {vals['deterministic']['return']:.2f}")

    # Plot Aktionen
    action_det = vals['deterministic']['actions'].apply(lambda x: x[0])
    action_stoch = vals['stochastic']['actions'].apply(lambda x: x[0])
    action_stoch_smooth = action_stoch.rolling(window=window, min_periods=1, center=False).mean()  # sliding mean of stochastic values

    #plt.figure(figsize=(10,4))
    plt.plot(action_stoch, label='Stochastisch (Gaussian head)', color='red', linewidth=0.2)
    plt.plot(action_stoch_smooth, label='Stochastisch (gleitender Mittelwert)', color='red', linestyle='-', linewidth=1)
    plt.plot(action_det, label='Deterministisch', color='blue', linewidth=1)
    #plt.fill_between(range(len(action_stoch)), action_stoch, action_det, color='orange', alpha=0.3, label='Deviation')
    plt.xlabel('Zeitschritt')
    plt.ylabel('Aktion [ ]')
    plt.title(f'Aktionen: Deterministische vs. stochastische Aktionen (inkl. gleitendem Mittelwert) für Agent {os.path.basename(agent_path)}')
    plt.legend()
    plt.tight_layout()
    plt.show()
