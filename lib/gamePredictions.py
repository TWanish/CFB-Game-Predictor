#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 18:38:32 2019

@author: TMWanish

Collection of functions for actually predicting games
"""

import pandas as pd
import numpy as np
import requests
import bs4

def predictGame(team1, team2, model, data, output):
    
    if team1 in data.columns.values:
        pass
    else:
        for team in data.columns.values:
            if team1 in data.loc['alias',team]:
                team1 = team
                
    if team2 in data.columns.values:
        pass
    else:
        for team in data.columns.values:
            if team2 in data.loc['alias',team]:
                team2 = team
                    
    team1History = []
    team2History = []
    winCount = 0
    for i in range(0,1000):
        normalizer=0
        for var in model.keys():
            if var is not 'srs':
                normalizer += np.sqrt(model[var]['r_sq']) # r instead of r^2
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
                multiplier = np.sqrt(model[var]['r_sq'])/normalizer #specific r / sum of all rs
                
                #pts = sum((variable value w/ 3*stdev*r)*coef*(r/sum(r))+intercept*(r/sum(r)))
                team1Pts += np.random.normal(float(data.loc[var,team1]),model[var]['std']*6\
                                             *np.sqrt(model[var]['r_sq']))*model[var]['m']\
                                             *multiplier+model[var]['b']*multiplier
                team2Pts += np.random.normal(float(data.loc[var,team2]),model[var]['std']*6\
                                             *np.sqrt(model[var]['r_sq']))*model[var]['m']\
                                             *multiplier+model[var]['b']*multiplier
            else:
                multiplier = np.sqrt(model[var]['r_sq'])/normalizer
                team1Pts += np.random.normal(float(data.loc[var,team2]),model[var]['std']*6\
                                             *np.sqrt(model[var]['r_sq']))*model[var]['m']\
                                             *multiplier+model[var]['b']*multiplier
                team2Pts += np.random.normal(float(data.loc[var,team1]),model[var]['std']*6\
                                             *np.sqrt(model[var]['r_sq']))*model[var]['m']\
                                             *multiplier+model[var]['b']*multiplier
        team1History.append(int(team1Pts))
        team2History.append(int(team2Pts))
        if int(team1Pts)>int(team2Pts):
            winCount = winCount + 1
            
    if output is True:
        print(team1 + ': ' + str(np.mean(team1History)))
        print(team2 + ': ' + str(np.mean(team2History)))
        print('Win percentage: ' + str(winCount/10))
    
    if np.mean(team1History)>np.mean(team2History):
        winningTeam = team1
    else:
        winningTeam = team2
        
    gameSummary = {'Team 1': team1,
                   'Team 1 Score': np.mean(team1History),
                   'Team 2': team2,
                   'Team 2 Score': np.mean(team2History),
                   'Winning Percentage Team 1': winCount/10,
                   'Winning Team': winningTeam,
                   'Spread': round(2*(np.mean(team1History)-np.mean(team2History)))/2.0}
    return gameSummary

def predictNextWeek(model, data, week, output, file_path = None):
    ## Getting Schedule Results            
    url='https://www.sports-reference.com/cfb/years/2019-schedule.html'
    res = requests.get(url)
    html = res.content
    soup = bs4.BeautifulSoup(html, 'html.parser')
    step1 = soup.find('table', attrs={'id':'schedule'})
    step2 = bs4.BeautifulSoup(str(step1.findAll('tbody')),'html.parser').findAll('tr')
    dataDict = data.to_dict()
    weekName = 'week-'+str(week)
    
    for i in range(0,len(step2)):
        if str(week) == bs4.BeautifulSoup(str(step2[i].find('td',
                                             attrs={'data-stat':'week_number'})),'html.parser').string:
            try:
                team1 = bs4.BeautifulSoup(str(step2[i].find('td', 
                                              attrs={'data-stat':'winner_school_name'})),'html.parser').find('a').string
            except:
                team1 = bs4.BeautifulSoup(str(step2[i].find('td',
                                              attrs={'data-stat':'winner_school_name'})),'html.parser').string
            try:
                team2 = bs4.BeautifulSoup(str(step2[i].find('td',
                                              attrs={'data-stat':'loser_school_name'})),'html.parser').find('a').string
            except:
                team2 = bs4.BeautifulSoup(str(step2[i].find('td',
                                              attrs={'data-stat':'loser_school_name'})),'html.parser').string
            try:
                gameSummary = predictGame(team1, team2, model, data, False)
                team1 = gameSummary['Team 1'] # Overwriting team 1 value if an alias was used
                team2 = gameSummary['Team 2']
                team1Score = gameSummary['Team 1 Score']
                team2Score = gameSummary['Team 2 Score']
                team1WP = gameSummary['Winning Percentage Team 1']
                spread = gameSummary['Spread']
                results = {
                            'predictions':
                                {
                                    'team-1':team1,
                                    'team-1-score':team1Score,
                                    'team-2':team2,
                                    'team-2-score':team2Score,
                                    'team-1-win-chance':team1WP,
                                    'spread':spread
                                }
                            }
                                    
                if output is True:
                    print(results)
                    
            except KeyError:
                continue
            
            try:
                dataDict[team1][weekName].update(results)
            except KeyError:
                try:
                    dataDict[team1][weekName] = results
                except KeyError:
                    pass
            try:
                dataDict[team2][weekName].update(results)
            except KeyError:
                try:
                    dataDict[team2][weekName] = results
                except KeyError:
                    pass
            
    data = pd.DataFrame.from_dict(dataDict)
    
    if file_path is not None:
        print('saving...')
        data.to_json(file_path)
        
    return data