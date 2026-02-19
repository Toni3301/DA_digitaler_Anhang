import csv
from datetime import datetime, timedelta


# Dateipfade
input_file = "weather/DEU_Berlin.103840_IWEC.mos"
output_file = "weather/DEU_Berlin.103840_IWEC_experiment.mos"

# Startdatum und -zeit für die Simulation
start_datetime = datetime(2024, 1, 1)

# Funktion zur Umwandlung von Sekunden seit Simulationsbeginn in das gewünschte Datum-Zeit-Format
def convert_time(seconds):
    return (start_datetime + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S")

# Funktion zur linearen Interpolation
def interpolate(start, end, steps):
    return [start + (end - start) * i / steps for i in range(steps + 1)]

# Daten aus der Eingabedatei einlesen
data = []
with open(input_file, mode='r') as infile:
    for line in infile:
        line = line.strip()
        
        # Kommentare überspringen
        if line.startswith("#"):
            continue

        # Zeile in Spalten aufteilen
        columns = line.split()
        try:
            # Zeit und Werte extrahieren
            time_seconds = float(columns[0])
            temp_soll = float(columns[1])
            feuchte_soll = float(columns[3])
            data.append((time_seconds, temp_soll, feuchte_soll))
        except (IndexError, ValueError):
            print(f"Fehler beim Verarbeiten der Zeile: {line}")

# CSV-Schreiben vorbereiten
with open(output_file, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # CSV-Header schreiben
    writer.writerow(["time", "temp_soll", "feuchte_soll", "temp_regelung", "feuchte_regelung", "profil_wetter"])

    # Interpolierte Daten erstellen
    for i in range(len(data) - 1):
        start_time, start_temp, start_humidity = data[i]
        end_time, end_temp, end_humidity = data[i + 1]
        
        # Interpolationsschritte berechnen
        steps = int((end_time - start_time) / 600)  # 600 Sekunden = 10 Minuten
        times = interpolate(start_time, end_time, steps)
        temps = interpolate(start_temp, end_temp, steps)
        humidities = interpolate(start_humidity, end_humidity, steps)
        
        # Interpolierte Werte in die CSV-Datei schreiben
        for t, temp, humidity in zip(times, temps, humidities):
            temp += 1.8  # Regelabweichung der Klimakammer ausgleichen
            time_str = convert_time(t)
            writer.writerow([time_str, f"{temp:.1f}", f"{humidity:.1f}", "True", "True", "winter"])
