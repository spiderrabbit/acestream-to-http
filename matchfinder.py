bitrate_max=5000
bitrate_min=1000

import praw, re, sys, psutil, os
import requests, hashlib, json, time, subprocess
from MediaInfo import MediaInfo

#reddit = praw.Reddit(client_id='eSLpkm36H4FelA',
                     #client_secret='NM50GW0wQZ63Wju_n-8lgP4N0LE',
                     #user_agent='my user agent')

#matches={}
#subreddit = reddit.subreddit('soccerstreams')
#for submission in reddit.subreddit('soccerstreams').new(limit=30):#get 10 newest posts
  #if ((time.time ()- submission.created_utc)) < (24*3600):#only search posts last 24 hours
    #if re.search(r'vs', submission.title, re.IGNORECASE):
      #if re.search('manchester united', submission.title, re.IGNORECASE):
        #if submission.title not in matches:
          #matches[submission.title] = {}
        #for comment in submission.comments:
          #if re.search("acestream",comment.body):
            #acestreams = re.findall(r'acestream://([0-9a-z]+)', comment.body)
            #for s in acestreams:
              #if s not in matches[submission.title]:
                #matches[submission.title].update({s:[submission.created_utc]})

#print matches
#newmatches={}
#for match in matches:
  #if len(matches[match])>0: #only if stream attached
    ##print matches[match], len(matches[match])
    #for stream_pid in matches[match]:
      #if len(matches[match][stream_pid])>6:#not found in submitted posts, is a historic stream
        #link_posted = matches[match][stream_pid][7]
      #else:
        #link_posted = matches[match][stream_pid][0]#is a new stream
      ##print stream_pid
      #stream_uid = hashlib.sha1(stream_pid).hexdigest()
      #r = requests.get('http://127.0.0.1:6878/ace/getstream?format=json&sid={0}&id={1}'.format(stream_uid, stream_pid))
      #response = json.loads(r.text)
      ##print r.text
      #if 'response' in response:
        #if response['response'] is not None:
          #time.sleep(3)
          #r = requests.get(response['response']['stat_url'])
          #response_stream = json.loads(r.text)
          ##print r.text
          #if 'response' in response_stream:
            #if 'status' in response_stream['response']:
              #if response_stream['response']['status']=='dl':
                ##check is playing, if so transcode 30 seconds and investigate
                #time.sleep(2)
                #subprocess.Popen(["cvlc", response['response']['playback_url'], "--sout", "#std{access=file,mux=ts,dst='/tmp/acestream.mkv'}"])
                #time.sleep(30)#30s sample video
                #for process in psutil.process_iter(): 
                  #if '/usr/bin/vlc' in process.cmdline():
                    #process.kill()
                #info = MediaInfo(filename = '/tmp/acestream.mkv')
                #language=""
                #try:
                  #infoData = info.getInfo()
                  #proc = subprocess.Popen(["/usr/bin/mediainfo", "/tmp/acestream.mkv"], stdout=subprocess.PIPE)
                  #o=proc.stdout.read()
                  #for l in o.split("\n"): 
                    #if re.match("Language", l): language = l.split(":")[1][1:]
                  ##print infoData             
                #except:
                  #infoData = {}
                #if 'bitrate' not in infoData: score=0
                #else:
                  #score = int(response_stream['response']['peers'])/100.0 * int(response_stream['response']['speed_down'])*8.0/float(infoData['bitrate'])*1000
                #stream_data = [int(time.time()), response_stream['response']['status'], response_stream['response']['speed_down'], response_stream['response']['peers'], infoData, language, score, link_posted]
                #if match not in newmatches:
                  #newmatches[match]={}
                #if stream_pid not in newmatches[match]:
                  #newmatches[match].update({stream_pid:[]})
                #newmatches[match][stream_pid] = stream_data
          #r = requests.get(response['response']['command_url']+"?method=stop")
        #time.sleep(2)
        
