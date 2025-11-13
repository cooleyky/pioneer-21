""" plotting_functions.py
Useful plotting functions copied from notebooks
previously written.

@author: Kylene Cooley
Date: 13 Nov 2025
"""

import cmocean
import matplotlib.pyplot as plt

from lisst_functions import time_to_next_sample, find_irregular_dt

def addprofile2axes(ax, data, variable, color, legendtitle=None, legendcol=1):
    ax.plot(data[variable], data["depth"],
             c=color, label=data.cast, alpha = 0.75)
    ax.legend(fontsize='xx-small', ncol=legendcol, title=legendtitle)
    ax.set_xlabel(variable.replace("_"," ").title())
    return ax

def rgb_from_dict(list_in, cmap):
    # Get dictionary for colormap with one color for each cast
    cmdict = cmocean.tools.get_dict(cmap, N=len(list_in)+2)
    # Make lists of RGB values for cast loop
    red = [float(x[1]) for x in cmdict["red"]]
    green = [float(x[1]) for x in cmdict["green"]]
    blue = [float(x[1]) for x in cmdict["blue"]]
    rgb = list(zip(red, green, blue))
    return rgb

def addintervals2axes(ax, data, color, datalabel=None):
    sample_interval = time_to_next_sample(data)
    irregular_intervals = find_irregular_dt(sample_interval, 2)
    if irregular_intervals:
        print(data.cast)
    # print(sample_interval.shape)
    # print(data["sample_number"][0:-3].shape)
    ax.scatter(data["sample_number"][:-1], sample_interval,
             c=color, label=datalabel, edgecolors="none")
    return ax