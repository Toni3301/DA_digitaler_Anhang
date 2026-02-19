import matplotlib.pyplot as plt


def compute_plot_params(results):
    first_key = next(iter(results))
    time_h = results[first_key]['results']['time_h']
    nSet_WP = results[first_key]['results']['nSet_WP']

    # WP-off-times (>= 1 h)
    wp_off = nSet_WP <= 1e-3
    off_start = None
    wp_off_periods = []

    for i in range(len(wp_off)):
        if wp_off[i] and off_start is None:
            off_start = time_h[i]
        elif not wp_off[i] and off_start is not None:
            off_end = time_h[i-1]
            if off_end - off_start >= 1.0:
                wp_off_periods.append((off_start, off_end))
            off_start = None
    if off_start is not None:
        off_end = time_h[-1]
        if off_end - off_start >= 1.0:
            wp_off_periods.append((off_start, off_end))

    day_starts = [0, 24, 48]
    day_labels = ['Winter', 'Frühling', 'Herbst']

    plot_params = {
        'wp_off_periods': wp_off_periods,
        'day_starts': day_starts,
        'day_labels': day_labels
    }

    return plot_params



def annotate_plot(plot_params):
    ax = plt.gca()

    # mark wp off periods
    wp_off_legend_added = False
    for start, end in plot_params['wp_off_periods']:
        ax.axvspan(
            start,
            end,
            facecolor='white',
            edgecolor='gray',
            hatch='////',
            alpha=0.5,
            zorder=0.5,
            label='WP aus' if not wp_off_legend_added else None,
        )
        wp_off_legend_added = True

    # mark days
    day_start_legend_added = False
    for t in plot_params['day_starts']:
        ax.axvline(
            t,
            color='black',
            linestyle='--',
            linewidth=1.0,
            zorder=2,
            label='Tagesbeginn' if not day_start_legend_added else None,
        )
        day_start_legend_added = True

    # longer y axis for visible annotations
    ymin, ymax = ax.get_ylim()
    y_extra = 0.12 * (ymax - ymin)
    ax.set_ylim(ymin, ymax + y_extra)

    y_label_pos = ymax + 0.5 * y_extra

    # box for day labels
    day_starts = plot_params['day_starts']
    day_labels = plot_params['day_labels']
    x_max = ax.get_xlim()[1]

    for i, (t_start, label) in enumerate(zip(day_starts, day_labels)):
        if i < len(day_starts) - 1:
            t_end = day_starts[i + 1]
        else:
            t_end = x_max

        t_center = 0.5 * (t_start + t_end)

        ax.text(
            t_center,
            y_label_pos,
            label,
            ha='center',
            va='center',
            fontsize=10,
            zorder=3,
            bbox=dict(
                facecolor='white',
                edgecolor='gray',
                boxstyle='round,pad=0.25',
                linewidth=0.8,
            ),
        )

    ax.legend()
