import csv
from pathlib import Path

import batman
import matplotlib.pyplot as plt
import numpy as np

# Folder that holds this script (src/daneel/detection). __file__ is the
# script's own path, and .parent drops the file name so only the folder is left.
HERE = Path(__file__).parent

# Top of the repo, three folders up: detection -> daneel -> src -> repo root.
# This makes the paths below work no matter where you run the script from.
ROOT = Path(__file__).parents[3]

# Input table from the NASA Exoplanet Archive.
# The "/" operator in pathlib joins path pieces, like "ROOT/data/file.csv".
DATA_FILE = ROOT / "data" / "hip67522c_nasa_archive.csv"

# The plot image is saved here, next to the
PLOT_FILE = HERE / "hip67522c_transit.png"

# -------- let's do it now --------


# --- 1. Load the planet's parameters

with open(DATA_FILE, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
    
# Use the archive's default solution (Barber et al. 2024) for every value.
paper = next(row for row in rows if row["default_flag"] == "1")

# --- 2. Set up the transit model

params = batman.TransitParams()
params.t0 = 0.0                                 # mid-transit time [days]
params.per = float(paper["pl_orbper"])          # orbital period [days]
params.rp = float(paper["pl_ratror"])           # planet radius [stellar radii]
params.a = float(paper["pl_ratdor"])            # semi-major axis [stellar radii]
params.inc = float(paper["pl_orbincl"])         # inclination [deg]
params.ecc = float(paper["pl_orbeccen"])        # eccentricity
params.w = float(paper["pl_orblper"])           # argument of periastron [deg]
params.u = [0.319, 0.268]                       # limb-darkening coefficients
params.limb_dark = "quadratic"

print("Barber et al. 2024:", params.per, params.rp, params.a,
      params.inc, params.ecc, params.w)

# --- 3. Compute the light curve

# The transit lasts about 6 hours, so ±6 hours around mid-transit is plenty.
time = np.linspace(-0.25, 0.25, 1000)           # [days]
flux = batman.TransitModel(params, time).light_curve(params)

depth = 100 * (1 - flux.min())                  # [%]
in_transit = time[flux < 1]
duration = 24 * (in_transit[-1] - in_transit[0])  # [hours]

print(f"Transit depth:    {depth:.3f} %")
print(f"Transit duration: {duration:.2f} h")

# --- 4. Plot it 

plt.plot(time * 24, flux)                       # hours read easier than days
plt.xlabel("Time from mid-transit [hours]")
plt.ylabel("Relative flux")
plt.title("HIP 67522 c (Barber et al. 2024)")
plt.savefig(PLOT_FILE, dpi=150)
plt.show()
