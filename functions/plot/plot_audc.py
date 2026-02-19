import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from functions.fmu_scripts.generate_baseline_results import *


def plot_audc(agents, env, n_episodes=3, deterministic=True):
    """AUDC = (μ(0) + μ(1)) / (2 * μ(0))"""

    def evaluate(agent_path, corruption_state):
        env._external_episode_params = {
            "corruption_state": corruption_state,
            "start_time": 0,
            "stop_time": 24*3600,
        }

        model = PPO.load(agent_path)
        episode_rewards = []

        for _ in range(n_episodes):
            obs, info = env.reset()
            terminated = False
            truncated = False
            ep_reward = 0.0

            while not (terminated or truncated):
                action, _ = model.predict(obs, deterministic=deterministic)
                obs, reward, terminated, truncated, info = env.step(action)
                ep_reward += float(reward)

            episode_rewards.append(ep_reward)

        return float(np.mean(episode_rewards))
    
    def compute_mu_from_results(results, sim_step_size=60):
        ele_weight = 100
        tdis_weight = 10

        # thermal discomfort
        t_room = results["T_room"].values
        t_room_set = (21.5 + 273.15) * np.ones_like(t_room)
        tdis_error = np.abs(t_room - t_room_set)  # [K]
        tdis_reward = - tdis_weight * tdis_error

        # energy consumption
        Q_WP = results["Q_WP"].values  # [W]
        energy_kwh = Q_WP * sim_step_size / 3.6e6  # [kWh]
        ele_reward = -ele_weight * energy_kwh

        # total reward
        reward_total = ele_reward + tdis_reward

        return float(np.sum(reward_total))

    # calculate AUDC
    audc_values = {}
    mu_values = {}

    for name, cfg in agents.items():
        print(f"[AUDC] Evaluating {name}")

        if name in ['Heizkurve', 'Agent untrainiert']: 
            mu_0 = compute_mu_from_results(cfg['results_corruption_0'])
            mu_1 = compute_mu_from_results(cfg['results_corruption_1'])

        else:
            mu_0 = evaluate(cfg["path"], corruption_state=False)
            mu_1 = evaluate(cfg["path"], corruption_state=True)

        audc = (mu_0 + mu_1) / (2.0 * mu_0)

        audc_values[name] = audc
        mu_values[name] = {
            "mu_no_corruption": mu_0,
            "mu_corruption": mu_1
        }

    # plot
    names = list(audc_values.keys())
    values = np.array([audc_values[n] for n in names])
    colors = [agents[n]["color"] for n in names]
    x = np.arange(len(names))

    plt.figure(figsize=(6, 4))
    plt.scatter(x, values, color=colors, s=80, zorder=3, marker='x')
    for xi, yi in zip(x, values):
        plt.text(
            xi,
            yi+0.025,
            f"{yi:.2f}",
            ha="center",
            va="bottom",
            fontsize=9
        )
    plt.axhline(1.0, linestyle="--", linewidth=1)
    plt.xticks(x, names, rotation=20)
    plt.ylabel("AUDC_2P")
    plt.title("Vergleich: Zweipunkt-AUDC")
    plt.ylim(0, max(1.05, values.max() * 1.1))
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()

