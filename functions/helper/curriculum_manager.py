import numpy as np
import random
from functions.helper.weather_randomization import *
from collections import deque

class CurriculumManager:
    def __init__(self, max_difficulty_level=10, episode_days=1,
                 steps_per_level=20000,
                 mode='training',
                 corrupted_variables=None):
        
        self.mode = mode
        self.episode_days = episode_days
        self.max_difficulty_level = max_difficulty_level
        self.difficulty_level = 0
        self.steps_per_level = steps_per_level
        self.total_steps = 0
        self.corrupted_variables = corrupted_variables


    def increase_difficulty(self):
        if self.difficulty_level == self.max_difficulty_level or self.difficulty_level == 7:
            print(f"[Curriculum] Maximale Schwierigkeit erreicht, Steigerung nicht möglich")

        else:
            self.difficulty_level += 1

            if self.difficulty_level == 1:
                print(f"[Curriculum] Schwierigkeit erhöht auf Level {self.difficulty_level}: Wettervariation eingeschaltet.")
            
            elif self.difficulty_level == 2:
                print(f"[Curriculum] Schwierigkeit erhöht auf Level {self.difficulty_level}: Corruption eingeschaltet.")
        


    def decrease_difficulty(self):
        if self.difficulty_level == 0:
            print(f"[Curriculum] Minimale Schwierigkeit erreicht, Senkung nicht möglich")

        else:
            self.difficulty_level -= 1

            if self.difficulty_level == 1:
                print(f"[Curriculum] Schwierigkeit verringert auf Level {self.difficulty_level}: Corruption ausgeschaltet.")
            
            elif self.difficulty_level == 2:
                print(f"[Curriculum] Schwierigkeit verringert auf Level {self.difficulty_level}: Corruption ausgeschaltet.")



    def adjust_difficulty(self, mean_reward):
        print(f'[Curriculum] Mean eval reward = {mean_reward}')
        self.mean_reward = mean_reward  # save for logging
        
        # check if necessary training steps are reached
        if self.total_steps >= self.steps_per_level * (self.difficulty_level + 1):
            print("[Curriculum] Trainingszeit auf aktuellem Level abgeschlossen.")
            self.increase_difficulty()

        else:
            print("[Curriculum] Trainingszeit auf aktuellem Level läuft...")


    def get_episode_params(self, verbose=False):
        """called by env.reset()"""
        # standard parameters
        start_time = 0
        stop_time = self.episode_days * 24*3600
        corruption_state = False


        if self.mode == 'evaluation':
            # weather
            if self.max_difficulty_level >= 1:
                start_time, stop_time = weather_randomization(self.episode_days, self.mode)

            # corruption
            if self.max_difficulty_level >= 2:
                corruption_state = True
            
            if verbose: print(f"[Curriculum] EVAL level={self.max_difficulty_level}, start_time={start_time/3600} h, stop_time={stop_time/3600} h, corruption_state={corruption_state}")
                
        else:          
            # weather
            if self.difficulty_level >= 1:
                start_time, stop_time = weather_randomization(self.episode_days, self.mode)

                # corruption
                if self.difficulty_level >= 2:
                    corruption_state = True

            if verbose: print(f"[Curriculum] level={self.difficulty_level}, start_time={start_time/3600} h, stop_time={stop_time/3600} h, corruption_state={corruption_state}")


        return {
            'episode_duration': self.episode_days * 24*3600,
            'start_time': start_time,
            'stop_time': stop_time,
            'corruption_state': corruption_state,
        }


if __name__ == '__main__':
    curriculum = CurriculumManager(max_difficulty_level=10, episode_days=1, steps_per_level=20000, mode='evaluation', corrupted_variables=['T_RL_WP'])
    eval_params = curriculum.get_episode_params()
    print(eval_params)
