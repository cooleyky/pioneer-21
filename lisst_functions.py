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