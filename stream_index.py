import praw, re, sys, psutil, os
import requests, hashlib, json, time, subprocess
from MediaInfo import MediaInfo
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path+'/public/streams/matches.json', 'r') as f: matches = json.loads(f.read())

reddit = praw.Reddit(client_id='eSLpkm36H4FelA',
                     client_secret='NM50GW0wQZ63Wju_n-8lgP4N0LE',
                     user_agent='my user agent')
streams = []
subreddit = reddit.subreddit('soccerstreams')
for submission in reddit.subreddit('soccerstreams').new(limit=30):#get 10 newest posts
  if ((time.time ()- submission.created_utc)) < (24*3600):#only search posts last 24 hours
    if re.search(r'vs', submission.title, re.IGNORECASE):
      if submission.title not in matches:
        matches[submission.title] = {}
      print submission.title, submission.created_utc
      for comment in submission.comments:
        if re.search("acestream",comment.body):
          acestreams = re.findall(r'acestream://([0-9a-z]+)', comment.body)
          for s in acestreams:
            if s not in matches[submission.title]:
              matches[submission.title].update({s:[submission.created_utc]})
#with open('matches.json', 'w') as f: f.write(json.dumps(matches))

newmatches={}
for match in matches:
  if len(matches[match])>0: #only if stream attached
    #print matches[match], len(matches[match])
    for stream_pid in matches[match]:
      if len(matches[match][stream_pid])>6:#not found in submitted posts, is a historic stream
        link_posted = matches[match][stream_pid][7]
      else:
        link_posted = matches[match][stream_pid][0]#is a new stream
      #print stream_pid
      stream_uid = hashlib.sha1(stream_pid).hexdigest()
      r = requests.get('http://127.0.0.1:6878/ace/getstream?format=json&sid={0}&id={1}'.format(stream_uid, stream_pid))
      response = json.loads(r.text)
      #print r.text
      if 'response' in response:
        if response['response'] is not None:
          time.sleep(15)
          r = requests.get(response['response']['stat_url'])
          response_stream = json.loads(r.text)
          #print r.text
          if 'response' in response_stream:
            if 'status' in response_stream['response']:
              if response_stream['response']['status']=='dl':
                #check is playing, if so transcode 30 seconds and investigate
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
                stream_data = [int(time.time()), response_stream['response']['status'], response_stream['response']['speed_down'], response_stream['response']['peers'], infoData, language, score, link_posted]
                if match not in newmatches:
                  newmatches[match]={}
                if stream_pid not in newmatches[match]:
                  newmatches[match].update({stream_pid:[]})
                newmatches[match][stream_pid] = stream_data
          r = requests.get(response['response']['command_url']+"?method=stop")
        time.sleep(5)
#print matches
with open(dir_path+'/public/streams/matches.json', 'w') as f: f.write(json.dumps(newmatches))

#write stream history
for m in newmatches:
  for s in newmatches[m]:
    if os.path.exists(dir_path+'/public/streams/%s' % s):
      with open(dir_path+'/public/streams/%s' % s, 'r') as f: stream_history = json.loads(f.read())
      stream_history.append(newmatches[m][s])
    else:
      stream_history = [newmatches[m][s]]
    with open(dir_path+'/public/streams/%s' % s, 'w') as f: f.write(json.dumps(stream_history))
