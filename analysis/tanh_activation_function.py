import numpy as np
import matplotlib.pyplot as plt

# Wertebereich für die Eingabe (x)
x = np.linspace(-5, 5, 500)

# tanh-Aktivierungsfunktion
y = np.tanh(x)

# Diagramm erstellen
plt.figure(figsize=(8, 5))
plt.plot(x, y, label=r'$\tanh(x)$', color='red', linewidth=2)

# Hilfslinien und Achsenbeschriftungen
plt.axhline(0, color='gray', linewidth=1)
plt.axhline(1, color='gray', linestyle='--', linewidth=1)
plt.axhline(-1, color='gray', linestyle='--', linewidth=1)
plt.axvline(0, color='gray', linewidth=1)

# Beschriftungen und Titel
plt.title("tanh-Aktivierungsfunktion eines Neurons", fontsize=14)
plt.xlabel("Kumulierte Eingabe z", fontsize=12)
plt.ylabel("Ausgabe f(z)", fontsize=12)

# Legende und Gitter
#plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

# Diagramm anzeigen
plt.show()
