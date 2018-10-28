import time, datetime, os, json, urllib2, re
  
def getreplies(data):
  verified = False
  try:
    if data['author_flair_text'] is not None:
      if re.search('Verified', data['author_flair_text'], re.IGNORECASE): verified = True
  except:
    pass
  try:
    acestreams = re.findall(r'[\[\]\w\s]*acestream://[\w]+[\[\]\w\s]*\n', data['body'])
    #acestreams = re.findall(r'acestream://([0-9a-z]+)', data['body'])
    for a in acestreams:
      links.append({'acestream':a, 'verified':verified})
  except:
    pass
  try:
    if data['replies']!="":
      for reply in data['replies']['data']['children']:
        getreplies(reply['data'])
  except:
    pass

def getlinks(data):
  url = data['data']['children'][0]['data']['url']+'search.json'
  print url
  request = urllib2.Request(url)
  request.add_header('User-agent', 'Kodi soccerstreams bot 0.1')
  result = urllib2.urlopen(request)
  reply = result.read()
  return json.loads(reply)

def findstream(links):
  preferred_stream = ""
  for l in links:
    line = l['acestream'].replace("\n",'').strip()
    if l['verified']:
      if re.search('720p|HD',line,re.IGNORECASE):#verified 720p
        acestreams = re.findall(r'acestream://([0-9a-z]+)',line)
        if acestreams: preferred_stream = acestreams[0]
  if preferred_stream == "":
    for l in links:
      line = l['acestream'].replace("\n",'').strip()
      if re.search('720p|HD',line,re.IGNORECASE):#verified 720p
        acestreams = re.findall(r'acestream://([0-9a-z]+)',line)
        preferred_stream = acestreams[0]
  return preferred_stream

dir_path = os.path.dirname(os.path.realpath(__file__))
blacklisted_streams = []

while True:
  print "loop"
  #crawl every 1 minute to see if needs to start recording- start 5 mins beforehand
  with open(dir_path+'/torecord.json') as f:
    torecord = json.load(f)
  for m in torecord:
    mtime = datetime.datetime.strptime(m[-16:], '%Y-%m-%d %H:%M')
    unix_start = time.mktime(mtime.timetuple())
    if ((unix_start - 300) < time.time()) and (time.time() - unix_start < (3*3600)):# if 5 mins before start time and not more than 3 hours ago
      #search r/soccerstreams for streams
      teams = re.sub(r"[A-Z]{2,10}",'',m[:-16])#remove all capital words e.g. AFC
      teams = teams.split("vs")
      print m
      query = "{}%20AND%20{}".format(teams[0].strip().split(" ")[0], teams[1].strip().split(" ")[0])
      print query
      request = urllib2.Request('https://www.reddit.com/r/soccerstreams/search.json?sort=new&restrict_sr=on&q={0}'.format(query))
      request.add_header('User-agent', 'Kodi soccerstreams bot 0.1')
      try:
        result = urllib2.urlopen(request)
      except:#error in fetch (e.g. 503 unavailable), back to top of loop
        continue
      data = json.loads(result.read())
      if len(data['data']['children'])>0:
        data = getlinks(data)
        links = []
        print data
        for c in data[1]['data']['children']:
          getreplies(c['data'])#recursively fetch replies
        print links
        #find preferred stream - verified first, then 720p then 1080p then whatever
        preferred_stream = findstream(links)
        print preferred_stream
      else:
        print "not found"
  time.sleep(60)
  
  



#(function)

#check if engine running, if not running then start

#start stream and write pid file

#(function)check qualaity of stream- if buffering or <200kbps 
#then increment part number and find another stream

#start transcoding - MATCH NAME-PART NUMBER.mp4 and live stream
#every minute check quality of stream

#5+45+15+45+30 - minumum 140minues
#after 3 hours stop recording
