""" lisst_functions.py
Functions to match file names to cast number,
read in LISST data, and plot against CTD data.

Compiled from previously written notebooks.

@author: Kylene Cooley
Date: 13 Nov 2025
"""

# Import libraries used in this notebook
import os
import re
import glob
import urllib.request as request

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import xarray as xr

from plotting_functions import addintervals2axes, addprofile2axes

# Base url for data on Raw Data Archive
RDA_BASE_URL = f"https://rawdata.oceanobservatories.org/files/cruise_data/Pioneer-MAB/{cruise_folder}/LISST/"

# General LISST data download and parsing into dataset
# Version 25 Aug 2025: Retain integer pandas index as
# sample number
def load_lisst(lisst_path, header):
    # Load LISST data from CSV
    lisst_df = pd.read_csv(lisst_path, names=header)
    try: lisst_df.head(1)
    except: print("No LISST data downloaded")
    # Rename integer index to sample number
    lisst_df.rename_axis("sample_number", inplace=True)
    # Create LISST time vector for Dataframe Index
    lisst_time = pd.to_datetime(lisst_df[
        ["year", "month", "day", "hour", "minute",
         "second"]
        ], yearfirst=True, utc=True)
    lisst_df.insert(0, "time", lisst_time.values)
    # Append LISST time index to integer sample
    # number index
    # lisst_df.set_index("time", drop=True,
                    #    append=True, inplace=True)
    # Convert data frame to Xarray Dataset for easy
    # manipulation
    lisst_ds = xr.Dataset.from_dataframe(lisst_df)
    return lisst_ds

    
# Create 2D array for binned volume concentration
def concat_volume_concentration(lisst_ds):
    volumecon2D = list([])
    bins = list([])
    for var in lisst_ds.variables:
        if re.search("volumecon[0-9]+", var):
                bins.append(var)
                volumecon2D.append(lisst_ds[var])
    lisst_ds = lisst_ds.drop_vars(bins)
    str2num = lambda x: int(x.replace("volumecon", ""))
    bins = [str2num(x) for x in bins]
    lisst_ds["volume_concentration_2D"] = xr.concat(
        volumecon2D, pd.Index(bins, name="bin")
        )
    lisst_ds["volume_concentration_2D"] = lisst_ds["volume_concentration_2D"].assign_attrs(units="$\mu$L/L")
    return lisst_ds


# Mask data where depth < 0
def mask_air_data(lisst_ds):
    depth_mask = lisst_ds.sample_number[lisst_ds.depth>=0].values
    lisst_ds = lisst_ds.sel(sample_number=depth_mask)
    return lisst_ds


# Scrape the LISST readme file on the RDA
# to get CSV file names for each cast
def scrape_lisst_list(text):
    castfiles = {}
    filenext = False
    # text, urlheaders =  request.urlretrieve(RDA_URL+readme_file)
    with open(text) as f:
        for x in f:
            if "CAST" in x:
                # print(x)
                cast = x.replace("    ", "")[:-1]
                filenext = True
                continue
            if (filenext is True)&(".CSV" in x):
                # print(x)
                file = x.replace("    ", "")[:-1]
                castfiles[cast] = file
                filenext = False
            else:
                continue
    # Sort dict values into list of tuples with
    # key, value pairs in castfiles:
    pairs = list(castfiles.items())
    return pairs


# Define function to calculate the interval between samples in seconds
def time_to_next_sample(ds):
    time2 = ds.time[1:].values
    time1 = ds.time[:-1].values
    dtime = time2-time1
    dtime = dtime.astype("timedelta64[s]")
    return dtime


# Check sample intervals for anything over the expected sample interval
def find_irregular_dt(dtime, dt0):
    irregular = dtime!=dt0
    # idx = np.indices(dtime)
    # idx_irregular = zip(idx[0][irregular], idx[1][irregular])
    return np.any(irregular)


# define a function to plot casts in a group
def plot_lisst_profiles(lisst_casts, rgb, current_axes, param, legendtitle=None, legendcol=1):
    # loop through list of LISST cast files
    n = 0
    loop = lisst_casts.copy()
    while len(loop)>0:
        color = rgb[n+2]
        key, value = loop.pop(0)
        lisst_path = RDA_URL + value
        lisst_ds = load_lisst(lisst_path, csvhdr)
        lisst_ds = lisst_ds.assign_attrs(cast=key)
        # Add cast data to existing axes
        current_axes = addprofile2axes(current_axes, lisst_ds, param, color,
                                       legendtitle=legendtitle, legendcol=legendcol)
        # Advance counter for colors
        n += 1
    return current_axes

# define a function to plot sample intervals
# from many casts
def plot_lisst_interval(lisst_casts, color, current_axes, datalabel=None):
    # loop through list of LISST cast files
    loop = lisst_casts.copy()
    while len(loop)>0:
        # Load cast data
        key, value = loop.pop(0)
        lisst_path = RDA_URL + value
        lisst_ds = load_lisst(lisst_path, csvhdr)
        lisst_ds = lisst_ds.assign_attrs(cast=key)
        # Add cast data to existing axes
        if len(loop)==(len(lisst_casts)-1):
            current_axes = addintervals2axes(current_axes, lisst_ds, color,
                                             datalabel=datalabel)
        else:
            current_axes = addintervals2axes(current_axes, lisst_ds, color)
    return current_axes
