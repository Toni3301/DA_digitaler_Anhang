## setup
import pandas as pd

'''Generate weather data
You need one .mos file that contains the weatherdata for a single day. This script generates a whole year with the same
weather over and over again. It's important to insert a header into the output file after the file has been generated.
It can be found in any of the other dymola weather files. Just copy all of the header into your file as it is. 
Don't worry about the location being incorrect as it doesn't influence the simulation'''

# import data of one day
one_day_of_weather = pd.read_csv('1_day_of_fall.mos', comment='#', header=None, sep="\t", on_bad_lines='skip')


# convert string to int
one_day_of_weather.iloc[:, 0] = one_day_of_weather.iloc[:, 0].astype(int)


## generate a whole year
# initialize new dataframe
one_year_of_weather = pd.DataFrame()

for i in range(365):
    temp_daten = one_day_of_weather.copy()
    # Direkte Berechnung für die gesamte Spalte
    temp_daten.iloc[:, 0] += i * 3600 * len(temp_daten) + 3600 * temp_daten.index

    one_year_of_weather = pd.concat([one_year_of_weather, temp_daten])

# write the new data to a .mos file
one_year_of_weather.to_csv('365_days_of_fall_dymola.mos', index=False, header=False, sep="\t")
