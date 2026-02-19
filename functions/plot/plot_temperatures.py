import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
import pandas as pd
from functions.helper.plot_helper import *

# for _name, _data in results.items():
# name = _name
# results = _data['results']
# color = _data['color']

def plot_outside_temperature(results, plot_params):
    for _name, _data in results.items():
        T_outside = _data['results']['B_weaDat.weaBus.TDryBul'] - 273.15  # [°C]
        plt.plot(_data['results']['time_h'], T_outside, label=_name, color=_data['color'])

    annotate_plot(plot_params)

    plt.title('Vergleich: Außentemperatur im Zeitverlauf')
    plt.xlabel('Zeit [h]')
    plt.ylabel('Temperatur [°C]')
    plt.legend()
    plt.tight_layout()
    plt.grid()
    plt.show()


def plot_air_temperatures(results, plot_params):
    T_set = 21.5  # [°C]
    for _name, _data in results.items():
        T_room = _data['results']['T_room'] - 273.15  # [°C]
        plt.plot(_data['results']['time_h'], T_room, label=_name, color=_data['color'])

    # T_set and comfort zone
    plt.axhline(T_set, color='green', linestyle='dotted', label="Raumtemperatur Soll")
    plt.axhline(T_set-1.5, color='green', linestyle='--', label="Komfortgrenzen Raumtemperatur")  
    plt.axhline(T_set+1.5, color='green', linestyle='--') 

    annotate_plot(plot_params)

    plt.title('Vergleich: Lufttemperatur')
    plt.xlabel('Zeit [h]')
    plt.ylabel('Temperatur [°C]')
    plt.grid()
    plt.tight_layout()
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.show()


def plot_T_VL_Gebaeude(results, plot_params):
    window = 50
    for _name, _data in results.items():
        measurement_raw = _data['results']['T_VL_Gebaeude'] - 273.15
        measurement_smooth = pd.Series(measurement_raw).rolling(window=window, center=True).mean()
        plt.plot(_data['results']['time_h'], measurement_smooth, label=_name + ' ist', color=_data['color'])
    
        if _name == 'Heizkurve': continue

        setpoint_raw = _data['results']['from_degC1.u']
        setpoint_smooth = pd.Series(setpoint_raw).rolling(window=window, center=True).mean()
        plt.plot(_data['results']['time_h'], setpoint_smooth, label=_name + ' soll', color=_data['color'], linestyle='--')
    
    annotate_plot(plot_params)

    plt.title('Vergleich: Vorlauftemperatur Gebäude')
    plt.xlabel('Zeit [h]')
    plt.ylabel('Temperatur [°C]')
    plt.grid()
    plt.tight_layout()
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.show()


def plot_thermal_discomfort_summenhaeufigkeit(results):
    T_set = 21.5  # [°C]
    plt.figure()
    
    for _name, _data in results.items():
        T_room = _data['results']['T_room'] - 273.15
        dT = T_room - T_set  # signed deviation from setpoint
        dT_sorted = np.sort(dT)  # sort values
        ECDF = np.arange(1, len(dT_sorted) + 1) / len(dT_sorted)  # cumulative relative frequency (ECDF)
        plt.step(dT_sorted, ECDF, where="post", label=_name, color=_data['color'])

    plt.axvline(0, linestyle="dotted", label="Raumtemperatur Soll", color='g')
    plt.axvline(-1.5, linestyle="--", label="Komfortgrenzen Raumtemperatur", color='g')
    plt.axvline(1.5, linestyle="--", color='g')

    plt.xlabel("Temperaturabweichung ΔT [K]")
    plt.ylabel("Summenhäufigkeit [ ]")
    plt.title('Vergleich: Summenhäufigkeit der Lufttemperatur')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
