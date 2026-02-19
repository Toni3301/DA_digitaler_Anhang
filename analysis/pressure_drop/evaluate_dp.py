import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from DyMat import DyMatFile

experiment = 2

# experiment 1
if experiment == 1:
    filepath = '/home/toni/development/diplomarbeit/code/pressure_drop/20241112T080823Z-pressuredrop.feather'
    time_open_start = '11:11:00'
    time_open_end = '12:10:00'
    time_closed_start = '10:07:00'
    time_closed_end = '11:05:00'

# experiment 2 ->
elif experiment == 2:
    filepath = '/home/toni/development/diplomarbeit/code/pressure_drop/20241118T092419Z-experiment_weather_dp_1.feather'
    time_open_start = '11:22:00'
    time_open_end = '13:12:00'
    time_closed_start = '13:20:00'
    time_closed_end = '15:20:00'

df = pd.read_feather(filepath)

# convert dates to datetime index
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# calculate time in hours from the start of the experiment
start_time = df.index[0]
df['time_hours'] = (df.index - start_time).total_seconds() / 3600



'''all the experimental data'''
'''p_RL = df['XLM12BPR01']  # p Sensor bei RL aus Gebäude
p_VL = df['XLM21BPR01']  # p Sensor bei VL in Gebäude
plt.plot(df['time_hours'], p_RL, label='p_RL', color='b')
plt.plot(df['time_hours'], p_VL, label='p_VL', color='r')
plt.legend()
plt.grid()
plt.xlabel('Versuchszeit [h]')
plt.ylabel('Druck [bar]')
plt.show()'''



'''valve fully closed (counterclockwise)'''
# experimental data
valve_closed = df.between_time(time_closed_start, time_closed_end).copy()
valve_closed_start_time = valve_closed.index[0]
valve_closed.loc[:, 'time_hours'] = (valve_closed.index - valve_closed_start_time).total_seconds() / 3600
p_RL = valve_closed['XLM12BPR01']
p_VL = valve_closed['XLM21BPR01']
dp = np.mean(p_VL) - np.mean(p_RL)
plt.text(1.1, 0.3, f"Δp = {dp:.2f} bar", transform=plt.gca().transAxes,
         fontsize=10, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

plt.plot(valve_closed['time_hours'], p_RL, label='p_RL Experiment', color='b')
plt.plot(valve_closed['time_hours'], p_VL, label='p_VL Experiment', color='r')
plt.plot(valve_closed['time_hours'], p_VL-p_RL, label='Δp Experiment', color='g')

# sim data
mat_file = DyMatFile('/home/toni/development/diplomarbeit/code/pressure_drop/twv_closed_dp.mat')
sim_p_VL = mat_file.data('VS_senRelPre.port_a.p')
sim_p_RL = mat_file.data('VS_senRelPre.port_b.p')

sim_p_VL = np.linspace(sim_p_VL[0], sim_p_VL[1], len(sim_p_RL))
sim_time = np.linspace(0, len(sim_p_RL) - 1, len(sim_p_RL)) / 3600

plt.plot(sim_time, sim_p_VL/100000, label='p_VL Simulation',  linestyle='--', color='r')
plt.plot(sim_time, sim_p_RL/100000, label='p_RL Simulation', linestyle='--', color='b')
plt.plot(sim_time, (sim_p_VL-sim_p_RL)/100000, label='Δp Simulation', linestyle='--', color='black')

plt.xlabel('Versuchszeit [h]')
plt.ylabel('Statischer Absolutdruck [bar]')
plt.title('Statischer Absolutdruck mit geschlossenem Dreiwegeventil')
plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5))
plt.xlim(left=0, right=6000/3600)
plt.ylim(bottom=0)
plt.grid()
plt.show()



'''valve fully opened (clockwise)'''
# experimental data
valve_opened = df.between_time(time_open_start, time_open_end).copy()
valve_opened_start_time = valve_opened.index[0]
valve_opened.loc[:, 'time_hours'] = (valve_opened.index - valve_opened_start_time).total_seconds() / 3600
p_RL = valve_opened['XLM12BPR01']
p_VL = valve_opened['XLM21BPR01']
dp = np.mean(p_VL) - np.mean(p_RL)
plt.text(1.1, 0.3, f"Δp = {dp:.2f} bar", transform=plt.gca().transAxes,
         fontsize=10, verticalalignment='top', horizontalalignment='left',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

plt.plot(valve_opened['time_hours'], p_RL, label='p_RL Experiment', color='b')
plt.plot(valve_opened['time_hours'], p_VL, label='p_VL Experiment', color='r')
plt.plot(valve_opened['time_hours'], p_VL-p_RL, label='Δp Experiment', color='g')

# sim data
mat_file = DyMatFile('/home/toni/development/diplomarbeit/code/pressure_drop/twv_open_dp.mat')
sim_p_VL = mat_file.data('VS_senRelPre.port_a.p')
sim_p_RL = mat_file.data('VS_senRelPre.port_b.p')

sim_p_VL = np.linspace(sim_p_VL[0], sim_p_VL[1], len(sim_p_RL))
sim_time = np.linspace(0, len(sim_p_RL) - 1, len(sim_p_RL)) / 3600

plt.plot(sim_time, sim_p_VL/100000, label='p_VL Simulation',  linestyle='--', color='r')
plt.plot(sim_time, sim_p_RL/100000, label='p_RL Simulation', linestyle='--', color='b')
plt.plot(sim_time, (sim_p_VL-sim_p_RL)/100000, label='Δp Simulation', linestyle='--', color='black')

plt.xlabel('Versuchszeit [h]')
plt.ylabel('Statischer Absolutdruck [bar]')
plt.title('Statischer Absolutdruck mit offenem Dreiwegeventil')
plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5))
plt.xlim(left=0, right=6000/3600)
plt.ylim(bottom=0)
plt.grid()
plt.show()