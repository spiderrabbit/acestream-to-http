from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import timedelta
thisyear = datetime.today().strftime("%Y")
r = requests.get('https://www.dailymail.co.uk/sport/football/premier-league/fixtures.html#fixtures')
data = r.text
soup = BeautifulSoup(data, features="html.parser")
#match_dict[lstr.encode_contents()][datestr].append('{0} vs {1} {2} {3}'.format(matchlist[1], matchlist[2], datestr, matchlist[0]))
match_dict = {}
leagues = soup.find('ul', {'class':'football-competition-dropdown-list'})

for a in leagues.findAll('a'):
  r = requests.get('https://www.dailymail.co.uk/{}'.format(a['href']))
  data = r.text
  soup = BeautifulSoup(data, features="html.parser") 
  competition = soup.find('h1', {'class':'competition-title'})
  match_dict[competition.encode_contents().encode('utf-8')] = {}
  matches = soup.findAll('dl', {'class':'matches'})
  for m in matches:
    day = m.find_previous_sibling('h3')
    matchdate = day.encode_contents()#Saturday 4 May
    if matchdate == "Today": 
      matchdateobj = datetime.today()
    else:
      matchdateobj = datetime.strptime('{0} {1}'.format(matchdate, thisyear),'%A %d %B %Y')
    if matchdateobj < datetime.today() : 
      matchdateobj =  matchdateobj.replace(year= int(thisyear)+1)
    match_dict[competition.encode_contents()][matchdateobj.strftime('%Y-%m-%d')] = []
    home = m.find('span', {'class':'home-side'}).find('img')['alt'].encode('utf-8')
    away = m.find('span', {'class':'away-side'}).find('img')['alt'].encode('utf-8')
    time = m.find('span', {'class': 'match-time'})
    match_dict[competition.encode_contents()][matchdateobj.strftime('%Y-%m-%d')].append('{0} vs {1} {2} {3}'.format(home, away, matchdateobj.strftime('%Y-%m-%d'), time.encode_contents()))
print match_dict
  

