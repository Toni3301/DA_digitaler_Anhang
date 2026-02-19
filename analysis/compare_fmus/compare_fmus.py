import DyMat
import matplotlib.pyplot as plt
import numpy as np

input_value = "Qp_HK_nom"
# input_value = "KS_thickness"

if input_value == "Qp_HK_nom":
    files = {
        "3240 W": "Qp_HK_nom_3240.mat",
        "4250 W": "Qp_HK_nom_4250.mat",
        "5760 W": "Qp_HK_nom_5760.mat",
    }
elif input_value == "KS_thickness":
    files = {
        "175 mm Kalksandstein": "N_KS_175.mat",
        "10 mm Kalksandstein": "N_KS_010.mat"
    }

for label, path in files.items():
    mat = DyMat.DyMatFile(path)
    vals = mat.data('B_EG.T_room') - 273.15
    time = mat.abscissa('B_EG.T_room', 0)[0] / 3600  # <-- hier [0]!
    mask = time <= 60
    plt.plot(time[mask], vals[mask], label=label)

plt.axhline(y=23, color='r', linestyle='--', linewidth=1, label='Zieltemperatur')
plt.legend()
plt.grid()
plt.xlabel('Zeit [h]')
plt.ylabel('Lufttemperatur im Raum [°C]')

if input_value == "Qp_HK_nom":
    plt.title('Entwicklung der Lufttemperatur im Raum bei \nverschiedenen nominalen Heizleistungen')
    plt.xlim(0, 5)

elif input_value == "KS_thickness":
    plt.title('Entwicklung der Lufttemperatur im Raum bei \nverschiedenen Wandzusammensetzungen')

plt.show()
