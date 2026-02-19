import numpy as np

def weather_randomization(episode_days, mode='training'):
    """
    Wählt Start- und Stoppzeitpunkte für Wetterdaten aus,
    sodass Training nur ungerade Tage und Evaluation nur gerade Tage verwendet.
    """

    weather_file_maxtime = 3.15324e7/3600/24  # standard length of any dymola weather file [d]
    daytime = 24*3600  # time in a day [s]

    # Erzeuge alle möglichen Starttage
    possible_days = np.arange(0, int(weather_file_maxtime - episode_days))

    # Filter: ungerade Tage für Training, gerade Tage für Evaluation
    if mode == 'training':
        day_candidates = possible_days[possible_days % 2 == 1]
    elif mode == 'evaluation':
        day_candidates = possible_days[possible_days % 2 == 0]
    else:
        raise ValueError("mode must be 'training' or 'evaluation'")

    start_day = np.random.choice(day_candidates)
    start_time = start_day * daytime
    stop_time = start_time + episode_days * daytime

    return start_time, stop_time  # [s]


if __name__ == '__main__':
    simtime_days = 2
    for mode in ['training', 'evaluation']:
        start_time, stop_time = weather_randomization(simtime_days, mode)
        print(f"\nMode: {mode}")
        print(f"start_time = {start_time/3600:.1f} h")
        print(f"stop_time = {stop_time/3600:.1f} h")
        print(f"sim_time = {(stop_time - start_time)/3600:.1f} h")
