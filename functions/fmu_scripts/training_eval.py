from sb3_contrib import RecurrentPPO
from functions.helper.curriculum_manager import *
from training_FMUEnv import *
from fmugym import FMUGymConfig, VarSpace, State2Out, TargetValue

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
stop_time = 24*3600  # episode time [s], used for start of training and evaluation
total_timesteps = 6e4  # total learning timesteps
additional_timesteps = 1e5  # steps for further training of existing agent
setpoint_temperature = 21.5 + 273.15  # T_set_room
sim_step_size = 60
action_step_size = 60

curriculum_max_difficulty_level = 0
eval_freq = 5000  # steps between checkpoints

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

output_noise = VarSpace("output_noise")
output_noise.add_var_box('nSet_WP', 0.0, 0.0)
output_noise.add_var_box('T_sou_WP', 0.0, 0.0)
output_noise.add_var_box('T_VL_WP', 0.0, 0.0)
output_noise.add_var_box('T_VL_Gebaeude', 0.0, 0.0)
output_noise.add_var_box('T_RL_Gebaeude', 0.0, 0.0)
output_noise.add_var_box('T_room', 0.0, 0.0)

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

curriculum = CurriculumManager(
    episode_days=24*3600/(3600*24), 
    reward_threshold_increase=-4100,  # to be adjusted
    reward_threshold_decrease=-5000,  # to be adjusted
    mode='training',
    max_difficulty_level=0,
    )

# create environments
env = FMUEnv(config)
env.curriculum = curriculum

agent_path = 'temp/checkpoints/recurrent_ppo_agent_50000_steps.zip'
model = RecurrentPPO.load(agent_path, env=env, tensorboard_log='./agents/logs') 
# resetting the environment and setting random initial and target values
observation, info = env.reset()
# capturing trajectories here
obs_array = []
act_array = []
obs_array.append(observation["observation"])

episode_return = 0
num_steps = int((24*3600 - 0) / 60)
for _ in range(num_steps):
    action, _state = model.predict(observation, deterministic=True) 
    observation, reward, terminated, truncated, info = env.step(action)

    episode_return += reward

    if terminated or truncated:
        observation, info = env.reset()

print(agent_path)
print(episode_return[0])
