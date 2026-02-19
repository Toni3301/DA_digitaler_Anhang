from scipy.io import loadmat
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy.interpolate import RectBivariateSpline

def mat_reader(filepath="fmu/dsres.mat"):
    '''Returns the last value of every variable stored in a dictionary
    "variable_name" : value, excluding variables that do not change over time.'''

    import DyMat

    mat_file = DyMat.DyMatFile(filepath) 
    variables = mat_file.names()

    end_vals = {}
    for variable in variables:
        werte = mat_file.data(variable)

        # skip unnecessary variables
        if variable.startswith("wP.WP.innerCycle"):
            continue

        # if variable.startswith("B_EG.room_load.mixedAir"):
        #     continue

        # skip variables that don't vary
        middle_index = len(werte) // 2
        if werte[0] == werte[middle_index] and werte[0] == werte[-1]:
            continue
        
        # save the end values of the remaining variables
        end_vals[variable] = werte[-1]
    
    return end_vals

def mat_reader_wp(filepath):
    """
    Liest eine MAT-Datei mit Wärmepumpentabellen ein.
        Erste Zeile = Außentemperaturen (T_out)
        Erste Spalte = Vorlauftemperaturen (T_VL)
        Feld (0,0) ist unbrauchbar und wird ignoriert.
    """
    data = loadmat(filepath)

    # ersten 2D-Key finden
    key = [k for k in data.keys() if not k.startswith("__")][0]
    arr = np.array(data[key])

    # Rohdaten
    raw_cols = arr[0, 1:].astype(float)   # bisher T_out
    raw_idx  = arr[1:, 0].astype(float)   # bisher T_VL
    raw_vals = arr[1:, 1:]

    df = pd.DataFrame(raw_vals, index=raw_idx, columns=raw_cols)

    df = df.sort_index()
    df = df[sorted(df.columns)]

    return df


def create_wp_interpolator(WP_table):
    """
    Erstellt einen Interpolator
    interp(T_out_query, T_VL_query)
    """
    WP_table = WP_table.sort_index()
    WP_table = WP_table[sorted(WP_table.columns)]

    T_VL = WP_table.index.values.astype(float)
    T_out = WP_table.columns.values.astype(float)
    values = WP_table.values

    #spline = RectBivariateSpline(T_VL, T_out, values, kx=3, ky=3)
    interpolator = RegularGridInterpolator((T_VL, T_out), values, bounds_error=False, fill_value=None)
    
    def interp(T_out_query, T_VL_query):
        T_out_query = np.atleast_1d(T_out_query)
        T_VL_query = np.atleast_1d(T_VL_query)

        T_VL_b, T_out_b = np.broadcast_arrays(T_VL_query, T_out_query)

        points = np.stack([T_VL_b.ravel(), T_out_b.ravel()], axis=-1)

        #result = spline.ev(T_VL_b.ravel(), T_out_b.ravel())
        result = interpolator(points)
        return result.reshape(T_VL_b.shape)

    return interp
