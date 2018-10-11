bitrate_max=8000#kbps
bitrate_min=1000#kbps
searchterm = 'wales'
time_to_record = 1 #minutes

import praw, re, sys, psutil, os
import requests, hashlib, json, time, subprocess
import acestream_to_http_tc
from datetime import datetime
from MediaInfo import MediaInfo
pid = str(os.getpid())
pidfile = "/tmp/mydaemon.pid"

#only allow 1 copy of script at any time
if os.path.isfile(pidfile):
    print "%s already exists, exiting" % pidfile
    sys.exit()
file(pidfile, 'w').write(pid)

try:
  dir_path = os.path.dirname(os.path.realpath(__file__))+"/www"
  enginerunning = False
  if "acestreamengine" in (p.name() for p in psutil.process_iter()): 
    enginerunning=True
  if enginerunning == False:#start engine
    print "Start engine"
    acestream_to_http_tc.startengine(dir_path)
    
    
  reddit = praw.Reddit(client_id='eSLpkm36H4FelA',
                      client_secret='NM50GW0wQZ63Wju_n-8lgP4N0LE',
                      user_agent='my user agent')

  matches={}
  match_title=""
  subreddit = reddit.subreddit('soccerstreams')
  for submission in reddit.subreddit('soccerstreams').new(limit=30):#get 10 newest posts
    if ((time.time ()- submission.created_utc)) < (24*3600):#only search posts last 24 hours
      if re.search(r'vs', submission.title, re.IGNORECASE):
        if re.search(searchterm, submission.title, re.IGNORECASE):
          match_title = submission.title
          if submission.title not in matches:
            matches[submission.title] = {}
          for comment in submission.comments:
            if re.search("acestream",comment.body):
              acestreams = re.findall(r'acestream://([0-9a-z]+)', comment.body)
              for s in acestreams:
                if s not in matches[submission.title]:
                  matches[submission.title].update({s:[submission.created_utc, comment.author_flair_text]})
                  
  if len(matches)==0:
    print "No match found"
    sys.exit()
  print match_title
  print len(matches[match_title])
  post_match_start = re.search("\[([0-9]*):([0-9]*).*?\]",match_title)
  
  today = datetime.utcnow()
  time_of_match = today.replace(hour=int(post_match_start.group(1)), minute=int(post_match_start.group(2)), second=0, microsecond=0)
  time_difference = time_of_match - datetime.utcnow()
  #print time_difference
  seconds_to_match = time_difference.days*86400 + time_difference.seconds
  if seconds_to_match < -1000000 or seconds_to_match > 600:
    print "Not right time to start"
    sys.exit()
  
  newmatches={}
  for match in matches:
    if len(matches[match])>0: #only if stream attached
      #print matches[match], len(matches[match])
      for stream_pid in matches[match]:
        verified_streamer =  False
        if matches[match][stream_pid][1] is not None:
          if re.search("verified", matches[match][stream_pid][1], re.IGNORECASE): #1st element is flair text
            verified_streamer = True
        #print stream_pid
        stream_uid = hashlib.sha1(stream_pid).hexdigest()
        #try playing stream
        r = requests.get('http://127.0.0.1:6878/ace/getstream?format=json&sid={0}&id={1}'.format(stream_uid, stream_pid))
        response = json.loads(r.text)
        #print r.text
        if 'response' in response:
          if response['response'] is not None:
            time.sleep(3)
            r = requests.get(response['response']['stat_url'])
            response_stream = json.loads(r.text)
            #print r.text
            if 'response' in response_stream:
              if 'status' in response_stream['response']:
                if response_stream['response']['status']=='dl':
                  #check is playing, if so transcode 30 seconds and investigate
                  time.sleep(2)
                  for process in psutil.process_iter(): 
                    if '/usr/bin/vlc' in process.cmdline():
                      process.kill()
                  subprocess.Popen(["cvlc", response['response']['playback_url'], "--sout", "#std{access=file,mux=ts,dst='/tmp/acestream.mkv'}"])
                  time.sleep(30)#30s sample video
                  for process in psutil.process_iter(): 
                    if '/usr/bin/vlc' in process.cmdline():
                      process.kill()
                  info = MediaInfo(filename = '/tmp/acestream.mkv')
                  language=""
                  try:
                    infoData = info.getInfo()
                    proc = subprocess.Popen(["/usr/bin/mediainfo", "/tmp/acestream.mkv"], stdout=subprocess.PIPE)
                    o=proc.stdout.read()
                    for l in o.split("\n"): 
                      if re.match("Language", l): language = l.split(":")[1][1:]
                    #print infoData             
                  except:
                    infoData = {}
                  if 'bitrate' not in infoData: score=0
                  else:
                    score = int(response_stream['response']['peers'])/100.0 * int(response_stream['response']['speed_down'])*8.0/float(infoData['bitrate'])*1000
                  stream_data = [int(time.time()), response_stream['response']['status'], response_stream['response']['speed_down'], response_stream['response']['peers'], infoData, language, score, verified_streamer]
                  newmatches[match]={}
                  newmatches[match][stream_pid] = stream_data
            r = requests.get(response['response']['command_url']+"?method=stop")
          time.sleep(2)
          

  #newmatches = {u'[18:45 GMT] Poland vs Portugal': {u'5b4ed4f8570ac0af23fc5dc3151b5af61c8b4dcb': [1539287183, u'dl', 3339, 21, {'videoFrameRate': u'25.000', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'1153', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioCodecProfile': u'LC', 'haveVideo': 1, 'videoWidth': 1920, 'videoDuration': '46.12', 'audioChannel': u'2', 'fileSize': u'41063336', 'duration': '46.306', 'haveAudio': 1, 'audioSamplingRate': u'44100', 'audioDuration': '46.393', 'bitrate': u'7079142', 'videoCodecProfile': u'High@L4.1', 'audioCodec': u'AAC', 'videoHeight': 1080}, 'Polish', 0.7924011130162384, False]}}
  print newmatches
  possibles={}
  for match in newmatches:
    matchname = match
    for stream in newmatches[match]:
      if 'bitrate' in newmatches[match][stream][4]:
        if float(newmatches[match][stream][4]['bitrate'])/1000>bitrate_min and float(newmatches[match][stream][4]['bitrate'])/1000<bitrate_max:#order by number of peers
          print stream, newmatches[match][stream][4]['bitrate'], newmatches[match][stream][2], newmatches[match][stream][3], newmatches[match][stream][4]['videoWidth']
          number_of_peers = newmatches[match][stream][3]
          try:
            if verified_streamer: number_of_peers = number_of_peers * 2 #weight for verified streamers
          except:
            pass
          possibles[stream] = number_of_peers
        
  #print possibles
  beststream=[]
  for key, value in sorted(possibles.iteritems(), key=lambda (k,v): (v,k)):
      beststream.append(key)
  try:
    chosenstream = beststream.pop()
  except:
    print "No streams found"
    sys.exit()

  print matchname, chosenstream

  #tune in stream and kill after allotted time

  stream_uid = hashlib.sha1(chosenstream).hexdigest()
  r = requests.get('http://127.0.0.1:6878/ace/getstream?format=json&sid={0}&id={1}'.format(stream_uid, chosenstream))
  response = json.loads(r.text)

  if 'response' in response:
    if response['response'] is not None:
      out = json.loads(r.text)
      out['response']['stream_pid'] = chosenstream
      with open('/tmp/pid_stat_url', 'w') as f: f.write(json.dumps(out))
      time.sleep(3)
      r = requests.get(response['response']['stat_url'])
      response_stream = json.loads(r.text)
      if 'response' in response_stream:
        if 'status' in response_stream['response']:
          if response_stream['response']['status']=='dl':
            pid_stat_url = [chosenstream, response['response']['stat_url'], response['response']['playback_url'], r.text, chosenstream]
            #check is playing, if so transcode approriate length
            time.sleep(2)
            subprocess.Popen(["cvlc", response['response']['playback_url'], "--sout", "#std{access=file,mux=ts,dst='/tmp/acestream.mkv'}"])
            time.sleep(time_to_record*60)
  for process in psutil.process_iter(): 
    if '/usr/bin/vlc' in process.cmdline():
      process.kill()
  acestream_to_http_tc.ffmpeg_transcode("/tmp/acestream.mkv", dir_path+"/listings/"+matchname+".mp4")
  with open('/tmp/pid_stat_url', 'w') as f: f.write(json.dumps(None))

finally:
  os.unlink(pidfile)
  if os.path.isfile('/tmp/pid_stat_url'):
    os.unlink('/tmp/pid_stat_url')
