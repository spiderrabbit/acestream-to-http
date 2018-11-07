import os, json, subprocess, psutil, requests, random, string
import ConfigParser
from MediaInfo import MediaInfo

Config = ConfigParser.ConfigParser()
Config.read("/home/acestream/.config/acestream-to-http/acestream_to_http.conf")
PORT = Config.get('main', 'port')
SERVER_IP = Config.get('main', 'domain')
USERNAME = Config.get('main', 'username')
PASSWORD = Config.get('main', 'password')
PROTOCOL = Config.get('main', 'protocol')
dir_path = os.path.dirname(os.path.realpath(__file__))+"/www"

def startvlc(recording_name):
  pid_stat_url=engine_status()
  random_segment_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
  subprocess.Popen([
    "cvlc", 
    "--live-caching", "30000", 
    pid_stat_url['response']['playback_url'], 
    "--sout", 
    "#duplicate{{dst=std{{access=livehttp{{seglen=5,delsegs=true,numsegs=20,index={0}/listings/LIVE.m3u8,index-url={1}://{2}/segments/{3}-########.ts}},mux=ts{{use-key-frames}},dst={0}/segments/{3}-########.ts}},dst=std{{access=file,mux=ts,dst='{0}/listings/{3}.mp4'}}}}".format(dir_path, PROTOCOL, SERVER_IP, random_segment_name)
  ])
  #store recording title in json
  recordings = recordings_status()
  recordings[random_segment_name] = recording_name
  with open('{0}/listings/recordings.json'.format(dir_path), 'w+') as f: f.write(json.dumps(recordings))
  with open('/tmp/current_recording', 'w') as f: f.write(recording_name)
  return

def stopvlc():
  for process in psutil.process_iter(): 
    if'/usr/bin/vlc' in process.cmdline() and '--live-caching' in process.cmdline():
      process.kill()
  with open('/tmp/current_recording', 'w') as f: f.write('')#clear current recording file

def startengine():
  subprocess.Popen(["/snap/bin/acestreamplayer.engine", "--client-console", "--live-cache-type", "disk", "--live-disk-cache-size", "1000000000"])
  return
  
def stopengine():
  stopvlc()
  for process in psutil.process_iter(): 
    if process.name() == "acestreamengine":
      process.kill()
  with open('/tmp/pid_stat_url', 'w') as f: f.write(json.dumps(None))
  return

def stopenginestream():
  stopvlc()
  if engine_status() is not None:
    sr = requests.get(engine_status()['response']['command_url']+"?method=stop")
  with open('/tmp/pid_stat_url', 'w') as f: f.write(json.dumps(None))

def ffmpeg_transcode(file_to_transcode):
  #find actual disk file
  recordings = recordings_status()
  recordingfilename = ''
  for f in recordings:
    if recordings[f] == file_to_transcode: 
      recordingfilename = '{}.mp4'.format(f)
  if len(recordingfilename)>0:
    random_segment_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    disk_recording_name = '{0}/listings/{1}'.format(dir_path,recordingfilename)
    disk_recording_outputfile = '{0}/listings/{1}.mp4'.format(dir_path,random_segment_name)
    #ffmpeg has needed -bsf:a aac_adtstoasc option to fix  PES packet size mismatch, Error parsing ADTS frame header errors only for AAC audio
    info = MediaInfo(filename = disk_recording_name)
    try:
      if info.getInfo()['audioCodec']=="AAC":
        file_save_status = ["ffmpeg", "-y", "-i", disk_recording_name, "-c:v", "copy", "-c:a", "copy", "-movflags", "faststart", "-bsf:a", "aac_adtstoasc", disk_recording_outputfile]
      else:
        file_save_status = ["ffmpeg", "-y", "-i", disk_recording_name, "-c:v", "copy", "-c:a", "copy", "-movflags", "faststart", disk_recording_outputfile]
    except:
      file_save_status = ["ffmpeg", "-y", "-i", disk_recording_name, "-c:v", "copy", "-c:a", "copy", "-movflags", "faststart", disk_recording_outputfile]
    subprocess.Popen(file_save_status)
    recordings[random_segment_name] = 'TRANSCODED_{0}'.format(file_to_transcode)
    with open('{0}/listings/recordings.json'.format(dir_path), 'w+') as f: f.write(json.dumps(recordings))
  return

def recordings_status():
  recordings_store = '{0}/listings/recordings.json'.format(dir_path)
  if os.path.isfile(recordings_store):
    with open(recordings_store, 'r') as f: 
      recordings = json.loads(f.read())
  else:
    recordings = {}
  return recordings 

def engine_status():
  if os.path.isfile('/tmp/pid_stat_url'):
    with open('/tmp/pid_stat_url', 'r') as f: 
      pid_stat_url = json.loads(f.read())
  else:
    pid_stat_url = None
  return pid_stat_url
