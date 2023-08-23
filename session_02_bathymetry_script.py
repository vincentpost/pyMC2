# %%
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd
from scipy.interpolate import griddata

# %%
from pyproj.datadir import set_data_dir
set_data_dir("c:/Users/vince/anaconda3/envs/geopandas_env/Library/share/proj/")

# %%
df = pd.read_excel(
    "data/dam_bathymetry.xlsx",
    skiprows=5,
    usecols="B,E,F",
    header=None,
    names=["z", "easting", "northing"],
)

# %%
utm_coordinates = gpd.points_from_xy(df["easting"], df["northing"])
gdf = gpd.GeoDataFrame(
    data=df["z"], 
    geometry=utm_coordinates, 
    crs="epsg:32754",
)

# %%
Path("data/dam_bathymetry").mkdir(exist_ok=True)
gdf.to_file("data/dam_bathymetry/dam_bathymetry.shp")

# %%
gdf_h = gpd.read_file("data/helper_poly/helper_poly.shp")

# %%
helper_poly = gdf_h['geometry'][0]
poly_vertices = helper_poly.exterior.xy

# %%
dfh = pd.DataFrame(
    data={
        "easting": poly_vertices[0],
        "northing": poly_vertices[1],
        "z": -0.20,
    }
)

# %%
df = pd.concat((df, dfh))

# %%
xmin, xmax = df['easting'].min(), df['easting'].max()
ymin, ymax = df['northing'].min(), df['northing'].max()
dx = dy = 0.5
xi = np.arange(xmin - 2, xmax + 2, dx)
yi = np.arange(ymin - 2, ymax + 2, dy)

# %%
X, Y = np.meshgrid(xi, yi)
cl_levels = np.arange(-2.75, 0, 0.25) # Contour levels to plot

fig3d = plt.figure()
fig_contours, axs_contours = plt.subplots(ncols=3)

for i, method in enumerate(["nearest", "cubic", "linear"]):
    zi = griddata(
        (df['easting'], df['northing']), 
        df['z'], 
        (xi[None, :], yi[:, None]), 
        method=method,
    )

    ax = axs_contours[i]
    cs = ax.contourf(X, Y, zi, cl_levels)

    ax = fig3d.add_subplot(1, 3, i+1, projection='3d')
    ax.plot_wireframe(X, Y, zi, rstride=4, cstride=4)

    # Measurements
    ax.scatter(df['easting'], df['northing'], df['z'], color='k')
    
    # Helper points
    idx = df['z'] == -0.20
    ax.scatter(df.loc[idx, 'easting'], df.loc[idx, 'northing'], df.loc[idx, 'z'], color='r')

plt.show()