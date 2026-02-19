import csv
import pandas as pd

# Dateipfade
input_file = "/home/toni/development/diplomarbeit/code/weather/Formatvorlage_weatherfile.csv"
output_file_experiment = "/home/toni/development/diplomarbeit/code/weather/experiment_weather_wp_check_0degC.csv"
output_file_dymola = "/home/toni/development/diplomarbeit/code/weather/dymola_weather_wp_check_0degC.mos"

'''experiment file'''
data = []
with open(input_file, mode='r') as infile:
    reader = csv.reader(infile)
    next(reader)  # skip header
    for row in reader:
        if row:  # skip empty rows
            try:
                # extract timestamp
                time_seconds = row[0]
                data.append(time_seconds)
            except IndexError:
                print(f"Fehler beim Verarbeiten der Zeile: {row}")

with open(output_file_experiment, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    writer.writerow(["time", "temp_soll", "feuchte_soll", "temp_regelung", "feuchte_regelung", "profil_wetter"])  # header

    for time_seconds in data:
        writer.writerow([time_seconds, '0.0', '25.0', "True", "True", "winter"])


'''dymola file'''
'''one_day_of_weather = pd.read_csv('/home/toni/development/diplomarbeit/code/weather/1_day_of_fall.mos', comment='#', header=None, sep="\t")
one_day_of_weather.iloc[:, 0] = one_day_of_weather.iloc[:, 0].astype(int)  # convert str to int

experiment_weather_dp = pd.DataFrame()  # initialize empty df
# time	20.0	10.0	40	100000	0	0	0	0	0	0	0	0	0	0	210	7.2	10	10	11.3	1160	9	999999999	130	0.1740	0	88	999.000	999.0	99.0
standard_hour = pd.DataFrame(0, 0.0, 10.0, 25, 100000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 210, 7.2, 10, 10, 11.3, 1160, 9, 999999999, 130, 0.1740, 0, 88, 999.000, 999.0, 99.0)
for i in range(365*24):
    hour = standard_hour
    hour[0] = i * 60*60
    experiment_weather_dp = pd.concat(experiment_weather_dp, hour)

experiment_weather_dp.to_csv('365_days_of_winter.mos', index=False, header=False, sep="\t")  # write the new data to a .mos file
'''