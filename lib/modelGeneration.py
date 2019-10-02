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
    data = data.drop(['link'])
    var_list = {}
    for x_var in ['off_pass_yds', 'off_pen_yds', 'off_rush_ypa', 'off_turnovers', 
                  'off_ypp', 'off_firstDown']:
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
                    
                    for x_var in ['def_pass_yds', 'def_pen_yds', 'def_rush_ypa', 
                                  'def_turnovers', 'def_ypp', 'ptsA', 'def_firstDown' ]:
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
                    
                except:
                    continue
                
    srs_model_x = np.array(srs_x).reshape(-1,1)
    srs_model = LinearRegression().fit(srs_model_x, margin_y)
    var_list['srs']={'r_sq':srs_model.score(srs_model_x, margin_y),
            'm':srs_model.coef_,
            'b':srs_model.intercept_
            }
    for var in ['def_pass_yds', 'def_pen_yds', 'def_rush_ypa', 'def_turnovers',
                'def_ypp', 'ptsA', 'def_firstDown']:
        def_model = LinearRegression().fit(np.array(def_stats[var]).reshape(-1,1),
                                     def_pts[var])
        var_list[var]={'r_sq':def_model.score(np.array(def_stats[var]).reshape(-1,1), 
                def_pts[var]),
                'm':def_model.coef_,
                'b':def_model.intercept_
                }
    ## Pick out useful variables and build a model
    util_vars = []
    for var in var_list:
        if var_list[var]['r_sq']>0.15:
            new_var_name = var+'/ppg'
            util_vars.append(var)
            data.loc[new_var_name]=data.loc[var].astype(float)\
            /data.loc['ptsF'].astype(float)
            var_list[var]['mean']=data.loc[var].astype(float).values.mean()
            var_list[var]['std']=data.loc[var].astype(float).values.std()
    final_model = {}
    for var in util_vars:
        final_model[var]=var_list[var]
    return final_model

def getMLDF(data):
    data = data.drop(['link'])
    off_ypp = []
    off_turnovers = []
    off_rush_ypa = []
    off_pen_yds = []
    off_pass_yds = []
    off_firstDown = []
    off_srs = []
    def_ypp = []
    def_turnovers = []
    def_rush_ypa = []
    def_pen_yds = []
    def_pass_yds = []
    def_firstDown = []
    def_srs = []
    ptsF =[]
    columns = ['off_ypp', 'off_turnovers', 'off_rush_ypa', 'off_pen_yds', 
               'off_pass_yds', 'off_firstDown', 'off_srs', 'def_ypp', 'def_turnovers',
               'def_rush_yds', 'def_pen_yds', 'def_pass_yds', 'def_firstDown',
               'def_srs', 'ptsF']
    for team in data.columns.values:
        for i in range(0,len(data[team].values)):
            team_week = data[team].values[i]
            if type(team_week) is dict:
                try:
                    win_team = team_week['winning-team']
                    off_ypp.append(float(data.loc['off_ypp',win_team]))
                    off_turnovers.append(float(data.loc['off_turnovers',win_team]))
                    off_rush_ypa.append(float(data.loc['off_rush_ypa',win_team]))
                    off_pen_yds.append(float(data.loc['off_pen_yds',win_team]))
                    off_pass_yds.append(float(data.loc['off_pass_yds',win_team]))
                    off_firstDown.append(float(data.loc['off_firstDown',win_team]))
                    off_srs.append(float(data.loc['srs',win_team]))
                    lose_team = team_week['losing-team']
                    def_ypp.append(float(data.loc['def_ypp',lose_team]))
                    def_turnovers.append(float(data.loc['def_turnovers',lose_team]))
                    def_rush_ypa.append(float(data.loc['def_rush_ypa',lose_team]))
                    def_pen_yds.append(float(data.loc['def_pen_yds',lose_team]))
                    def_pass_yds.append(float(data.loc['def_pass_yds',lose_team]))
                    def_firstDown.append(float(data.loc['def_firstDown',lose_team]))
                    def_srs.append(float(data.loc['srs',lose_team]))
                    ptsF.append(float(team_week['winning-score']))
                    
                    off_ypp.append(float(data.loc['off_ypp',lose_team]))
                    off_turnovers.append(float(data.loc['off_turnovers',lose_team]))
                    off_rush_ypa.append(float(data.loc['off_rush_ypa',lose_team]))
                    off_pen_yds.append(float(data.loc['off_pen_yds',lose_team]))
                    off_pass_yds.append(float(data.loc['off_pass_yds',lose_team]))
                    off_firstDown.append(float(data.loc['off_firstDown',lose_team]))
                    off_srs.append(float(data.loc['srs',lose_team]))
                    def_ypp.append(float(data.loc['def_ypp',win_team]))
                    def_turnovers.append(float(data.loc['def_turnovers',win_team]))
                    def_rush_ypa.append(float(data.loc['def_rush_ypa',win_team]))
                    def_pen_yds.append(float(data.loc['def_pen_yds',win_team]))
                    def_pass_yds.append(float(data.loc['def_pass_yds',win_team]))
                    def_firstDown.append(float(data.loc['def_firstDown',win_team]))
                    def_srs.append(float(data.loc['srs',win_team]))
                    ptsF.append(float(team_week['losing-score']))

                except:
                    continue
                
    df = pd.DataFrame(list(zip(off_ypp, off_turnovers, off_rush_ypa, 
                               off_pen_yds, off_pass_yds, off_firstDown, off_srs,
                               def_ypp, def_turnovers, def_rush_ypa, def_pen_yds,
                               def_pass_yds, def_firstDown, def_srs, 
                               ptsF)), columns=columns)
    X = df.drop(['ptsF'], axis=1)
    y = df['ptsF'].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    #----Reducing remaining variables into 2
    LDA = LinearDiscriminantAnalysis(n_components=5, shrinkage='auto', solver='eigen')
    LDA_reduced_df = LDA.fit(X_scaled,y).transform(X_scaled)
    print(LDA_reduced_df)
    classifier = RFC(n_estimators = 100, n_jobs = -1)
    X_train, X_test, y_train, y_test = tts(LDA_reduced_df,y,test_size = 0.2)
    classifier=classifier.fit(X_train, y_train)
    print(classifier.score(X_test, y_test))
    return 