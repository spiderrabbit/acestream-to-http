from bs4 import BeautifulSoup
import requests,sys, datetime,json

def getmatches(startdate):
  funcdateobj = datetime.datetime.strptime(startdate,'%Y-%m-%d')
  funcdatestr = funcdateobj.strftime('%Y/%b/%d')
  r = requests.get("https://www.theguardian.com/football/fixtures/more/{0}".format(funcdatestr))
  data = r.text
  soup = BeautifulSoup(data, features="html.parser")

  match_dict = {}

  mydivs = soup.findAll('div', {"class": "football-matches__day"})
  for div in mydivs:
    date = div.findAll('div', {"class": "date-divider"})
    dateobj = datetime.datetime.strptime(date[0].encode_contents(),'%A %d %B %Y')
    datestr = dateobj.strftime('%Y-%m-%d')
    leagues = div.findAll('div', {"class": "football-table__container"})
    for league in leagues:
      lstr = league.find('caption', {'class': 'table__caption'}).find('a')
      if lstr.encode_contents() not in match_dict:
        match_dict[lstr.encode_contents()] = {}
      if datestr not in match_dict[lstr.encode_contents()]:
        match_dict[lstr.encode_contents()][datestr] = []
      matches = league.findAll('table', {"class": "table--football"})
      for m in matches:
        body = m.find('tbody')
        tr = body.findAll('tr')
        for row in tr:
          matchlist = []
          td = row.findAll('td')
          for t in td:
            time = t.find('time')
            if time is not None:
              matchlist.append(time.encode_contents().strip('\n'))
            team = t.findAll('span', {'class': "team-name__long"})
            for tm in team: 
              tstr = tm.encode_contents()
              if tstr != '':
                matchlist.append(tstr)
          if len(matchlist)==3:
            match_dict[lstr.encode_contents()][datestr].append('{0} vs {1} {2} {3}'.format(matchlist[1], matchlist[2], datestr, matchlist[0]))
          #print t.encode_contents()
  print json.dumps(match_dict)

getmatches(sys.argv[1])
