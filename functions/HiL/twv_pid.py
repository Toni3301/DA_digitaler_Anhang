import matplotlib.pyplot as plt
from functions.functions.jump_function import jump_val

def pi_regler_generator(Kp=0.02, Ki=120, dt=60):
    integral = 0  # Initialwert des Integrals
    integral_max = 100  # Begrenzung des Integrals

    while True:
        # Empfang von Sollwert und Istwert
        setpoint, measurement = yield

        # Fehler berechnen
        error = setpoint - measurement

        # Integralanteil aktualisieren und begrenzen
        integral += error * dt
        integral = max(-integral_max, min(integral, integral_max))

        output = Kp * error + Ki * integral  # calculate output
        output = max(0, min(10, output))  # norm output

        yield output



if __name__ == '__main__':
    Kp = 0.02
    Ki = 120
    dt = 60

    # initialize generator
    pi_regler = pi_regler_generator(Kp, Ki, dt)
    next(pi_regler)

    # test
    measurement = 20.0
    measurement_vals = []
    output_vals = []
    time_vals = []
    setpoint_vals = []

    for time in range(1000):
        output = None
        setpoint = jump_val(time, 20, 35, jumptime=400)
        while output == None:
            output = pi_regler.send((setpoint, measurement))

        setpoint_vals.append(setpoint)
        output_vals.append(output)
        measurement_vals.append(measurement)
        time_vals.append(time)

        # Beispiel: Istwert für die nächste Iteration aktualisieren
        measurement += output * 0.05 - 0.01  # Simulierter Systemeffekt


    # Plot mit zwei Y-Achsen
    fig, ax1 = plt.subplots()

    # Linke Y-Achse: Messwerte
    ax1.set_xlabel('Zeit (s)')
    ax1.set_ylabel('Messwerte', color='tab:blue')
    ax1.plot(time_vals, measurement_vals, label='Messwerte', color='tab:blue', zorder=2)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.plot(time_vals, setpoint_vals, linestyle='--', color='tab:blue')

    # Rechte Y-Achse: Reglerausgang
    ax2 = ax1.twinx()
    ax2.set_ylabel('Reglerausgang', color='tab:orange')
    ax2.plot(time_vals, output_vals, label='Reglerausgang', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    # Grid und Anzeige
    fig.tight_layout()
    plt.title('Test PI Regler für HIL Versuch')
    plt.grid()
    plt.show()