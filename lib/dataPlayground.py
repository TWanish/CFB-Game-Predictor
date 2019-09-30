#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 12:57:16 2019

@author: Wanish, Tal

Playground for understanding individual stat importance and modeling

"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

try:
    path = os.path.normpath(str(os.getcwd()).split('lib')[0]+'/data/teamData.json')
except:
    print('path not found')
    
data = pd.read_json(path).drop(['link'])

## General Stat Fitting
var_list = {}
for x_var in ['off_pass_yds', 'off_pen_yds', 'off_rush_yds', 'off_turnovers', 
              'off_ypp', 'def_pass_yds', 'def_pen_yds', 'def_rush_yds', 
              'def_turnovers', 'def_ypp' ]:
    x = np.array(data.loc[x_var]).reshape(-1,1) #pass, pen, rush, turnovers, ypp
    if x_var.split('_')[0]=='off':
        y = data.transpose()['ptsF']
    elif x_var.split('_')[0]=='def':
        y = data.transpose()['ptsA']
    model = LinearRegression().fit(x, y)
    r = model.score(x, y)
    var_list[x_var]={'r_sq':r,
            'm':model.coef_,
            'b':model.intercept_
            }
    
## SRS Difference Trending

    