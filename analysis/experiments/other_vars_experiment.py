import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter


filepath = 'analysis/experiments/20241204T171059Z-experiment_weather_wp_check.feather'
df = pd.read_feather(filepath)

# correct timestamps
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
df['time_h'] = df.index / 3600

'''##### T_Gebaeude #####'''
T_VL_Gebaeude = df['XLW10BTR01']
T_RL_Gebaeude = df['XLW10BTR11']

plt.figure(figsize=(6, 4))  # plot size
plt.plot(df['time_h'], T_VL_Gebaeude, label='T_VL_Gebaeude', color='b')
plt.plot(df['time_h'], T_RL_Gebaeude, label='T_RL_Gebaeude', color='r')
plt.xlim(4, 8)
plt.ylim(58.5, 60.25)

plt.xlabel('Zeit [h]')
plt.ylabel('Temperatur [°C]')
plt.title('Messung: Temperaturen an der Schnittstelle im Versuchsstand')
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()

