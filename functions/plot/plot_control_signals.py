import matplotlib.pyplot as plt
from functions.helper.plot_helper import *

# for _name, _data in results.items():
# name = _name
# results = _data['results']
# color = _data['color']

def plot_control_signal_twv(results, plot_params):
    for _name, _data in results.items():
        agent_signal = _data['results']['CTRL_DWV.y']
        plt.plot(_data['results']['time_h'], agent_signal, label=_name, color=_data['color'])

    plt.title('Vergleich: Steuersignal Dreiwegeventil')
    plt.xlabel('Zeit [h]')
    plt.ylabel('Steuersignal [ ]')
    plt.figtext(0.2, -0.05, "0 --> kein Wasser fließt durch die Wärmepumpe\n"
                            "1 --> das gesamte Wasser fließt durch die Wärmepumpe",
                            wrap=True, ha='left', va='top', fontsize=9)
    
    annotate_plot(plot_params)

    plt.grid()
    plt.tight_layout()
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.show()


def plot_control_signal_wp(results, plot_params):
    for _name, _data in results.items():
        nSet_WP = _data['results']['nSet_WP']
        plt.plot(_data['results']['time_h'], nSet_WP, label=_name, color=_data['color'])
    
    annotate_plot(plot_params)
    
    plt.title('Vergleich: Steuersignal Wärmepumpe')
    plt.xlabel('Zeit [h]')
    plt.ylabel('Steuersignal [ ]')
    plt.grid()
    plt.tight_layout()
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.show()
    