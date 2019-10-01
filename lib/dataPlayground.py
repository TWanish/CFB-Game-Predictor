#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 18:35:07 2019

@author: TMWanish

Used for actually predicting games for the next week or adhoc game predictions
"""

import pandas as pd
import numpy as np
import os
from modelGeneration import getModel, getMLDF
from gamePredictions import predictGame

try:
    path = os.path.normpath(str(os.getcwd()).split('lib')[0]+'/data/teamData.json')
except:
    print('path not found')
data = pd.read_json(path).drop(['link'])
    
model = getModel(data)

predictGame('Auburn', 'Florida', model, data)