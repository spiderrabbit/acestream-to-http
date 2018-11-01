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
    acestreams = re.findall(r'[\[\]\w\s]*acestream://[\w]{40}[\[\]\w\s]*', data['body'])
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
  request = urllib2.Request(url+'search.json')
  request.add_header('User-agent', 'Kodi soccerstreams bot 0.1')
  result = urllib2.urlopen(request)
  reply = result.read()
  return json.loads(reply)

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
    for preferred_format in ['720p', 'HD', '1080', 'SD', 'acestream']: 
      for l in links:
        if preferred_stream == '':
          line = l['acestream'].replace("\n",'').strip()
          if l['verified'] == verified :
            if re.search(preferred_format,line,re.IGNORECASE):#
              acestreams = re.findall(r'acestream://([0-9a-z]+)',line)
              if acestreams: 
                if preferred_stream not in blacklisted_streams:
                  preferred_stream = acestreams[0]
  return preferred_stream

matchlink = ''
dir_path = os.path.dirname(os.path.realpath(__file__))
blacklisted_streams = []
started_recording = False
links = []
recording_part = 1
while True:
  print "loop"  #crawl every 1 minute to see if needs to start recording- start 5 mins beforehand
  if started_recording == False:
    with open(dir_path+'/torecord.json') as f: #load matches to record
      torecord = json.load(f)
    for m in torecord: #iterate through each scheduled recording
      mtime = datetime.datetime.strptime(m[-16:], '%Y-%m-%d %H:%M')
      unix_start = time.mktime(mtime.timetuple())#get start time of matches
      # if it is now more than 5 mins before start time and not more than 3 hours ago
      if ((unix_start - 300) < time.time()) and (time.time() - unix_start < (3*3600)):
        #parse team string data
        teams = re.sub(r"[A-Z]{2,10}",'',m[:-16])#remove all capital words e.g. AFC
        teams = teams.split("vs")
        query = "{}%20AND%20{}".format(teams[0].strip().split(" ")[0], teams[1].strip().split(" ")[0])
        #search r/soccerstreams for streams
        request = urllib2.Request('https://www.reddit.com/r/soccerstreams/search.json?sort=new&restrict_sr=on&q={0}'.format(query))
        request.add_header('User-agent', 'Kodi soccerstreams bot 0.1')
        data = {'data':{'children':''}}#initialise data variable
        try:
          result = urllib2.urlopen(request)
          data = json.loads(result.read())
        except:#error in fetch (e.g. 503 unavailable), back to top of while loop
          continue
        if len(data['data']['children'])>0:#found a match
          matchlink = data['data']['children'][0]['data']['url']
          preferred_stream = findstream(matchlink)
          print preferred_stream
          playstream.playstream(preferred_stream, '{0}_{1}'.format(m, recording_part))
          started_recording = True
        else:
          print "not found"# NEED TO ADD ALTERNATIVE QUERIES TO IMPROVE SEARCH
  else:#is recording started_recording == True:
    if time.time() - unix_start > (3*3600):#recording for 3 hours - stop
      acestream_to_http_tc.stopengine(dir_path)
      started_recording = False
      blacklisted_streams = []
      recording_part = 1
      print "recording finished"
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
            if data is not None:
              if 'status' in data['response']:
                if data['response']['status']=='dl' and data['response']['speed_down']>100:
                  restart_recording = False
          except urllib2.URLError:
            engine_failure = True
      if restart_recording:
        if engine_failure == False:
          blacklisted_streams.append(preferred_stream)#only blacklist non working streams
        print "restart"
        preferred_stream = findstream(matchlink)
        recording_part += 1 
        playstream.playstream(preferred_stream, '{0}_{1}'.format(m, recording_part))
      else:
        print "OK to carry on"
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
