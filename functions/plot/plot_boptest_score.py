import matplotlib.pyplot as plt
import numpy as np

def plot_boptest_score(ele_tot_agent, ele_tot_baseline, pele_tot_agent, pele_tot_baseline, tdis_tot_agent, tdis_tot_baseline):
    '''##### calculate BOPTEST score #####'''
    boptest_score_agent = 0.3 * ele_tot_agent + 4.25 * pele_tot_agent + 0.005 * tdis_tot_agent
    boptest_score_baseline = 0.3 * ele_tot_baseline + 4.25 * pele_tot_baseline + 0.005 * tdis_tot_baseline
    boptest_score_agent = np.mean(boptest_score_agent)
    boptest_score_baseline = np.mean(boptest_score_baseline)

    '''##### plot #####'''
    labels = ["BOPTEST Score"]
    baseline_values = [boptest_score_baseline]
    agent_values = [boptest_score_agent]
    width = 0.35
    annotation_font_size = 10

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(6, 5))

    # Balken zeichnen
    bars1 = ax.bar(x - width/2, baseline_values, width, label="Baseline", color="lightcoral")
    bars2 = ax.bar(x + width/2, agent_values, width, label="Agent", color="skyblue")

    ax.set_ylabel("BOPTEST Score")

    # Skalierung für Annotationen
    max_val = max(baseline_values + agent_values)

    for i in range(len(labels)):
        h_base = baseline_values[i]
        h_agent = agent_values[i]

        # numerische Werte direkt über die Balken schreiben
        ax.text(x[i] - width/2, h_base, f"{h_base:.4f}",
                ha="center", va="bottom", fontsize=annotation_font_size)
        ax.text(x[i] + width/2, h_agent, f"{h_agent:.4f}",
                ha="center", va="bottom", fontsize=annotation_font_size)

        # prozentuale Änderung
        if h_base != 0:
            pct_change = 100 * (h_agent - h_base) / h_base
            color = "green" if pct_change < 0 else "red"
            ax.text(x[i] + width/2, h_agent + 0.05*max_val,
                    f"{pct_change:+.1f}%",
                    ha="center", va="bottom", fontsize=annotation_font_size,
                    color=color, fontweight="bold")

    # Achsen + Layout
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.legend([bars1, bars2], ["Baseline", "Agent"], loc="upper center")
    ax.set_ylim(0, max_val * 1.15)

    plt.title("Vergleich: BOPTEST Score")
    plt.tight_layout()
    plt.show()
