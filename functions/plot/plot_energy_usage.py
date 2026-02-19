from functions.helper.mat_reader import *
from functions.helper.training_helper_functions import *
import matplotlib.pyplot as plt
from functions.helper.calculate_energy import *
import numpy as np


def plot_energy_usage(config, results):
    # === Import heatpump tables and interpolate ===
    WP_tableP_ele = mat_reader_wp('fmu/WP_tableP_ele.mat')
    WP_tableP_ele = create_wp_interpolator(WP_tableP_ele)

    WP_tableQdot_con = mat_reader_wp('fmu/WP_tableQdot_con.mat')
    WP_tableQdot_con = create_wp_interpolator(WP_tableQdot_con)

    sim_step_size = config.sim_step_size  # [s]
    floor_area = 72  # [m²]

    # === Energy calculation ===
    for _name, _data in results.items():
        T_sou_WP = _data['results']['T_sou_WP'] - 273.15
        T_VL_WP = _data['results']['T_VL_WP'] - 273.15
        nSet_WP = _data['results']['nSet_WP']

        Q_use, P_use = calculate_energy(
            sim_step_size,
            T_VL_WP,
            T_sou_WP,
            nSet_WP,
            WP_tableQdot_con,
            WP_tableP_ele
        )

        Q_use_sum = np.sum(Q_use) / floor_area
        P_use_sum = np.sum(P_use) / floor_area
        COP = Q_use_sum / P_use_sum

        results[_name]['Q_use_sum'] = Q_use_sum
        results[_name]['P_use_sum'] = P_use_sum
        results[_name]['COP'] = COP

    # === FINAL VALUES ===
    agent_names = list(results.keys())
    n_series = len(agent_names)

    width = 0.8 / n_series
    BAR_ALPHA = 0.4
    PERCENT_OFFSET = 0.05

    energies = {
        name: [results[name]['Q_use_sum'], results[name]['P_use_sum']]
        for name in agent_names
    }
    cops = {name: results[name]['COP'] for name in agent_names}

    labels_energy = ['Thermisch', 'Elektrisch']
    labels_cop = ['COP']

    x_energy = np.arange(len(labels_energy))
    x_cop = x_energy[-1] + np.arange(1, len(labels_cop) + 1)
    offsets = (np.arange(n_series) - (n_series - 1) / 2) * width

    fig, ax = plt.subplots(figsize=(9, 5))
    ax2 = ax.twinx()

    # === Reference series ===
    ref_name = agent_names[0]
    ref_energy = energies[ref_name]
    ref_cop = cops[ref_name]

    # === Set axis limits BEFORE annotations ===
    max_energy_val = max(max(v) for v in energies.values())
    ax.set_ylim(0, max_energy_val * 1.2)

    max_cop_val = max(cops.values())
    ax2.set_ylim(0, max_cop_val * 1.2)

    energy_offset = PERCENT_OFFSET * ax.get_ylim()[1]
    cop_offset = PERCENT_OFFSET * ax2.get_ylim()[1]

    # === ENERGY bars ===
    for idx, name in enumerate(agent_names):
        y_vals = energies[name]

        ax.bar(
            x_energy + offsets[idx],
            y_vals,
            width,
            label=name,
            color=results[name]['color'],
            alpha=BAR_ALPHA
        )

        for i in range(len(labels_energy)):
            # Absolute value
            ax.text(
                x_energy[i] + offsets[idx],
                y_vals[i],
                f'{y_vals[i]:.2f}',
                ha='center',
                va='bottom',
                fontsize=8
            )

            # Percentage relative to reference
            if name != ref_name:
                pct = 100 * (y_vals[i] - ref_energy[i]) / ref_energy[i]

                ax.text(
                    x_energy[i] + offsets[idx],
                    y_vals[i] + energy_offset,
                    f'{pct:+.1f}%',
                    ha='center',
                    fontsize=8,
                    color=('green' if pct < 0 else 'red'),
                    fontweight='bold'
                )

    # === COP bars (identical placement logic) ===
    for idx, name in enumerate(agent_names):
        value = cops[name]

        ax2.bar(
            x_cop + offsets[idx],
            [value],
            width,
            color=results[name]['color'],
            alpha=BAR_ALPHA
        )

        # Absolute COP
        ax2.text(
            x_cop + offsets[idx],
            value,
            f'{value:.2f}',
            ha='center',
            va='bottom',
            fontsize=8
        )

        # Percentage relative to reference
        if name != ref_name:
            pct = 100 * (value - ref_cop) / ref_cop

            ax2.text(
                x_cop + offsets[idx],
                value + cop_offset,
                f'{pct:+.1f}%',
                ha='center',
                fontsize=8,
                color=('green' if pct > 0 else 'red'),
                fontweight='bold'
            )

    # === Layout ===
    ax.set_ylabel('Normierter Energieverbrauch [kWh/m²]')
    ax2.set_ylabel('COP')

    ax.set_xticks(list(x_energy) + list(x_cop))
    ax.set_xticklabels(labels_energy + labels_cop)

    ax.legend(loc='upper center')
    ax.axvline(x=x_energy[-1] + 0.5, color='black', linewidth=1)

    plt.title('Vergleich: Normierter Energieverbrauch und COP')

    if len(agent_names) > 1:
        plt.figtext(
            0.5,
            -0.05,
            'Prozentuale Abweichungen werden jeweils zum ersten Balken der Kategorie angegeben',
            ha='center',
            fontsize=8
        )

    plt.tight_layout()
    plt.show()
