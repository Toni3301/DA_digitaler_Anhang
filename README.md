# Digitaler Anhang zur Diplomarbeit

Enthalten: Digitale Dateien der Diplomarbeit „Training von Reinforcement Learning Agenten zur Regelung eines Gebäudeenergiesystems“
Autorin: Antonia Johanna Beatrice Spall

---

## Nutzungshinweise

1. **Python-Umgebung vorbereiten**  
   Installiere alle benötigten Pakete laut `pyproject.toml`:
   ```bash
   poetry install
2. **Agenten laden und evaluieren**  
    Die .zip Dateien in agents/ enthalten trainierte Modelle.
    Diese können mit dem Skript analysis/compare_agents.py geladen, ausgeführt und verglichen werden.
3. **Agenten trainieren**  
    Das Training wird mittels training_main.py gesteuert.
    Die korrekte Einstellung der gewünschten Parameter und Flags ist zu beachten.

---

## Ordnerstruktur
├── agents
│ ├── agent_on_curriculum_steps
│ └── other_agents_and_tests
├── analysis
│ ├── compare_agents.py
│ ├── compare_fmus
│ ├── experiments
│ ├── pressure_drop
│ ├── weather
│ └── wp_test.py
├── fmu
├── functions
│ ├── HiL
│ ├── fmu_scripts
│ ├── functions
│ ├── helper
│ └── plot
├── training_FMUEnv.py
└── training_main.py

- **agents/**  
  Enthält alle trainierten Reinforcement-Learning-Agenten, ihre Checkpoints und Trainingslogs.  
  - `agent_on_curriculum_steps` → Agenten für die Trainingsstufen des Curriculum-Learnings  
  - `other_agents_and_tests` → weitere Trainingsläufe, Vergleichsagenten und experimentelle Checkpoints

- **analysis/**  
  Skripte zur Analyse und Auswertung der Agenten und FMUs, inklusive:  
  - `compare_agents.py` → Vergleich mehrerer gespeicherter Agenten; wird zum Erzeugen wichtiger Auswerte-Plots verwendet  
  - `compare_fmus/` → Vergleich mehrerer exportierter FMUs; dient zur Einstellung von Parametern  
  - `experiments/` → experimentell ermittelte Werte und Tools zur Auswertung:  
    - `2024-06-14_Shango_EMS-Parameter_List.xlsx` und `Translator_HIL.csv` → Entschlüsselung der Sensornamen des Versuchsstands  
    - Feather-Dateien und `Vdot_Ablesedaten.csv` → Ergebnisdateien der Experimente  
    - `examine_corruption.py` → Ermittlung der Schwankung einer einzelnen Größe  
    - Weitere Skripte → Plotten einzelner oder mehrerer Werte aus den Ergebnisfiles  
  - `pressure_drop/` → Daten und Auswertung der Druckverlustmessung  
  - `weather/` → Wetterdateien und Skripte zur Erzeugung dieser  
        `DEU_Berlin.103840_IWEC.mos` → verwendetes Wetterfile für die Simulation
  - `wp_test.py` → Skript zum Plotten der Wärmepumpen-Leistungsdaten  
  - `gaussian_head.py` → Ermitteln des Gaussian Heads von fertigen Agenten  
  - `hp_tables.py` → Skalieren der Wärmepumpen-Tabellen für Dymola  
  - `tanh_activation_function.py` → Darstellung der Aktivierungsfunktion eines Neurons  
  - `test_variable.py` → Test verschiedener Werte für einen Parameter in der FMU

- **fmu/**  
  - `dymola.mat` → Ergebnisse der Simulation in Dymola  
  - `simmodell.fmu` → verwendete FMU  
  - `simmodell.png` → Bild der FMU  
  - `WP_tableP_ele.mat` → Leistungstabelle der Wärmepumpe, elektrische Leistung (P_ele)  
  - `WP_tableQdot_con.mat` → Leistungstabelle der Wärmepumpe, thermische Leistung (Qdot)

- **functions/**  
  Hilfsfunktionen für Training, Datenaufbereitung und Visualisierung  
  Unterordner:  
  - `fmu_scripts/` → Skripte für FMU-Tests und Trainingsumgebung:  
    - `fmu_test.py` → Vergleich der Ergebnisse der FMU mit denen aus Dymola; Untersuchung des Einschwingvorgangs  
    - `generate_agent_results.py` → Generieren von Ergebnissen eines gespeicherten Agenten mit vorgegebenen Parametern  
    - `generate_baseline_results.py` → Generieren von Vergleichsergebnissen mit der Heizkurve, mit vorgegebenen Parametern  
    - `get_jump_response.py` → Untersuchung der Sprungantwort verschiedener Variablen  
    - `get_steady_state.py` → Simulation bis zum Steady State, Speichern/Laden der Ergebnisse  
    - `sample_initial_conditions.py` → Auswahl passender Startwerte für die jeweilige Außentemperatur zu Beginn der Episode  
    - `set_conditions.py` → Weitergabe von Variablen an die FMU  
    - `training_eval.py` → manuelle Berechnung des Returns einer Episode als Vergleichswert zu den intern berechneten Werten  
  - `functions/` → allgemeine Funktionen:  
    - `heatcurves.py` → hinterlegte Heizkurven des Versuchsstands  
    - `jump_function.py` → Sprungfunktion  
  - `helper/` → allgemeine Hilfsfunktionen:  
    - `calculate_energy.py` → Berechnung des momentanen Energieverbrauchs der Wärmepumpe anhand der vorhandenen Simulationsparameter  
    - `callback.py` → Callback für den Trainingsprozess  
    - `curriculum_manager.py` → implementierte Logik des Curriculums  
    - `mat_reader.py` → Einlesen von `.mat`-Dateien aus Dymola-Ergebnisfiles  
    - `plot_helper.py` → ausgelagerte Funktionen zur Unterstützung beim Plotten  
    - `result_save_load.py` → Speichern/Laden der Ergebnisse für einzelne Agenten  
    - `training_helper_functions.py` → ausgelagerte Funktionen zur Unterstützung beim Training  
    - `weather_randomization.py` → Auswahl des Wetters für eine Episode  
  - `HiL/` → Funktionen für Hardware-in-the-Loop:  
    - `hil_connector.py` → Generieren der Agentenaktion für den Einsatz auf dem Prüfstand  
    - `twv_pid.py` → PID-Regler, der die Agentenaktion in ein Stellsignal für das Dreiwegeventil umwandelt  
  - `plot/` → Visualisierungsskripte:  
    - Verschiedene Plot-Skripte, verwenden jeweils vorab generierte Ergebnisse (siehe `compare_agents.py`)

- **training_FMUEnv.py** & **training_main.py**  
  Hauptskripte für Training und Evaluation der RL-Agenten

---

## Weitere Hinweise

- Logs (`events.out.tfevents.*`) stammen aus TensorBoard-Trainingsläufen. 
    Diese können mit dem Befehl `poetry run tensorboard --logdir agents/logs` ausgewertet werden
- Dateien in `__pycache__` sind kompilierte Python-Module, können ignoriert werden  
- Die Ordnerstruktur sollte beibehalten werden, damit Skripte korrekt funktionieren
- Bei älteren Skripten können vor der fehlerfreien Ausführung Aktualisierungen nötig sein
