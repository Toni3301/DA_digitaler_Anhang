import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from scipy.signal import savgol_filter

import os
import sys
if "__file__" not in globals():
    __file__ = os.path.abspath("functions/helper/calculate_energy.py")
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)
analysis_path = os.path.join(project_root, "analysis")
experiments_path = os.path.join(analysis_path, "experiments")
weather_path = os.path.join(analysis_path, "weather")

from functions.functions.heatcurves import *
from functions.fmu_scripts.get_steady_state import get_steady_state


experiment = 2
sim_comparison = False

if experiment == 'bosch':  # random Bosch experiment
    filepath = 'analysis/experiments/20241029T143206Z-sollwerte_klimakammer_winter_herbst_herbst_sommer.feather'
    df = pd.read_feather(filepath)

    # correct timestamps
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

    T_VL_WP = df['HYB_TempFlowHeatPump_X']
    T_weather = df['OutTemp']
    T_VL_WP_set = T_weather.apply(heatcurve_hp)
    df['T_VL_WP_set'] = T_VL_WP_set
    T_VL_Boi_set = T_weather.apply(heatcurve_boi)
    df['T_VL_Boi_set'] = T_VL_Boi_set

    plt.figure(figsize=(6, 4))  # plot size
    plt.plot(df.index, T_VL_WP_set, label='Soll WP', color='b')
    plt.plot(df.index, T_VL_Boi_set, label='Soll Boiler', color='r')
    plt.gca().xaxis.set_major_locator(HourLocator(interval=15))  # x axis interval [h]
    plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))  # format HH:MM
    plt.plot(df.index, T_VL_WP, label='Ist', color='green')

    plt.xlabel('Zeit')
    plt.ylabel('Vorlauftemperatur [°C]')
    plt.title('VL Temperatur der Wärmeerzeuger im Versuchsstand')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

elif experiment == 'climatechamber':
    filepath = '.experiments/20241213T115905Z-experiment_weather_wp_check_0degC.feather'
    df = pd.read_feather(filepath)

    df.index = df.index / 3600 # time [s] -> [h]

    T_aussen_mess = df['XLP00BTR03']
    T_aussen_set = np.zeros(len(T_aussen_mess))
    T_mean = T_aussen_mess.mean()

    plt.plot(df.index, T_aussen_mess, label='Ist', color='g')
    plt.plot(df.index, T_aussen_set, label='Soll', color='r')
    plt.axhline(T_mean, label='Mittlere Abweichung', linestyle='--', color='g')

    plt.xlabel('Zeit [h]')
    plt.ylabel('Temperatur [°C]')
    plt.title('Lufttemperatur in der Klimakammer')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

    print(f'Mittlere Abweichung vom Sollwert: {T_mean} °C')


else:  # my experiments
    fmu_filepath = "fmu/simmodell.fmu"
    if experiment == 1:
        filepath = 'analysis/experiments/20241204T171059Z-experiment_weather_wp_check.feather'
    elif experiment == 2:
        filepath = 'analysis/experiments/20241213T115905Z-experiment_weather_wp_check_0degC.feather'

    df = pd.read_feather(filepath)

    df.index = df.index / 3600 # time [s] -> [h]

    T_VL_WEZ = df['XLW10BTR01']
    T_aussen_mess = df["climate chamber air temperature"]
    T_VL_WP_Set = []

    for value in T_aussen_mess: T_VL_WP_Set.append(heatcurve_boi(value))
    T_VL_WP_Set = np.array(T_VL_WP_Set)
    T_VL_WP_Set = savgol_filter(T_VL_WP_Set, window_length=10000, polyorder=2)

    plt.plot(df.index, T_VL_WEZ, label='Ist', color='g')
    plt.plot(df.index, T_VL_WP_Set, label='Soll', color='r')

    if sim_comparison:
        output_var = 'WP_senT_VL.T'
        max_simtime = df.index[-1] * 3600
        tolerance = 5e-10
        conditions = {
                        # set the same VL temperature as in experiment
                        'WP_manual_control_setting': True, 
                        'WP_T_VL': 59,

                        # wp control PID
                        'CTRL_WP_k': 0.0001,  # townhouse: 0.0001
                        'CTRL_WP_Ti': 15,  # townhouse: 30
                        'CTRL_WP_Td': 1,  # townhouse: 1

                        # wp control hysteresis
                        'WP_dT_on': 1,  # lower limit
                        'WP_dT_off': -2,  # upper limit, negative -> above setpoint

                      }
        steady_state_values, output_values, time_values = get_steady_state(fmu_filepath, output_var=output_var, conditions=conditions, tolerance=tolerance, use_preexisting_data=False, plot=False, full_output=True, max_simtime=max_simtime)
        plt.plot(time_values, output_values, label='Simulation', color='blue')

    plt.xlim(left=14, right=20)
    plt.ylim(top=63, bottom=45)

    plt.xlabel('Zeit [h]')
    plt.ylabel('Vorlauftemperatur [°C]')
    plt.title('VL Temperatur der Wärmeerzeuger im Versuchsstand')
    plt.tight_layout()
    plt.legend()
    plt.grid()
    plt.show()
