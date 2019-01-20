import time, datetime, os, json, urllib2, re
import acestream_to_http_tc
import playstream
  
def getreplies(data):
  global links
  verified = False
  try:
    if data['author_flair_text'] is not None:
      if re.search('Verified', data['author_flair_text'], re.IGNORECASE): verified = True
  except:
    pass
  try:
    acestreams = re.findall(r'[^\n]*acestream://[\w]{40}[^\n]*', data['body'])
    #acestreams = re.findall(r'[\[\]\w\s]*acestream://[\w]{40}[\[\]\w\s]*', data['body'])
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

def getlinks(url):
  request = urllib2.Request(url+'search.json?sort=top')
  request.add_header('User-agent', 'Kodi soccerstreams bot 0.1')
  result = urllib2.urlopen(request)
  reply = result.read()
  return json.loads(reply)

def findmatch(searchquery):
  #search r/soccerstreams for streams
  #request = urllib2.Request('https://www.reddit.com/r/soccerstreams/search.json?sort=new&restrict_sr=on&limit=1&q={0}'.format(query))
  request = urllib2.Request('https://www.reddit.com/r/soccerstreams_pl/search.json?sort=new&restrict_sr=on&limit=1&q={0}'.format(query))
  request.add_header('User-agent', 'Kodi soccerstreams bot 0.1')
  data = {'data':{'children':''}}#initialise data variable
  try:
    result = urllib2.urlopen(request)
    data = json.loads(result.read())
  except:#error in fetch (e.g. 503 unavailable), back to top of while loop
    pass
  return data

def findstream(matchlink):
  global links, blacklisted_streams
  data = getlinks(matchlink)
  links = []
  for c in data[1]['data']['children']:
    getreplies(c['data'])#recursively fetch replies
  #find preferred stream - verified first, then 720p then 1080p then whatever
  preferred_stream = ''
  #search verified streamers first
  for verified in [True, False]:
    #search preferred language 
    for language in ['[EN]','']:
      for preferred_format in ['1080', '720p', 'HD', 'SD', 'acestream']: 
        for l in links:#iterate through links
          if re.match(language,l['acestream']):
              if l['verified'] == verified :
                line = l['acestream'].replace("\n",'').strip()
                if re.search(preferred_format,line,re.IGNORECASE):#
                  acestreams = re.findall(r'acestream://([0-9a-z]+)',line)
                  if acestreams: 
                    if preferred_stream not in blacklisted_streams:
                      if preferred_stream=='': preferred_stream = acestreams[0]
  
  
  #for verified in [True, False]:
    #for preferred_format in ['1080', '720p', 'HD', 'SD', 'acestream']: 
      #for l in links:
        #if preferred_stream == '':
          #line = l['acestream'].replace("\n",'').strip()
          #if l['verified'] == verified :
            #if re.search(preferred_format,line,re.IGNORECASE):#
              #acestreams = re.findall(r'acestream://([0-9a-z]+)',line)
              #if acestreams: 
                #if preferred_stream not in blacklisted_streams:
                  #preferred_stream = acestreams[0]
  return preferred_stream

matchlink = ''
dir_path = os.path.dirname(os.path.realpath(__file__))
blacklisted_streams = []
started_recording = False
links = []
recording_part = 1
with open('/tmp/current_recording', 'w+') as f: f.write('')
while True:
  #print "loop"  #crawl every 1 minute to see if needs to start recording- start 5 mins beforehand
  if started_recording == False:
    with open(dir_path+'/torecord.json') as f: #load matches to record
      torecord = json.load(f)
    if torecord is not None:
      for m in torecord: #iterate through each scheduled recording
        mtime = datetime.datetime.strptime(m[-16:], '%Y-%m-%d %H:%M')
        unix_start = time.mktime(mtime.timetuple())#get start time of matches
        # if it is now more than 5 mins before start time and not more than 3 hours ago
        if ((unix_start - 300) < time.time()) and (time.time() - unix_start < (3*3600)):
          #parse team string data
          teams = re.sub(r"[A-Z]{2,10}",'',m[:-16])#remove all capital words e.g. AFC
          teams = teams.split("vs")
          hometeam = teams[0].strip().split(" ")[0]
          awayteam = teams[1].strip().split(" ")[0]
          if len(awayteam) == 0: query = hometeam
          elif len(hometeam) == 0: query = awayteam
          else: query = "{}%20AND%20{}".format(hometeam, awayteam)
          data = findmatch(query) #find via both teams
          if len(data['data']['children'])==0:#nothing found
            query = "{}%20OR%20{}".format(hometeam, awayteam)
            data = findmatch(query)# find via either team
          if len(data['data']['children'])>0:#found a match
            print str(datetime.datetime.now()),"found via {}".format(query)
            matchlink = data['data']['children'][0]['data']['url']
            preferred_stream = findstream(matchlink)
            print str(datetime.datetime.now()),preferred_stream
            playstream.playstream(preferred_stream, '{0}_{1}'.format(m, recording_part))
            started_recording = True
            break
          else:
            print str(datetime.datetime.now()),"{0} not found via {1}".format(m, query)# NEED TO ADD ALTERNATIVE QUERIES TO IMPROVE SEARCH
  else:#is recording started_recording == True:
    if time.time() - unix_start > (3*3600):#recording for 3 hours - stop
      acestream_to_http_tc.stopengine()
      #process file
      acestream_to_http_tc.ffmpeg_transcode('{0}_{1}'.format(m, recording_part))
      started_recording = False
      blacklisted_streams = []
      recording_part = 1
      print str(datetime.datetime.now()),"recording finished"
    else: #check is recording OK
      restart_recording = True
      engine_failure = False
      status = acestream_to_http_tc.engine_status()
      if status is not None:
        if 'stat_url' in status['response']:
          stat_url=status['response']['stat_url']
          request = urllib2.Request(stat_url)
          try:
            result = urllib2.urlopen(request)
            data = json.loads(result.read())          #{u'response': {u'status': u'dl', u'uploaded': 2555904, u'speed_down': 449, u'speed_up': 17, u'playback_session_id': u'faafb1af12aa9b7d161c1648eb1ce95bda1a7043', u'peers': 48, u'total_progress': 0, u'downloaded': 33521664}, u'error': None}
            if data is not None and 'response' in data:
              if data['response'] is not None and 'status' in data['response']:
                if data['response']['status']=='dl' and data['response']['speed_down']>100:
                  restart_recording = False
                else:
                  print str(datetime.datetime.now()),"Stream Failure"
                  print str(datetime.datetime.now()),data
          except urllib2.URLError:
            engine_failure = True
            print str(datetime.datetime.now()),"Engine failure: urllib2.URLError"
      if restart_recording:
        if engine_failure == False:#only blacklist non working streams, not if engine failed
          blacklisted_streams.append(preferred_stream)
          print str(datetime.datetime.now()),"Blacklisted: ", blacklisted_streams
        print str(datetime.datetime.now()),"restart"
        #transcode stream that has stopped
        acestream_to_http_tc.ffmpeg_transcode('{0}_{1}'.format(m, recording_part))
        recording_part += 1 #increment recording name
        started_recording = False #search again for stream
      else:
        print str(datetime.datetime.now()),"OK to carry on"
  time.sleep(60)

