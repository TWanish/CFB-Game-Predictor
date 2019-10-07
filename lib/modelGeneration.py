#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 12:57:16 2019

@author: TMWanish

Playground for understanding individual stat importance and modeling

"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split as tts
import matplotlib.pyplot as plt

def getModel(data):
    ## General Stat Fitting
    var_list = {}
    
    for x_var in list(data.index):
        if 'off_' in x_var:
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
        else:
            pass
        
    ## Per Game Trending
    srs_x = []
    margin_y = []
    def_stats = {}
    def_pts = {}
    for team in data.columns.values:
        for i in range(0,len(data[team].values)):
            team_week = data[team].values[i]
            if type(team_week) is dict:
                try:
                    win_team = team_week['winning-team']
                    win_pts = int(team_week['winning-score'])
                    win_srs = float(data.loc['srs',win_team])
                    lose_team = team_week['losing-team']
                    lose_pts = int(team_week['losing-score'])
                    lose_srs = float(data.loc['srs',lose_team])
                    margin = win_pts-lose_pts
                    srs_margin = win_srs - lose_srs
                    srs_x.append(srs_margin)
                    margin_y.append(margin)
                    
                    for x_var in list(data.index):
                        if 'def_' in x_var:
                            try:
                                def_stats[x_var].append(float(data.loc[x_var,lose_team]))
                                def_pts[x_var].append(float(win_pts))
                                def_stats[x_var].append(float(data.loc[x_var,win_team]))
                                def_pts[x_var].append(float(lose_pts))
                            except:
                                def_stats[x_var] = [float(data.loc[x_var, lose_team])]
                                def_pts[x_var] = [(float(win_pts))]
                                def_stats[x_var].append(float(data.loc[x_var,win_team]))
                                def_pts[x_var].append(float(lose_pts))
                        else:
                            pass
                    
                except:
                    continue
                
    srs_model_x = np.array(srs_x).reshape(-1,1)
    srs_model = LinearRegression().fit(srs_model_x, margin_y)
    var_list['srs']={'r_sq':srs_model.score(srs_model_x, margin_y),
            'm':srs_model.coef_,
            'b':srs_model.intercept_
            }
    for var in list(data.index):
        if 'def_' in var:
            def_model = LinearRegression().fit(np.array(def_stats[var]).reshape(-1,1),
                                         def_pts[var])
            var_list[var]={'r_sq':def_model.score(np.array(def_stats[var]).reshape(-1,1), 
                    def_pts[var]),
                    'm':def_model.coef_,
                    'b':def_model.intercept_
                    }
        else:
            pass
    ## Pick out useful variables and build a model
    util_vars = []
    for var in var_list:
        if var_list[var]['r_sq']>0.225: # Marker for significance, increase as season progresses (start at .10, finish at .35)
            util_vars.append(var)
            var_list[var]['mean']=data.loc[var].astype(float).values.mean()
            var_list[var]['std']=data.loc[var].astype(float).values.std()
    final_model = {}
    for var in util_vars:
        final_model[var]=var_list[var]
    return final_model

