import pandas as pd
from datetime import datetime, timedelta

# Parameter
start_time = datetime(2025, 1, 1, 0, 0, 0)
time_step = timedelta(minutes=10)
max_temp = 20
hours_to_reach_max = max_temp * 2  # 1 K alle 2 h → 20 K in 40 h
num_steps = int((hours_to_reach_max * 60) / 10) + 1  # 10-Minuten-Schritte

# DataFrame generieren
times = [start_time + i * time_step for i in range(num_steps)]
temp_soll = [float(min(i // 12, max_temp)) for i in range(num_steps)]  # alle 2h (+12 Schritte) +1K
feuchte_soll = [25.0] * num_steps
temp_regelung = ["True"] * num_steps
feuchte_regelung = ["True"] * num_steps
profil_wetter = ["winter"] * num_steps

df = pd.DataFrame({
    "time": times,
    "temp_soll": temp_soll,
    "feuchte_soll": feuchte_soll,
    "temp_regelung": temp_regelung,
    "feuchte_regelung": feuchte_regelung,
    "profil_wetter": profil_wetter
})

# CSV speichern
output_path = "weather/experiment_temperature_steps.csv"
df.to_csv(output_path, index=False)

print(f"CSV gespeichert als {output_path} mit {len(df)} Zeilen (Dauer: {(times[-1]-times[0])}).")
