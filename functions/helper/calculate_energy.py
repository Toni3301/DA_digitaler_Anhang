import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from functions.helper.mat_reader import *


def calculate_energy(sim_step_size, T_VL_WP, T_sou_WP, nSet_WP, WP_tableQdot_con, WP_tableP_ele, batch=False):
    '''calculates energy consumption from WP tables'''
    P_nominal = 20  # scaling factor in dymola

    # ensure array inputs
    T_sou_WP = np.atleast_1d(T_sou_WP)  # [°C]
    T_VL_WP = np.atleast_1d(T_VL_WP)  # [°C]
    nSet_WP = np.atleast_1d(nSet_WP)  # [ ]

    if not (T_sou_WP.shape == T_VL_WP.shape == nSet_WP.shape):
        raise ValueError("T_VL_WP, T_sou_WP and nSet_WP must have the same size")

    Qdot_values = WP_tableQdot_con(T_sou_WP, T_VL_WP) * nSet_WP  # [W]
    P_values = WP_tableP_ele(T_sou_WP, T_VL_WP) * nSet_WP**3  # [W]

    Q_use = Qdot_values * sim_step_size / 3.6e6
    P_use = P_values * sim_step_size / 3.6e6

    if not batch:
        Q_use = np.sum(Q_use)
        P_use = np.sum(P_use)

    return Q_use * P_nominal, P_use * P_nominal * 10  # [kWh]
        

if __name__ == "__main__":
    WP_tableP_ele_path = "fmu/WP_tableP_ele.mat"
    WP_tableQdot_con_path = "fmu/WP_tableQdot_con.mat"

    # load and interpolate tables
    WP_tableP_ele = create_wp_interpolator(mat_reader_wp(WP_tableP_ele_path))
    WP_tableQdot_con = create_wp_interpolator(mat_reader_wp(WP_tableQdot_con_path))

    # debug
    raw = mat_reader_wp(WP_tableQdot_con_path)
    print("T_VL:", raw.index.values)
    print("T_out:", raw.columns.values)

    # parameters
    sim_step_size = 60
    
    T_VL_fine = np.linspace(0, 55, 50)
    T_out_fine = np.linspace(-15, 40, 50)
    T_VL_grid, T_out_grid = np.meshgrid(T_VL_fine, T_out_fine)

    nSet_WP = np.ones_like(T_VL_grid)  

    # arrays for results
    Q_table = np.zeros_like(T_VL_grid)
    P_table = np.zeros_like(T_VL_grid)
    Q_physical = np.zeros_like(T_VL_grid)
    P_physical = np.zeros_like(T_VL_grid)


    # get values
    for i in range(T_VL_grid.shape[0]):
        Q_table[i, :], P_table[i, :] = calculate_energy(
            sim_step_size=sim_step_size,
            T_VL_WP=T_VL_grid[i, :],
            T_sou_WP=T_out_grid[i, :],
            nSet_WP=nSet_WP[i, :],
            WP_tableQdot_con=WP_tableQdot_con,
            WP_tableP_ele=WP_tableP_ele,
            batch=True
        )

    COP_table = np.divide(Q_table, np.maximum(P_table, 1e-9))

    def plot_surface(X, Y, Z, title, z_label, azim=-120, z_lim=None, cmap="viridis", vmin=None, vmax=None):
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(X, Y, Z, cmap=cmap, edgecolor="none", vmin=vmin, vmax=vmax)
        plt.title(title)
        ax.set_xlabel("Vorlauftemperatur [°C]")
        ax.set_ylabel("Außentemperatur [°C]")
        fig.colorbar(surf, shrink=0.5, aspect=10, label=z_label)
        if z_lim is not None:
            ax.set_zlim(0, z_lim)
        else:
            ax.set_zlim(bottom=0)
        ax.view_init(elev=30, azim=azim)
        plt.show()

    # table
    plot_surface(T_VL_grid, T_out_grid, Q_table, "Kennfeld thermische Leistung, tabellarisch", "Thermische Leistung [kW]", azim=-150)
    plot_surface(T_VL_grid, T_out_grid, P_table, "Kennfeld elektrische Leistung, tabellarisch", "Elektrische Leistung [kW]", azim=-150)
    plot_surface(T_VL_grid, T_out_grid, COP_table, "Kennfeld COP, tabellarisch", "COP [ ]", azim=-60)
