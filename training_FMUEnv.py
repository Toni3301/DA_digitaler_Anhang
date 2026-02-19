import os
import time
import numpy as np
from fmpy import read_model_description
from fmugym import FMUGym
import gymnasium as gym

from functions.helper.training_helper_functions import *
from functions.fmu_scripts.get_steady_state import *
from functions.fmu_scripts.set_conditions import *
from functions.helper.mat_reader import *
from functions.helper.calculate_energy import *
from functions.fmu_scripts.sample_initial_conditions import *
from functions.functions.heatcurves import *


os.environ["DYMOLA_RUNTIME_MESSAGES"] = "0"  # silence unnecessary dymola warnings


class FMUEnv(FMUGym):
    def __init__(self, config):
        with suppress_fmu_output_context():
            super().__init__(config)

        self.fallback_initial_conditions = get_steady_state(self.fmu_path, 'B_EG.T_room', use_preexisting_data=True)
        self.T_outside = None
        self.model_description = read_model_description(self.fmu_path)
        self.vrs = {variable.name: variable.valueReference for variable in self.model_description.modelVariables}
        self.config = config

        # finding indices
        self.T_room_idx = list(self.observation.keys()).index('T_room')
        self.T_VL_Gebaeude_idx = list(self.observation.keys()).index('T_VL_Gebaeude')
        self.T_sou_WP_idx = list(self.observation.keys()).index('T_sou_WP')
        self.T_VL_WP_idx = list(self.observation.keys()).index('T_VL_WP')
        self.T_RL_WP_idx = list(self.observation.keys()).index('T_RL_WP')
        self.m_flow_idx = list(self.observation.keys()).index('wP.port_a1.m_flow')
        self.nSet_WP_idx = list(self.observation.keys()).index('nSet_WP')
        self.wall_1_idx = list(self.observation.keys()).index('B_EG.surf_surBou[1].T')
        self.wall_2_idx = list(self.observation.keys()).index('B_EG.surf_conBou[1].T')
        self.wall_3_idx = list(self.observation.keys()).index('B_EG.surf_conBou[2].T')

        # reading wp tables
        self.WP_tableP_ele = mat_reader_wp('fmu/WP_tableP_ele.mat')
        self.WP_tableP_ele = create_wp_interpolator(self.WP_tableP_ele)
        self.WP_tableQdot_con = mat_reader_wp('fmu/WP_tableQdot_con.mat')
        self.WP_tableQdot_con = create_wp_interpolator(self.WP_tableQdot_con)

        self._external_episode_params = None


    '''##### initialization #####'''
    def set_initial_conditions(self):
        # get useful initial conditions
        if self.T_outside is None:
            self.initial_conditions = self.fallback_initial_conditions
        else:
            self.initial_conditions = sample_initial_conditions(fmu_filepath=self.fmu_path, T_outside=self.T_outside, verbose=True)

        set_conditions(self.initial_conditions, self.fmu, self.vrs, self.model_description)  # initialize fmu in steady state 
        set_conditions({'agent_control_setting': True}, self.fmu, self.vrs)  # activate agent control

    def _noisy_init(self):  # random variations to initial system states and dynamic parameters by sampling from self.random_vars_refs 
        # add noise to setpoint goals
        for ye in self.y_stop:
            self.y_stop[ye] = self.y_stop_range[ye].sample()[0]
        
        # add noise to initial system state
        init_states = {}
        for var in self.random_vars_refs:
            var_ref = self.random_vars_refs[var][0]
            uniform_value = self.random_vars_refs[var][1].sample()[0]
            init_states[var_ref] = uniform_value

            # domain randomization with noisy initial y_start
            if var in self.rand_starts.keys():
                input_string = self.rand_starts[var]
                self.y_start[input_string] = float(uniform_value)
        
        return init_states



    '''##### helper functions #####'''
    def _get_info(self):  # used by step() and reset(), returns any relevant debugging information.
        return {'info_time':time.time()}
    
    def _get_terminated(self):  # returns two booleans indicating first the termination and second truncation status. 
        '''Termination: Regular end of episode is reached
        Truncation: Episode was stopped because of too big errors'''
        
        if self.time > self.stop_time:
            return True, False
    
        for termination in self.terminations:
            min_value = self.terminations[termination].low[0]
            max_value = self.terminations[termination].high[0]

            if self.observation[termination] < min_value or self.observation[termination] > max_value:
                print("[Info] truncated")
                return False, True
                    
        return False, False
    


    '''##### essentials #####'''
    def step(self, *args, **kwargs):
        obs, reward, terminated, truncated, info = super().step(*args, **kwargs)

        # heatcurve control
        T_outside = obs['observation'][self.T_sou_WP_idx] - 273.15
        WP_T_VL = heatcurve_boi(T_outside)
        set_conditions({'WP_T_VL': WP_T_VL}, self.fmu, self.vrs)

        return obs, reward, terminated, truncated, info


    def reset(self, *args, **kwargs):  # resets fmu
        if self._external_episode_params is not None:  # prioritize external eval params
            self.curriculum_params = self._external_episode_params
            self._external_episode_params = None  # only use them for one episode

        else:  # get curriculum eval params if no external eval params were defined
            self.curriculum_params = self.curriculum.get_episode_params(verbose=True)
        
        self.config.start_time = self.curriculum_params["start_time"]
        self.config.stop_time = self.curriculum_params["stop_time"]

        with suppress_fmu_output_context():
            super().__init__(self.config)
            obs, info = super().reset(*args, **kwargs)

            # set fitting initial conditions for T_outside
            self.T_outside = obs['observation'][self.T_sou_WP_idx] - 273.15
            self.set_initial_conditions()
        
        return obs, info



    '''##### action #####'''    
    def _get_input_noise(self):  # returns input noise for each input component
        input_noise = []
        for inp_name in self.input_dict:
            input_noise.append(self.input_noise[inp_name].sample()[0])
        return np.array(input_noise)
    
    def _create_action_space(self, inputs):  # Define the action space
        action_space = gym.spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)  # [-1, 1], necessary for PPO
        return action_space
    
    def _process_action(self, action):  # scale and add noise to action
        # scaling
        #low, high = 20, 90
        low, high = 20, 45
        scaled = low + (action[0] + 1) * (high - low) / 2
        processed_action = np.array([scaled], dtype=np.float32)

        # noise
        noisy_action = processed_action + self._get_input_noise()

        self.fmu.setReal([self.vrs['agent_T_VL']], [noisy_action])

        return noisy_action
    



    '''##### observation #####'''
    def _get_output_noise(self):
        '''returns additive gaussian output noise'''

        output_noise = []

        for out_name in self.unwrapped.output_dict:
            sigma = 0.0  # default

            # get sigma values
            low = self.output_noise[out_name].low
            high = self.output_noise[out_name].high
            sigma = max(abs(low), abs(high))

            single_noise = np.random.normal(loc=0.0, scale=sigma)[0]  # sample gaussian noise

            # systematic sensor bias
            if out_name == 'T_RL_WP':
                single_noise += 0.15

            output_noise.append(single_noise)

        # curriculum switch: disable noise entirely
        corruption_active = self.curriculum_params.get('corruption_state', False)
        if not corruption_active:
            output_noise = np.zeros(len(output_noise))

        return np.array(output_noise)

    def _create_observation_space(self, outputs):  # returns observation space, 
        lows = []
        highs = []
        for out in outputs:
            lows.append(outputs[out].low[0])
            highs.append(outputs[out].high[0])
        observation_space = gym.spaces.Dict({
            'observation': gym.spaces.Box(low=np.array(lows), high=np.array(highs), dtype=np.float32),
            'achieved_goal': gym.spaces.Box(low=np.array(lows), high=np.array(highs), dtype=np.float32),
            'desired_goal': gym.spaces.Box(low=np.array(lows), high=np.array(highs), dtype=np.float32)
        })

        return observation_space

    def _get_obs(self):  # returns current output values of the fmu, adds noise to it
        self._get_fmu_output()
        obs = np.array([self.unwrapped.observation[out] for out in self.unwrapped.output_dict.keys()], dtype=np.float32).reshape(self.observation_space["achieved_goal"].shape)
        noisy_observation = obs + self._get_output_noise()
        self.setpoint = self.setpoint_trajectory(self.y_start, self.y_stop, self.time)

        desired_goal = np.zeros(len(noisy_observation), dtype=np.float32)
        desired_goal[self.T_room_idx] = float(self.setpoint)

        return {
            "observation": noisy_observation,
            "achieved_goal": noisy_observation,
            "desired_goal": desired_goal,
        }
    
    def setpoint_trajectory(self, y_start, y_stop, time):
        return np.array([y_start['T_room']] * len(y_start))  # constant goal for B_EG.T_room
    


    '''##### reward #####'''
    def _process_reward(self, obs, acts, info):  # interface between step and compute_reward
        # log action
        current_action = acts.copy() if isinstance(acts, np.ndarray) else acts
        info['action'] = current_action[0]

        achieved_goal = obs["achieved_goal"]
        desired_goal = obs["desired_goal"]
        reward = self.compute_reward(achieved_goal, desired_goal, info)

        return reward
        

    def compute_reward(self, achieved_goal, desired_goal, info):
        ele_weight = 100
        tdis_weight = 10
        tdis_punishment = 0 # -0.1

        # observation values
        T_room = achieved_goal[self.T_room_idx] - 273.15
        T_room_set = desired_goal[self.T_room_idx] - 273.15
        T_sou_WP = achieved_goal[self.T_sou_WP_idx] - 273.15
        T_VL_WP = achieved_goal[self.T_VL_WP_idx] - 273.15
        nSet_WP = achieved_goal[self.nSet_WP_idx]

        '''#### BOPTEST variables ####'''
        '''electrical energy consumption'''
        _, energy_consumption = calculate_energy(self.config.sim_step_size, T_VL_WP, T_sou_WP, nSet_WP, self.WP_tableQdot_con, self.WP_tableP_ele)  # [kWh]
        ele_reward = - ele_weight * energy_consumption

        '''thermal discomfort'''
        tdis_error = np.abs(T_room - T_room_set)  # [K]
        tdis_reward = - tdis_weight * tdis_error
        tdis_reward = float(tdis_reward)
        if tdis_error <= 1.5: tdis_punishment = 0  # comfort zone

        '''#### reward ####'''
        reward = ele_reward + tdis_reward + tdis_punishment
        
        # logging into info dict
        log_dict = {
            "energy_consumption_reward": ele_reward,
            "thermal_discomfort_reward": tdis_reward,
            "thermal_discomfort_punishment": tdis_punishment,
            "reward_total": reward,
            "T_room": achieved_goal[self.T_room_idx] - 273.15,
            "T_VL_Gebaeude": achieved_goal[self.T_VL_Gebaeude_idx],
            "curriculum_stufe": self.curriculum.difficulty_level,
        }

        if hasattr(self.curriculum, "mean_reward"): 
            log_dict["curriculum_reward"] = self.curriculum.mean_reward
        
        info.update(log_dict)

        return np.array([reward], dtype=np.float32)
    