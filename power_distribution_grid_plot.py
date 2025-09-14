import math
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import pandas as pd
from armi import configure
from armi.reactor import grids

configure(permissive=True)

# Create hex grid with 1.0 cm pitch
hexes = grids.HexGrid.fromPitch(1.0)

# Load data from CSV files
inner_data = pd.read_csv("inner_FAs.csv") # inner assembly data
outer_data = pd.read_csv("outer_FAs.csv") # outer assembly data

# Combine data into a single dictionary of (i, j) to power values
power_values = {(row['x'], row['y']): row['Power (MW)'] for _, row in pd.concat([inner_data, outer_data]).iterrows()}

# Generate power list for color mapping
power_list = [power for power in power_values.values()] # Non-zero power list

polys = []
fig, ax = plt.subplots(dpi=600)
ax.set_aspect("equal")
ax.set_axis_off()

assembly_count = 187 # Toal number of assemblies (including assemblies that do not generate power)

for hex_i in hexes.generateSortedHexLocationList(assembly_count):
    x, y, z = hex_i.getGlobalCoordinates()
    i, j = hex_i.i, hex_i.j
    if (i, j) in power_values:
        power = power_values[(i, j)]
        ax.text(x, y, f"{power:.2f}", ha="center", va="center", fontsize=4.5)
        polys.append(mpatches.RegularPolygon((x, y), numVertices=6, radius=1 / math.sqrt(3), orientation=math.pi / 2))
    else:
        polys.append(mpatches.RegularPolygon((x, y), numVertices=6, radius=1 / math.sqrt(3), orientation=math.pi / 2, facecolor='white', edgecolor='k'))

# Use raw power values for color mapping with a custom normalization
min_power = min(power_list) if power_list else 0
max_power = max(power_list) if power_list else 1
norm = plt.Normalize(min_power, max_power)
cmap = plt.cm.Oranges
power_colors = [power_values.get((i, j), 0) for i, j in [(hex_i.i, hex_i.j) for hex_i in hexes.generateSortedHexLocationList(assembly_count)]]
patches = PatchCollection(polys, facecolors=cmap(norm(power_colors)) if power_list else ['white'], ec='k')
ax.add_collection(patches)

# Add colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # only needed for older mpl
cbar = plt.colorbar(sm, ax=ax, shrink=.8)
cbar.set_label("Assembly Power (MW)")


# Create a bounding box around patches with a small margin (2%)
bbox = patches.get_datalim(ax.transData)
bbox = bbox.expanded(1.02, 1.02)
ax.set_xlim(bbox.xmin, bbox.xmax)
ax.set_ylim(bbox.ymin, bbox.ymax)

plt.show()