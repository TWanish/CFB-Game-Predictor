#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 18:35:07 2019

@author: TMWanish

Used for actually predicting games for the next week or adhoc game predictions
"""

import pandas as pd
import os
from modelGeneration import getModel
from rankingGenerator import createRankings
from gamePredictions import predictNextWeek

try:
    path = os.path.normpath(str(os.getcwd()).split('lib')[0]+'/data/teamData.json')
except:
    print('path not found')
    

data = pd.read_json(path)
    
model = getModel(data)

print('Generating rankings...')
rankings = createRankings(data.columns.values, 0, 
                               len(data.columns.values)-1, 
                               model, data)[::-1]
print(rankings[0:25])
predictNextWeek(model, data, 11, False, file_path = path)