import os, MediaInfo, json, subprocess, psutil, requests

def startvlc(dir_path, PROTOCOL, USERNAME, PASSWORD, SERVER_IP):
  f = open(dir_path+"/listings/LIVE.strm", "w")
  f.write("%s://%s:%s@%s/segments/acestream.m3u8" % (PROTOCOL, USERNAME, PASSWORD, SERVER_IP))
  f.close()
  subprocess.Popen(["cvlc", "--live-caching", "30000", pid_stat_url[2], "--sout", "#duplicate{dst=std{access=livehttp{seglen=5,delsegs=true,numsegs=20,index="+dir_path+"/segments/acestream.m3u8,index-url="+PROTOCOL+"://"+USERNAME+":"+PASSWORD+"@"+SERVER_IP+"/segments/stream-########.ts},mux=ts{use-key-frames},dst="+dir_path+"/segments/stream-########.ts},dst=std{access=file,mux=ts,dst='"+dir_path+"/listings/live_stream_from_start.mp4'}}"])
  return

def stopvlc(dir_path):
  for process in psutil.process_iter(): 
    if'/usr/bin/vlc' in process.cmdline() and '--live-caching' in process.cmdline():
      process.kill()
  if os.path.isfile(dir_path+"/listings/LIVE.strm"):
    os.remove(dir_path+"/listings/LIVE.strm")

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
