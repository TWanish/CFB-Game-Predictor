import requests
import bs4
import json
import os
import pandas as pd

def updateSchoolInfo(teamData, link, name = None):
    res = requests.get(link)
    html = res.content
    soup = bs4.BeautifulSoup(html, 'html.parser')
    ## Summary Data (pts For, pts Against, SRS, SOS)
    step = soup.find('div', attrs={'data-template':'Partials/Teams/Summary'}).findAll('p')
    long_alias = soup.find('div', attrs={'id':
        'bottom_nav_container'}).findAll('p')[1].find('a').getText().split('2019 ')[1].split(' Pages')[0]
    short_alias = soup.find('div', attrs={'data-template':
        'Partials/Teams/Summary'}).findAll('span')[1].getText()
    alias = [long_alias, short_alias]
    ## If ranked + conference play, if unranked or conference play only, if unranked and no conference
    if len(step)==11:
        ptsF = step[6].getText().split(' ')[1]
        ptsA = step[8].getText().split(' ')[2]
        srs = step[9].getText().split(' ')[1]
        sos = step[10].getText().split(' ')[1]
    elif len(step)==10:
        ptsF = step[5].getText().split(' ')[1]
        ptsA = step[7].getText().split(' ')[2]
        srs = step[8].getText().split(' ')[1]
        sos = step[9].getText().split(' ')[1]
    elif len(step)==9:
        ptsF = step[4].getText().split(' ')[1]
        ptsA = step[6].getText().split(' ')[2]
        srs = step[7].getText().split(' ')[1]
        sos = step[8].getText().split(' ')[1]
    toAppend = {
            name:{
            'alias':alias,
            'link':link,
            'ptsF':ptsF,
            'ptsA':ptsA,
            'srs':srs,
            'sos':sos,
                 }
               }
    ## Summary Data (Off Rush yards, Pass Yards, YPP, Penalties, TO)
    step = soup.find('table', attrs={'id':'team'})
    step2 = bs4.BeautifulSoup(str(step.findAll('tbody')),'html.parser').findAll('tr')
    offensiveStats = step2[0].findAll('td')
    defensiveStats = step2[1].findAll('td')
    ## Offensive Stats
    for i in range(0,len(offensiveStats)):
        stat = offensiveStats[i]['data-stat']
        if stat == 'g':
            continue
        value = offensiveStats[i].getText()
        toAppend[name].update({'off_'+stat:value})
    for j in range(0,len(defensiveStats)):
        stat = defensiveStats[j]['data-stat']
        if stat == 'g':
            continue
        value = defensiveStats[j].getText()
        toAppend[name].update({'def_'+stat:value})
    teamData.update(toAppend)
    return

path = os.path.normpath(str(os.getcwd()).split('lib')[0]+'/data/teamData.json')
print(path)

teamData = {}

try:
    data = pd.read_json(path)
    teamData = data.to_dict()
    print('Found Existing Data File')
    for school in list(teamData.keys()):
        updateSchoolInfo(teamData, teamData[school]['link'])
        print('Updating ' + school)
    
except:
    print('Existing data file not found')
    url='https://www.sports-reference.com/cfb/schools/'
    res = requests.get(url)
    html = res.content
    soup = bs4.BeautifulSoup(html, 'html.parser')
    step1 = soup.find('table', attrs={'id':'schools'})
    step2 = bs4.BeautifulSoup(str(step1.findAll('tbody')),'html.parser').findAll('tr')
    
    for i in range(0,len(step2)):
        year = bs4.BeautifulSoup(str(step2[i].find('td',
                                     attrs={'data-stat':'year_max'})),'html.parser').string
        if year == '2019':
            schoolLink = bs4.BeautifulSoup(str(step2[i].find('td',
                                           attrs={'data-stat':'school_name'})),'html.parser').find('a', href=True)
            name = schoolLink.string
            print('Fetching ' + name)
            link = 'https://www.sports-reference.com'+schoolLink['href']+'2019.html'
            updateSchoolInfo(teamData, link, name)
        
## Getting Schedule Results
print('Updating Schedule Results...')
url='https://www.sports-reference.com/cfb/years/2019-schedule.html'
res = requests.get(url)
html = res.content
soup = bs4.BeautifulSoup(html, 'html.parser')
step1 = soup.find('table', attrs={'id':'schedule'})
step2 = bs4.BeautifulSoup(str(step1.findAll('tbody')),'html.parser').findAll('tr')

resultsData = {}

for i in range(0,len(step2)):
    week = 'week-'+bs4.BeautifulSoup(str(step2[i].find('td',
                                         attrs={'data-stat':'week_number'})),'html.parser').string
    try:
        team1 = bs4.BeautifulSoup(str(step2[i].find('td', 
                                      attrs={'data-stat':'winner_school_name'})),'html.parser').find('a').string
    except:
        team1 = bs4.BeautifulSoup(str(step2[i].find('td',
                                      attrs={'data-stat':'winner_school_name'})),'html.parser').string
    try:
        if 'winning-score' in teamData[team1][week].keys():
            continue
        else:
            raise ValueError('Not present for '+ week)
    except:
        team1Score = bs4.BeautifulSoup(str(step2[i].find('td',
                                           attrs={'data-stat':'winner_points'})),'html.parser').string
        if team1Score is None:
            print('done.')
            break
        
        if bs4.BeautifulSoup(str(step2[i].find('td',
                                 attrs={'data-stat':'game_location'})),'html.parser').string == "@":
            team1Home = False
        else:
            team1Home = True
        try:
            team2 = bs4.BeautifulSoup(str(step2[i].find('td',
                                          attrs={'data-stat':'loser_school_name'})),'html.parser').find('a').string
        except:
            team2 = bs4.BeautifulSoup(str(step2[i].find('td',
                                          attrs={'data-stat':'loser_school_name'})),'html.parser').string
        team2Score = bs4.BeautifulSoup(str(step2[i].find('td',
                                           attrs={'data-stat':'loser_points'})),'html.parser').string
        
        results = {
                week:
                    {
                        'winning-team':team1,
                        'winning-score': team1Score,
                        'winning-team-home':team1Home,
                        'losing-team':team2,
                        'losing-score':team2Score
                    }
                }
        try:
            existingWeek = teamData[team1][week]
        except:
            existingWeek = {}
        existingWeek.update(results)
        try:
            teamData[team1].update(existingWeek)
        except:
            for team in teamData.keys():
                if team1 in teamData[team]['alias']:
                    team1 = team
                    teamData[team1].update(existingWeek)
                    break
        try:
            teamData[team2].update(existingWeek)
        except:
            for team in teamData.keys():
                if team2 in teamData[team]['alias']:
                    team2 = team
                    teamData[team2].update(existingWeek)
                    break
    
with open(path, 'w') as outfile:
    json.dump(teamData, outfile)