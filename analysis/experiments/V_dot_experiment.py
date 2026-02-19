import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file_path = "analysis/experiments/Vdot_Ablesedaten.csv"

df = pd.read_csv(file_path)
time_data = df['time']
flow_data = df['flow']
flow_mean = np.mean(flow_data)

plt.plot(time_data, flow_data, label='Messwerte', linewidth=1)
plt.axhline(flow_mean, color='r', linestyle='--', label='Mittelwert')

plt.xlabel('Zeit [s]')
plt.ylabel('Durchfluss [l/s]')
plt.title('Messwerte: Durchfluss Versuchsstand')
plt.ylim(0.180, 0.240)
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()
