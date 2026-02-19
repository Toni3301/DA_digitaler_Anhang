import os
import sys
import numpy as np
import matplotlib.pyplot as plt

from functions.helper.mat_reader import * 

WP_tableP_ele = mat_reader_wp('fmu/WP_tableP_ele.mat')
WP_tableQdot_con = mat_reader_wp('fmu/WP_tableQdot_con.mat')
WP_tableP_ele_interp = create_wp_interpolator(WP_tableP_ele)
WP_tableQdot_con_interp = create_wp_interpolator(WP_tableQdot_con)

# -----------------------------
# HELPER FUNCTION TO PLOT 3D
# -----------------------------
def plot_surface(X, Y, Z, title, z_label, azim=-120, z_lim=None, cmap="viridis", vmin=None, vmax=None):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap=cmap, edgecolor="none", vmin=vmin, vmax=vmax)
    plt.title(title)
    ax.set_xlabel("Außentemperatur [°C]")
    ax.set_ylabel("Vorlauftemperatur [°C]")
    fig.colorbar(surf, shrink=0.5, aspect=10, label=z_label)
    if z_lim is not None:
        ax.set_zlim(0, z_lim)
    else:
        ax.set_zlim(bottom=0)
    ax.view_init(elev=30, azim=azim)
    plt.show()

# -----------------------------
# ORIGINAL DATA PLOTS
# -----------------------------
# Electrical power
x = WP_tableP_ele.columns.astype(float).values
y = WP_tableP_ele.index.astype(float).values
z = WP_tableP_ele.values.astype(float)
X, Y = np.meshgrid(x, y)
ele_min, ele_max = z.min(), z.max()
plot_surface(X, Y, z, "Kennfeld elektrische Leistung", "Elektrische Leistung [W]", 
             z_lim=1000, vmin=ele_min, vmax=ele_max)

# Thermal power
x = WP_tableQdot_con.columns.astype(float).values
y = WP_tableQdot_con.index.astype(float).values
z = WP_tableQdot_con.values.astype(float)
X, Y = np.meshgrid(x, y)
th_min, th_max = z.min(), z.max()
plot_surface(X, Y, z, "Kennfeld thermische Leistung", "Thermische Leistung [W]",
             vmin=th_min, vmax=th_max)

# COP
COP_values = WP_tableQdot_con.values / WP_tableP_ele.values
X, Y = np.meshgrid(WP_tableQdot_con.columns.astype(float), WP_tableQdot_con.index.astype(float))
cop_min, cop_max = COP_values.min(), COP_values.max()
plot_surface(X, Y, COP_values, "Kennfeld COP", "COP [ ]", azim=-170,
             vmin=cop_min, vmax=cop_max)


# -----------------------------
# INTERPOLATED DATA PLOTS
# -----------------------------
# Create finer grid for smooth interpolation
T_out_fine = np.linspace(WP_tableP_ele.index.min(), WP_tableP_ele.index.max(), 50)
T_VL_fine = np.linspace(WP_tableP_ele.columns.min(), WP_tableP_ele.columns.max(), 50)
X_fine, Y_fine = np.meshgrid(T_VL_fine, T_out_fine)

# Electrical power interpolated
Z_fine = np.zeros_like(X_fine)
for i in range(X_fine.shape[0]):
    Z_fine[i, :] = WP_tableP_ele_interp(Y_fine[i, :], X_fine[i, :])
plot_surface(X_fine, Y_fine, Z_fine, "Interpoliertes Kennfeld elektrische Leistung", "Elektrische Leistung [W]", 
             z_lim=1000, vmin=ele_min, vmax=ele_max)

# Thermal power interpolated
Z_fine = np.zeros_like(X_fine)
for i in range(X_fine.shape[0]):
    Z_fine[i, :] = WP_tableQdot_con_interp(Y_fine[i, :], X_fine[i, :])
plot_surface(X_fine, Y_fine, Z_fine, "Interpoliertes Kennfeld thermische Leistung", "Thermische Leistung [W]",
             vmin=th_min, vmax=th_max)

# COP interpolated
Z_fine = np.zeros_like(X_fine)
for i in range(X_fine.shape[0]):
    for j in range(X_fine.shape[1]):
        Qdot_con = WP_tableQdot_con_interp(Y_fine[i, j], X_fine[i, j])
        P_ele = WP_tableP_ele_interp(Y_fine[i, j], X_fine[i, j])
        Z_fine[i, j] = Qdot_con / P_ele
#Z_fine = np.where(Z_fine > 5.25, np.nan, Z_fine)
plot_surface(X_fine, Y_fine, Z_fine, "Interpoliertes Kennfeld COP", "COP [ ]", azim=-170,
             vmin=cop_min, vmax=cop_max)
