#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 18:35:07 2019

@author: TMWanish

Used for actually predicting games for the next week or adhoc game predictions
"""

import pandas as pd
import os
from modelGeneration import getModel, getMLDF
from rankingGenerator import createRankings

try:
    path = os.path.normpath(str(os.getcwd()).split('lib')[0]+'/data/teamData.json')
except:
    print('path not found')
data = pd.read_json(path).drop(['link'])
    
model = getModel(data)

#predictGame('Clemson', 'Auburn', model, data)

rankings = createRankings(data.columns.values, 0, 
                               len(data.columns.values)-1, 
                               model, data)[::-1][0:25]