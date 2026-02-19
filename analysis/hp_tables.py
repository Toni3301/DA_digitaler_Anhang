import numpy as np

# Matrizen aus dem Townhouse -> 2 kW WP
tableQdot_con = np.array([
    [0, -15, -10, -5, 0, 5, 10, 15, 40],
    [0,	1853, 2053, 2187, 2307, 2627, 3013, 3227, 3227],
    [35, 1840, 1987, 2147, 2267, 2627, 2893, 3093, 3067],
    [45, 1947, 1947, 2107, 2213, 2587, 2853, 3000, 3000],
    [55, 1747, 1907, 2027, 2147, 2507, 2747, 2893, 2893]
], dtype=np.float64)

tableP_ele = np.array([
    [0, -15, -10, -5, 0, 5, 10, 15, 40],
    [35, 588, 540, 508, 471, 478, 502, 474, 474],
    [45, 657, 621, 596, 567, 584, 584, 573, 573],
    [55, 779, 695, 714, 692, 699, 722, 682, 682],
    [65, 896, 867, 780, 795, 864, 916, 851, 851]
], dtype=np.float64)

# Definiere den Faktor
f = 9/2

# Multipliziere jeden Eintrag außer die erste Zeile und die erste Spalte mit f
tableQdot_con[1:, 1:] *= f
tableP_ele[1:, 1:] *= f

# Gib die Matrix im gewünschten Format aus
for row in tableQdot_con:
    print("\t".join(map(str, row)))

print("")

for row in tableP_ele:
    print("\t".join(map(str, row)))