newmatches={u'[19:00 GMT] Manchester United vs Valencia': {u'f8f4afedb7e9ff99ae9f0b3d1ae8bc69443396b9': [1538504072, u'dl', 1841, 33, {'videoFrameRate': u'59.940', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'2665', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioCodecProfile': u'LC', 'haveVideo': 1, 'videoWidth': 1280, 'videoDuration': '44.461', 'audioChannel': u'2', 'fileSize': u'25986676', 'duration': '44.425', 'haveAudio': 1, 'audioSamplingRate': u'48000', 'audioDuration': '46.549', 'bitrate': u'4489545', 'videoCodecProfile': u'High@L4.1', 'audioCodec': u'AAC', 'videoHeight': 720}, '', 1.082568500816898, 1538501464.0], u'82cdfe0781b7b651564b88c4ac16f2f1412547d4': [1538504149, u'dl', 1190, 58, {'videoAspectRatio': u'1.778', 'audioCodecProfile': u'LC', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'haveVideo': 1, 'videoWidth': 1280, 'videoDuration': '33.979', 'audioChannel': u'2', 'fileSize': u'21774912', 'duration': '33.97', 'haveAudio': 1, 'audioSamplingRate': u'48000', 'audioDuration': '34.369', 'bitrate': u'5124955', 'videoCodecProfile': u'Main@L3.1', 'audioCodec': u'AAC', 'videoHeight': 720}, '', 1.0773948259057884, 1538501464.0], u'f48bd0dc0a3514c6a8f071abeb11c0f4df6976e5': [1538504495, u'dl', 518, 8, {'videoFrameRate': u'59.940', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'2406', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioCodecProfile': u'LC', 'haveVideo': 1, 'videoWidth': 768, 'videoDuration': '40.14', 'audioChannel': u'2', 'fileSize': u'8141152', 'duration': '40.114', 'haveAudio': 1, 'audioSamplingRate': u'48000', 'audioDuration': '40.405', 'bitrate': u'1623264', 'videoCodecProfile': u'Main@L5', 'audioCodec': u'AAC', 'videoHeight': 432}, '', 0.20423048869438365, 1538501464.0], u'2304e9fb94eb3533b02a6c9907a18f65c1107e71': [1538504110, u'dl', 1813, 17, {'videoFrameRate': u'25.000', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'325', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioCodecProfile': u'LC', 'haveVideo': 1, 'videoWidth': 1920, 'videoDuration': '13.0', 'audioChannel': u'2', 'fileSize': u'11581364', 'duration': '13.302', 'haveAudio': 1, 'audioSamplingRate': u'44100', 'audioDuration': '13.374', 'bitrate': u'6893644', 'videoCodecProfile': u'High@L4', 'audioCodec': u'AAC', 'videoHeight': 1080}, 'English / English', 0.3576744026816587, 1538501464.0], u'15f227a91b63a803d97d2bcb048721df88ce4c35': [1538504226, u'dl', 3117, 5, {'videoFrameRate': u'50.000', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'1855', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioCodecProfile': u'LC', 'haveVideo': 1, 'videoWidth': 1920, 'videoDuration': '37.092', 'audioChannel': u'2', 'fileSize': u'35025528', 'duration': '5.936', 'haveAudio': 1, 'audioSamplingRate': u'48000', 'audioDuration': '4392.925', 'bitrate': u'6439743', 'videoCodecProfile': u'High@L4.2', 'audioCodec': u'AAC', 'videoHeight': 1080}, '', 0.193610210842265, 1538501464.0], u'f4b452a0680eb1467d7ccc30d4678e7792250f24': [1538504264, u'dl', 939, 94, {'videoFrameRate': u'29.970', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'1117', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioBitrate': u'96000', 'videoBitrate': u'1676563', 'audioCodecProfile': u'Joint stereo', 'haveVideo': 1, 'videoWidth': 1280, 'videoDuration': '37.269', 'audioChannel': u'2', 'fileSize': u'10375344', 'duration': '37.15', 'haveAudio': 1, 'audioSamplingRate': u'44100', 'audioDuration': '44.669', 'bitrate': u'1865730', 'videoCodecProfile': u'High@L3.1', 'audioCodec': u'MPA1L3', 'videoHeight': 720}, '', 3.7847276937177403, 1538501464.0], u'1604a494095c9d6113ee706d4976cead9ccc4f09': [1538504302, u'dl', 1070, 1, {'videoAspectRatio': u'1.778', 'audioCodecProfile': u'LC', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'haveVideo': 1, 'videoWidth': 960, 'videoDuration': '47.6', 'audioChannel': u'2', 'fileSize': u'9591948', 'duration': '47.814', 'haveAudio': 1, 'audioSamplingRate': u'32000', 'audioDuration': '49.408', 'bitrate': u'1554961', 'videoCodecProfile': u'Main@L3.1', 'audioCodec': u'AAC', 'videoHeight': 540}, 'Arabic', 0.055049612176768424, 1538501464.0], u'f418a92b223b11b290b9b6a64fefbe7718b1bc9b': [1538504340, u'dl', 2883, 29, {'videoAspectRatio': u'1.778', 'audioCodecProfile': u'LC', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'haveVideo': 1, 'videoWidth': 1920, 'videoDuration': '46.913', 'audioChannel': u'2', 'fileSize': u'31352572', 'duration': '46.93', 'haveAudio': 1, 'audioSamplingRate': u'48000', 'audioDuration': '47.146', 'bitrate': u'5342602', 'videoCodecProfile': u'Main@L4.2', 'audioCodec': u'AAC', 'videoHeight': 1080}, '', 1.2519293033619197, 1538501464.0], u'45db815ca746a94b73ffe0b26cf2caa287691cc6': [1538504380, u'dl', 2360, 38, {'videoFrameRate': u'50.000', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'2291', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioCodecProfile': u'LC', 'haveVideo': 1, 'videoWidth': 1920, 'videoDuration': '45.82', 'audioChannel': u'2', 'fileSize': u'39451048', 'duration': '45.789', 'haveAudio': 1, 'audioSamplingRate': u'48000', 'audioDuration': '45.824', 'bitrate': u'6891248', 'videoCodecProfile': u'High@L4.2', 'audioCodec': u'AAC', 'videoHeight': 1080}, '', 1.041088638806788, 1538501464.0], u'a586e7b22779b3846dfeed626fa888d064dfda95': [1538504418, u'dl', 1715, 39, {'videoAspectRatio': u'1.778', 'audioCodecProfile': u'LC', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'haveVideo': 1, 'videoWidth': 1920, 'videoDuration': '41.4', 'audioChannel': u'2', 'fileSize': u'27806328', 'duration': '41.328', 'haveAudio': 1, 'audioSamplingRate': u'48000', 'audioDuration': '41.429', 'bitrate': u'5374954', 'videoCodecProfile': u'High@L4.2', 'audioCodec': u'AAC', 'videoHeight': 1080}, '', 0.9955061940995216, 1538501464.0], u'7d3057f6b27217683e112cc5ed3539e5f0474b4c': [1538504457, u'dl', 1063, 41, {'videoFrameRate': u'29.970', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'1153', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioBitrate': u'96000', 'videoBitrate': u'2096090', 'audioCodecProfile': u'Joint stereo', 'haveVideo': 1, 'videoWidth': 1280, 'videoDuration': '38.473', 'audioChannel': u'2', 'fileSize': u'11455592', 'duration': '39.618', 'haveAudio': 1, 'audioSamplingRate': u'44100', 'audioDuration': '39.842', 'bitrate': u'2307059', 'videoCodecProfile': u'High@L3.1', 'audioCodec': u'MPA1L3', 'videoHeight': 720}, 'English', 1.5112920822571074, 1538501464.0], u'e2a432c457cf513591901afb5603ce1f7b7c05ad': [1538504188, u'dl', 959, 99, {'videoFrameRate': u'25.000', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'1140', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioBitrate': u'96000', 'videoBitrate': u'2162171', 'audioCodecProfile': u'Joint stereo', 'haveVideo': 1, 'videoWidth': 1280, 'videoDuration': '45.6', 'audioChannel': u'2', 'fileSize': u'13669856', 'duration': '45.962', 'haveAudio': 1, 'audioSamplingRate': u'44100', 'audioDuration': '46.034', 'bitrate': u'2376574', 'videoCodecProfile': u'High@L3.1', 'audioCodec': u'MPA1L3', 'videoHeight': 720}, ' / Spanish', 3.195894594487695, 1538501464.0], u'b27acb3ad8e7ffc14394a1d49ed6e6c3dec51460': [1538504533, u'dl', 766, 42, {'videoFrameRate': u'25.000', 'videoAspectRatio': u'1.778', 'videoFrameCount': u'1040', 'videoCodec': u'AVC', 'container': u'MPEG-TS', 'audioCodecProfile': u'LC', 'haveVideo': 1, 'videoWidth': 960, 'videoDuration': '41.615', 'audioChannel': u'2', 'fileSize': u'7927208', 'duration': '41.452', 'haveAudio': 1, 'audioSamplingRate': u'48000', 'audioDuration': '41.449', 'bitrate': u'1528314', 'videoCodecProfile': u'Main@L3.1', 'audioCodec': u'AAC', 'videoHeight': 540}, '', 1.6840518375150655, 1538501464.0]}}


print newmatches
possibles={}
for match in newmatches:
  for stream in newmatches[match]:
    #if stream=="f4b452a0680eb1467d7ccc30d4678e7792250f24": print newmatches[match][stream]
    if 'bitrate' in newmatches[match][stream][4]:
      print stream, newmatches[match][stream][4]['bitrate'], newmatches[match][stream][2], newmatches[match][stream][3], newmatches[match][stream][4]['videoWidth']
      if newmatches[match][stream][4]['bitrate']>bitrate_min:#order by number of peers
        possibles[stream]=newmatches[match][stream][3]
      
#print possibles
beststream=[]
for key, value in sorted(possibles.iteritems(), key=lambda (k,v): (v,k)):
    beststream.append(key)
print beststream.pop()
