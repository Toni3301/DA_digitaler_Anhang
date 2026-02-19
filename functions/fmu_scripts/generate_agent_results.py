import numpy as np
import pandas as pd
from functions.fmu_scripts.set_conditions import *
from functions.functions.heatcurves import *
from functions.fmu_scripts.sample_initial_conditions import *
from sb3_contrib import RecurrentPPO


def generate_agent_results(env, eval_level, model=None, policy_kwargs=None, log_data=True, 
                           agent_T_VL=None, eval_params=None, deterministic=True, days=None, 
                           SEED=None, corruption=False):
    lstm_states = None
    episode_starts = np.ones((1,), dtype=bool)
    daytime = 3600*24

    if model == None:
        # create untrained model
        model = RecurrentPPO(
            policy="MultiInputLstmPolicy",
            env=env,
            verbose=0,
            policy_kwargs=policy_kwargs
        )

    if log_data:
        data_dict = {
            "time_step": [],
            "time_h": [],
            "action": [],
            "CTRL_DWV.y": []
        }
        output_vars = list(env.unwrapped.output_dict.keys())
        for var in output_vars:
            data_dict[var] = []
            data_dict[f"{var}_set"] = []
    else:
        data_dict = None
        output_vars = list(env.unwrapped.output_dict.keys())
    episode_return = 0

    # set parameters
    env.curriculum.mode = 'evaluation'
    env.curriculum.eval_level = eval_level
    if eval_params == None:
        eval_params = env.curriculum.get_episode_params()

    if days == None:
        day_count = 1
        env._external_episode_params = eval_params

    else:  # custom eval days
        day_count = len(days)

    if corruption:
        env._external_episode_params = {
            "corruption_state": True,
            "start_time": 0,
            "stop_time": 24*3600,
        }

    
    # transform fixed action
    if agent_T_VL != None:
        agent_T_VL = 2 * (agent_T_VL - 20) / (90 - 20) - 1  # scale acording to action space
        agent_T_VL = np.array([agent_T_VL], dtype=np.float32)  # fit into data format


    # simulation loop
    total_steps = 0
    for i in range(day_count):
        lstm_states = None 
        episode_starts = np.ones((1,), dtype=bool)

        if days != None:  # custom eval days
            eval_params = {
                'start_time': days[i]*daytime, 
                'stop_time': days[i]*daytime + daytime,
                'episode_duration': daytime,
            }
            env._external_episode_params = eval_params
            
        num_steps = int((eval_params['stop_time'] - eval_params['start_time']) / env.config.sim_step_size)

        if SEED is not None:
            obs, _ = env.reset(seed=SEED)   
        else:
            obs, _ = env.reset()  

        set_conditions({'WP_manual_control_setting': True}, env.fmu, env.vrs)  # activate manual wp control


        for step in range(num_steps):
            batched_obs = {k: np.expand_dims(v, 0) for k, v in obs.items()}

            action_batch, lstm_states = model.predict(batched_obs,state=lstm_states,episode_start=episode_starts,deterministic=deterministic)
            action_single = action_batch[0]

            episode_starts = np.zeros((1,), dtype=bool)

            if agent_T_VL == None:
                # controlled by agent
                obs, reward, terminated, truncated, info = env.step(action_single)
            
            else:
                # fixed value
                obs, reward, terminated, truncated, info = env.step(agent_T_VL)
            
            done = terminated or truncated
            episode_return += reward

            if log_data:
                if days == None:
                    current_time_h = (total_steps * env.config.sim_step_size + eval_params['start_time']) / 3600.0
                else:
                    current_time_h = total_steps * env.config.sim_step_size / 3600.0

                # collect timestep info
                data_dict["time_step"].append(total_steps)
                data_dict["time_h"].append(current_time_h)
                data_dict["action"].append(action_single)

                # collect output data
                for idx, var in enumerate(output_vars):
                    data_dict[var].append(obs["observation"][idx])
                    data_dict[f"{var}_set"].append(obs["desired_goal"][idx])
            
            total_steps += 1

            if done:
                print(f"[DEBUG WARNING] Episode ended prematurely at step {step} with final reward {episode_return[0]:.4f}!")
                break

        
    env.curriculum.mode = 'training'
    
    agent_results = pd.DataFrame(data_dict) if log_data else None  # make dataframe
    episode_return = episode_return[0]

    return agent_results, eval_params, episode_return
