#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 21:20:11 2019

@author: TalWanish
"""
from gamePredictions import predictGame

def partition(teams, low, high, model, data):
    i = ( low-1 )         # index of smaller element 
    pivot = teams[high]     # pivot 
  
    for j in range(low , high): 
  
        # If current element is smaller than or 
        # equal to pivot 
        if   predictGame(teams[j],pivot, model, data, False) is not teams[j]: 
          
            # increment index of smaller element 
            i = i+1 
            teams[i],teams[j] = teams[j],teams[i] 
  
    teams[i+1],teams[high] = teams[high],teams[i+1] 
    return ( i+1 ) 

def createRankings(teams, low, high, model, data):
    if low < high: 
  
        # pi is partitioning index, arr[p] is now 
        # at right place 
        pi = partition(teams,low,high, model, data) 
  
        # Separately sort elements before 
        # partition and after partition 
        createRankings(teams, low, pi-1, model, data) 
        createRankings(teams, pi+1, high, model, data) 
    return teams
        