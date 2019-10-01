#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 18:38:32 2019

@author: TMWanish

Collection of functions for actually predicting games
"""

import pandas as pd
import numpy as np

def predictGame(team1, team2, model, data):
    team1History = []
    team2History = []
    winCount = 0
    for i in range(0,100):
        normalizer=0
        for var in model.keys():
            if var is not 'srs':
                normalizer += np.sqrt(model[var]['r_sq'])
        team1Pts = 0
        team2Pts = 0
        for var in model.keys():
            if var is 'srs':
                team1SRS = float(data.loc[var, team1])
                team2SRS = float(data.loc[var, team2])
                srs_margin = team1SRS-team2SRS
                team1Pts += srs_margin*model[var]['m']/1.4
                team2Pts -= srs_margin*model[var]['m']/1.4
            elif var.split('_')[0] == 'off':
                multiplier = np.sqrt(model[var]['r_sq'])/normalizer
                team1Pts += np.random.normal(float(data.loc[var,team1]),model[var]['std']*3\
                                             *np.sqrt(model[var]['r_sq']))*model[var]['m']\
                                             *multiplier+model[var]['b']*multiplier
                team2Pts += np.random.normal(float(data.loc[var,team2]),model[var]['std']*3\
                                             *np.sqrt(model[var]['r_sq']))*model[var]['m']\
                                             *multiplier+model[var]['b']*multiplier
            else:
                multiplier = np.sqrt(model[var]['r_sq'])/normalizer
                team1Pts += np.random.normal(float(data.loc[var,team2]),model[var]['std']*3\
                                             *np.sqrt(model[var]['r_sq']))*model[var]['m']\
                                             *multiplier+model[var]['b']*multiplier
                team2Pts += np.random.normal(float(data.loc[var,team1]),model[var]['std']*3\
                                             *np.sqrt(model[var]['r_sq']))*model[var]['m']\
                                             *multiplier+model[var]['b']*multiplier
        team1History.append(int(team1Pts))
        team2History.append(int(team2Pts))
        if int(team1Pts)>int(team2Pts):
            winCount = winCount + 1
    print(team1 + ': ' + str(np.mean(team1History)))
    print(team2 + ': ' + str(np.mean(team2History)))
    print('Win percentage: ' + str(winCount))
    return
