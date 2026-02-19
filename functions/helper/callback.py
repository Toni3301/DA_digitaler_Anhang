from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
import numpy as np
import os
from functions.fmu_scripts.generate_agent_results import *


class RewardLoggingCallback(BaseCallback):
    def __init__(self, verbose=0): 
        super().__init__(verbose)

        self.metrics_buffer = {
            "reward/energy_consumption_reward": [],
            "reward/thermal_discomfort_reward": [],
            "reward/thermal_discomfort_punishment": [],
            "reward/total": [],
            "fmu/T_room": [],
            "fmu/action": [],
            "curriculum/stufe": [],
            "curriculum/reward": [],
        }

    def _on_step(self) -> bool:
        # get info dict of last environment
        infos = self.locals["infos"]
        for info in infos:
            #if "energy_consumption_reward" in info:
            self.metrics_buffer["reward/energy_consumption_reward"].append(info["energy_consumption_reward"])
            self.metrics_buffer["reward/thermal_discomfort_reward"].append(info["thermal_discomfort_reward"])
            self.metrics_buffer["reward/thermal_discomfort_punishment"].append(info["thermal_discomfort_punishment"])
            self.metrics_buffer["reward/total"].append(info["reward_total"])
            self.metrics_buffer["fmu/T_room"].append(info["T_room"])
            self.metrics_buffer["fmu/action"].append(info["action"])
            self.metrics_buffer["curriculum/stufe"].append(info["curriculum_stufe"])
            if "curriculum_reward" in info:
                self.metrics_buffer["curriculum/reward"].append(info["curriculum_reward"])

            if "episode" in info:
                self._on_episode_end()

        return True
    
    def _on_episode_end(self):
        for key, values in self.metrics_buffer.items():
            if len(values) > 0:
                mean_val = float(np.mean(values))

                if key != "curriculum/stufe":
                    self.logger.record(f"{key}_mean", mean_val)
                else:
                    self.logger.record(key, mean_val)

                self.metrics_buffer[key].clear() 
        
        self.logger.dump(step=self.num_timesteps)
        

class CurriculumEvalCallback(EvalCallback):
    """EvalCallback, that also adjusts curriculum after every eval"""

    def __init__(self, curriculum, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.curriculum = curriculum

    def _on_step(self) -> bool:
        if self.curriculum.max_difficulty_level > 0:
            self.n_eval_episodes = 2
        else:
            self.n_eval_episodes = 1
    
        result = super()._on_step()

        if self.n_calls % self.eval_freq == 0:
            mean_reward = self.last_mean_reward
            self.curriculum.total_steps = self.num_timesteps
            self.curriculum.adjust_difficulty(mean_reward)

        return result
    