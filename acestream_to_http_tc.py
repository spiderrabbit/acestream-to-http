import os, json, subprocess, psutil, requests, random, string
from MediaInfo import MediaInfo
def startvlc(dir_path, PROTOCOL, USERNAME, PASSWORD, SERVER_IP, recording_name):
  pid_stat_url=engine_status()
  random_segment_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
  subprocess.Popen([
    "cvlc", 
    "--live-caching", "30000", 
    pid_stat_url['response']['playback_url'], 
    "--sout", 
    "#duplicate{{dst=std{{access=livehttp{{seglen=5,delsegs=true,numsegs=20,index={0}/listings/LIVE.m3u8,index-url={1}://{2}/segments/{3}-########.ts}},mux=ts{{use-key-frames}},dst={0}/segments/{3}-########.ts}},dst=std{{access=file,mux=ts,dst='{0}/listings/{4}.mp4'}}}}".format(dir_path, PROTOCOL, SERVER_IP, random_segment_name, recording_name)
  ])
  with open('/tmp/current_recording', 'w') as f: f.write(recording_name)
  return

def stopvlc(dir_path):
  for process in psutil.process_iter(): 
    if'/usr/bin/vlc' in process.cmdline() and '--live-caching' in process.cmdline():
      process.kill()
  with open('/tmp/current_recording', 'w') as f: f.write('')

def startengine(dir_path):
  subprocess.Popen(["/snap/bin/acestreamplayer.engine", "--client-console", "--live-cache-type", "disk", "--live-disk-cache-size", "1000000000"])
  return
  
def stopengine(dir_path):
  stopvlc(dir_path)
  for process in psutil.process_iter(): 
    if process.name() == "acestreamengine":
      process.kill()
  with open('/tmp/pid_stat_url', 'w') as f: f.write(json.dumps(None))
  return

def stopenginestream(dir_path):
  stopvlc(dir_path)
  if engine_status() is not None:
    sr = requests.get(engine_status()['response']['command_url']+"?method=stop")
  with open('/tmp/pid_stat_url', 'w') as f: f.write(json.dumps(None))

def ffmpeg_transcode(file_to_transcode, outputfile):
  #ffmpeg has needed -bsf:a aac_adtstoasc option to fix  PES packet size mismatch, Error parsing ADTS frame header errors only for AAC audio
  info = MediaInfo(filename = file_to_transcode)
  try:
    if info.getInfo()['audioCodec']=="AAC":
      file_save_status = ["ffmpeg", "-y", "-i", file_to_transcode, "-c:v", "copy", "-c:a", "copy", "-movflags", "faststart", "-bsf:a", "aac_adtstoasc", outputfile]
    else:
      file_save_status = ["ffmpeg", "-y", "-i", file_to_transcode, "-c:v", "copy", "-c:a", "copy", "-movflags", "faststart", outputfile]
  except:
    file_save_status = ["ffmpeg", "-y", "-i", file_to_transcode, "-c:v", "copy", "-c:a", "copy", "-movflags", "faststart", outputfile]
  subprocess.Popen(file_save_status)
  return

def engine_status():
  if os.path.isfile('/tmp/pid_stat_url'):
    with open('/tmp/pid_stat_url', 'r') as f: 
      pid_stat_url = json.loads(f.read())
  else:
    pid_stat_url = None
  return pid_stat_url
