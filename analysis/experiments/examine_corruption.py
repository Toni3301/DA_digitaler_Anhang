import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from functions.functions.heatcurves import *
from scipy.signal import savgol_filter


what_to_examine = 'Q_WP'
show_box = False

def read_data(filepath):
    # read in feather data
    df = pd.read_feather(filepath)
    df.date = pd.to_datetime(df.date)
    df = df[~df.date.duplicated(keep='first')]
    df = df.set_index('date').resample('1s').ffill()
    time_hours = (df.index - df.index[0]).total_seconds() / 3600

    return df, time_hours

if what_to_examine == 'climatechamber':  # climate chamber air temperature
    filepath = "analysis/experiments/2025-10-23-18_22_10-experiment_temperature_steps1.feather"
    df, time_hours = read_data(filepath)

    T_aussen_mess = df["climate chamber air temperature"]
    T_set_interp = df["climate chamber air temperature_setpoint"]
    x_mess = T_aussen_mess
    x_set = T_set_interp

    plt.plot(time_hours, T_aussen_mess, label='Ist', color='g')
    plt.plot(time_hours, T_set_interp, label='Soll', color='r')

    '''plt.title('Lufttemperatur in der Klimakammer, Stufenversuch, Detailansicht')
    plt.xlim(18.25, 20)
    plt.ylim(7.6, 10.4)
    show_box = False'''
    
    plt.title('Lufttemperatur in der Klimakammer, Stufenversuch')

    plt.xlabel('Zeit [h]')
    plt.ylabel('Temperatur [°C]')


elif what_to_examine == 'T_RL_Gebaeude':
    filepath = "analysis/experiments/20241213T115905Z-experiment_weather_wp_check_0degC.feather"
    df, time_hours = read_data(filepath)

    T_RL_WP = df["Condenser inlet temperature °C"]
    T_RL_WP_set = 20
    x_mess = T_RL_WP
    x_set = T_RL_WP_set

    plt.plot(time_hours, T_RL_WP, color='g', label='Ist', linewidth=0.8)
    plt.axhline(y=20, label='Soll', color='r', linestyle='--')

    plt.xlabel('Zeit [h]')
    plt.ylabel('Temperatur [°C]')
    plt.title("Messung: RL Temperatur Gebäude, Detailansicht")
    plt.xlim(10, 20)
    plt.ylim(16, 25.25)


elif what_to_examine == 'Q_WP':
    filepath = "analysis/experiments/20241213T115905Z-experiment_weather_wp_check_0degC.feather"
    df, time_hours = read_data(filepath)

    Q_WP = df['XLP12BQR01']
    Q_WP_set = 20
    x_mess = Q_WP
    x_set = Q_WP_set

    plt.plot(time_hours, Q_WP, color='g', label='Ist')
    plt.axhline(y=20, label='Soll', color='r', linestyle='--')

    plt.xlabel('Zeit [h]')
    plt.ylabel('Wärmemenge [kW]')
    plt.title("Messung: Eingebrachte Wärmemenge WEZ")
    #plt.xlim(10, 20)
    #plt.ylim(16, 25.25)


elif what_to_examine == 'T_VL_WP':
    #filepath = "analysis/experiments/20241213T115905Z-experiment_weather_wp_check_0degC.feather"
    filepath = 'analysis/experiments/20251113T155502Z-experiment_temperature_steps_wp_check.feather'

    # debug, alter versuch
    #filepath = 'analysis/experiments/20240709T134119Z-sollwerte_klimakammer_winter_herbst_herbst_sommer.feather'

    df, time_hours = read_data(filepath)

    #T_VL_WEZ = df['XLW10BTR01']
    T_VL_WEZ = df['XLP11BTR01']
    T_aussen_mess = df["climate chamber air temperature"]
    T_VL_WP_Set = []

    for value in T_aussen_mess: T_VL_WP_Set.append(heatcurve_boi(value))
    T_VL_WP_Set = np.array(T_VL_WP_Set)
    T_VL_WP_Set = savgol_filter(T_VL_WP_Set, window_length=10000, polyorder=2)

    x_mess = T_VL_WEZ
    x_set = T_VL_WP_Set

    plt.plot(time_hours, T_VL_WEZ, label='Ist', color='g')
    plt.plot(time_hours, x_set, label='Soll', color='r', linestyle='--')
    #plt.plot(time_hours, T_aussen_mess, label='Außentemperatur', color='orange')

    plt.xlabel('Zeit [h]')
    plt.ylabel('Temperatur [°C]')
    plt.title("Messung: VL Temperatur WP")

    #plt.xlim(16, 24)
    #plt.ylim(63, 50.5)



abweichung = x_mess - x_set
mittlere_abweichung = np.mean(np.abs(abweichung))
std_abweichung = np.std(abweichung)

plt.grid()
plt.legend()
plt.tight_layout()
textstr = '\n'.join((
    r'$\mathrm{Mittlere\ Abweichung:}\ %.2f\,°C$' % (mittlere_abweichung, ),
    r'$\mathrm{Standardabweichung:}\ %.2f\,°C$' % (std_abweichung, )
))
props = dict(boxstyle='round', facecolor='white', alpha=0.9)
if show_box: plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=10, verticalalignment='top', bbox=props)

plt.show()