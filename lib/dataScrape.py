import requests, bs4, json

url='https://www.sports-reference.com/cfb/schools/'
res = requests.get(url)
html = res.content
soup = bs4.BeautifulSoup(html, 'html.parser')
step1 = soup.find('table', attrs={'id':'schools'})
step2 = bs4.BeautifulSoup(str(step1.findAll('tbody')),'html.parser').findAll('tr')

teamData = {}

for i in range(0,len(step2)):
    year = bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'year_max'})),'html.parser').string
    if year == '2019':
        schoolLink = bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'school_name'})),'html.parser').find('a', href=True)
        name = schoolLink.string
        link = 'https://www.sports-reference.com'+schoolLink['href']+'2019.html'
        res = requests.get(link)
        html = res.content
        soup = bs4.BeautifulSoup(html, 'html.parser')
        
        ## Summary Data (pts For, pts Against, SRS, SOS)
        step3 = soup.find('div', attrs={'data-template':'Partials/Teams/Summary'}).findAll('p')
        ## If ranked + conference play, if unranked or conference play only, if unranked and no conference
        if len(step3)==11:
            ptsF = step3[6].getText().split(' ')[1]
            ptsA = step3[8].getText().split(' ')[2]
            srs = step3[9].getText().split(' ')[1]
            sos = step3[10].getText().split(' ')[1]
        elif len(step3)==10:
            ptsF = step3[5].getText().split(' ')[1]
            ptsA = step3[7].getText().split(' ')[2]
            srs = step3[8].getText().split(' ')[1]
            sos = step3[9].getText().split(' ')[1]
        elif len(step3)==9:
            ptsF = step3[4].getText().split(' ')[1]
            ptsA = step3[6].getText().split(' ')[2]
            srs = step3[7].getText().split(' ')[1]
            sos = step3[8].getText().split(' ')[1]
        ## Summary Data (Off Rush yards, Pass Yards, YPP, Penalties, TO)
        step3 = soup.find('table', attrs={'id':'team'})
        step4 = bs4.BeautifulSoup(str(step3.findAll('tbody')),'html.parser').findAll('tr')
        off_pass_yds = bs4.BeautifulSoup(str(step4[0].find('td', attrs={'data-stat':'pass_yds'})),'html.parser').string
        off_rush_yds = bs4.BeautifulSoup(str(step4[0].find('td', attrs={'data-stat':'rush_yds'})),'html.parser').string
        off_ypp = bs4.BeautifulSoup(str(step4[0].find('td', attrs={'data-stat':'tot_yds_per_play'})),'html.parser').string
        off_pen_yds = bs4.BeautifulSoup(str(step4[0].find('td', attrs={'data-stat':'penalty_yds'})),'html.parser').string
        off_turnovers = bs4.BeautifulSoup(str(step4[0].find('td', attrs={'data-stat':'turnovers'})),'html.parser').string
        def_pass_yds = bs4.BeautifulSoup(str(step4[1].find('td', attrs={'data-stat':'opp_pass_yds'})),'html.parser').string
        def_rush_yds = bs4.BeautifulSoup(str(step4[1].find('td', attrs={'data-stat':'opp_rush_yds'})),'html.parser').string
        def_ypp = bs4.BeautifulSoup(str(step4[1].find('td', attrs={'data-stat':'opp_tot_yds_per_play'})),'html.parser').string
        def_pen_yds = bs4.BeautifulSoup(str(step4[1].find('td', attrs={'data-stat':'opp_penalty_yds'})),'html.parser').string
        def_turnovers = bs4.BeautifulSoup(str(step4[1].find('td', attrs={'data-stat':'opp_turnovers'})),'html.parser').string
        toAppend = {
                name:{
                'link':link,
                'ptsF':ptsF,
                'ptsA':ptsA,
                'srs':srs,
                'sos':sos,
                'off_pass_yds':off_pass_yds,
                'off_rush_yds':off_rush_yds,
                'off_ypp':off_ypp,
                'off_pen_yds':off_pen_yds,
                'off_turnovers':off_turnovers,
                'def_pass_yds':def_pass_yds,
                'def_rush_yds':def_rush_yds,
                'def_ypp':def_ypp,
                'def_pen_yds':def_pen_yds,
                'def_turnovers':def_turnovers
                }
                }
        teamData.update(toAppend)
        
## Getting Schedule Results
url='https://www.sports-reference.com/cfb/years/2019-schedule.html'
res = requests.get(url)
html = res.content
soup = bs4.BeautifulSoup(html, 'html.parser')
step1 = soup.find('table', attrs={'id':'schedule'})
step2 = bs4.BeautifulSoup(str(step1.findAll('tbody')),'html.parser').findAll('tr')

resultsData = {}

for i in range(0,len(step2)):
    try:
        team1 = bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'winner_school_name'})),'html.parser').find('a').string
    except:
        team1 = bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'winner_school_name'})),'html.parser').string
    team1Score = bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'winner_points'})),'html.parser').string
    if team1Score is None:
        print('done.')
        break
    
    if bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'game_location'})),'html.parser').string == "@":
        team1Home = False
    else:
        team1Home = True
    try:
        team2 = bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'loser_school_name'})),'html.parser').find('a').string
    except:
        team2 = bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'loser_school_name'})),'html.parser').string
    team2Score = bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'loser_points'})),'html.parser').string
    week = 'week-'+bs4.BeautifulSoup(str(step2[i].find('td', attrs={'data-stat':'week_number'})),'html.parser').string
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
        teamData[team1].update(results)
    except:
        pass
    try:
        teamData[team2].update(results)
    except:
        pass
    

    
with open('teamData.json', 'w') as outfile:
    json.dump(teamData, outfile)

