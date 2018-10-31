import SimpleHTTPServer, SocketServer, requests
import os, psutil, time, sys, base64
import hashlib, json
import ConfigParser
import acestream_to_http_tc


Config = ConfigParser.ConfigParser()
Config.read("/home/acestream/.config/acestream-to-http/acestream_to_http.conf")
PORT = Config.get('main', 'port')
SERVER_IP = Config.get('main', 'domain')
USERNAME = Config.get('main', 'username')
PASSWORD = Config.get('main', 'password')
PROTOCOL = Config.get('main', 'protocol')
dir_path = os.path.dirname(os.path.realpath(__file__))+"/www"  #change this to where you want to store files. Must have "listings" and "segments" subdirectories writeable by script

temp_stream_saved = False
file_save_status = []
key = ""
streamtimer = 0

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_AUTHHEAD(self):
    self.send_response(401)
    self.send_header('WWW-Authenticate', 'Basic realm=\"acestream_to_http\"')
    self.send_header('Content-type', 'text/html')
    self.end_headers()
  
  def do_GET(self):
    global temp_stream_saved, file_save_status, key, streamtimer, dir_pat
    
    path = self.path.split("/")
    if path[1] != 'segments':#allow non-password access to live stream segments
      if self.headers.getheader('Authorization') == None:
        self.do_AUTHHEAD()
        pass
      elif self.headers.getheader('Authorization') != "Basic %s" % key:
        self.do_AUTHHEAD()
        pass
      if self.headers.getheader('Authorization') != "Basic %s" % key:
        return
      
    #check if vlc running 
    vlcrunning = False
    for process in psutil.process_iter(): 
      if '/usr/bin/vlc' in process.cmdline() and '--live-caching' in process.cmdline(): 
        vlcrunning = True
        vlcrunning_line = process.cmdline()
    enginerunning = False
    if "acestreamengine" in (p.name() for p in psutil.process_iter()): 
      enginerunning=True
      
    if path[1] == 'engine':
      if len(path) == 3:
        if path[2] == 'start' and enginerunning == False:
          acestream_to_http_tc.startengine(dir_path)
        elif path[2] == 'stop':
          acestream_to_http_tc.stopengine(dir_path)
        elif path[2] == 'stopstream':
          acestream_to_http_tc.stopenginestream(dir_path)
        time.sleep(5)
        self.send_response(302)
        self.send_header('Location',"/")
        self.end_headers()
    
    elif path[1] == 'transcoding' and acestream_to_http_tc.engine_status() is not None:
      if len(path) == 3:
        if path[2] == 'start':
          if vlcrunning == False:#only start one instance
            temp_stream_saved = False
            acestream_to_http_tc.startvlc(dir_path, PROTOCOL, USERNAME, PASSWORD, SERVER_IP)
        elif path[2] == 'stop':
          acestream_to_http_tc.stopengine(dir_path)
          temp_stream_saved = True
        time.sleep(5)stream_pid
        self.send_response(302)
        self.send_header('Location',"/")
        self.end_headers()
        
    elif path[1] == 'savefile' and len(path)==3:
      for f in path[2].split("?")[1].split("&"):
        if f.split("=")[0] == "savefilename":
          matchname = f.split("=")[1]
      acestream_to_http_tc.stopengine(dir_path)
      acestream_to_http_tc.ffmpeg_transcode(dir_path+"/listings/live_stream_from_start.mp4", dir_path+"/listings/"+matchname+".mp4")
      temp_stream_saved = False
      self.send_response(302)
      self.send_header('Location',"/")
      self.end_headers()
    
    elif path[1] == 'openpid' and len(path)==3 and enginerunning:
      acestream_to_http_tc.stopvlc(dir_path)
      stream_pid = False
      for f in path[2].split("?")[1].split("&"):
        if f.split("=")[0] == "pid":
          stream_pid = f.split("=")[1]
          stream_uid = hashlib.sha1(stream_pid).hexdigest()
      if stream_pid:
        r = requests.get('http://127.0.0.1:6878/ace/getstream?format=json&sid={0}&id={1}'.format(stream_uid, stream_pid))
        out = json.loads(r.text)
        out['response']['stream_pid'] = stream_pid
        #pid_stat_url = [stream_pid, json.loads(r.text)['response']['stat_url'], json.loads(r.text)['response']['playback_url'], r.text, stream_pid]
        with open('/tmp/pid_stat_url', 'w') as f: f.write(json.dumps(out))
      
      #start stream timer
      streamtimer = time.time()
      time.sleep(5)
      self.send_response(302)
      self.send_header('Location',"/")
      self.end_headers()

    else:
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write("""
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{
  font-family: Arial;
  font-size:12px;
  text-align:center;
}
.button {
    background-color: #4CAF50;
    border: none; 
    color: white; 
    padding: 12px 24px; 
    font-size: 12px;
    cursor: pointer;
    width:150px;
    text-align:left;
}
.buttonloading {
    background-color: #4CAF50;
    }
.buttonstopped{
    background-color: #AF504C
    }
  
.fa {
    margin-left: -12px;
    margin-right: 8px;
}
.status{
    font-family:Courier;
    font-size:80%;
}
.statusdiv{
    margin:auto;
    text-align:center;
    width:400px;
    padding-top:10px;
    padding-bottom:20px;
    font-family: Courier;
    font-weight: bold;
}
</style>
</head>
<body>
""")
      self.wfile.write("<div>")
      disabledtext = ["", ""]
      if enginerunning: 
        disabledtext[0] = "disabled style='opacity: 0.4;'"
        engine_status_text = "Running"
      else: 
        disabledtext[1] = "disabled style='opacity: 0.4;'"
        engine_status_text = "Not running"
      self.wfile.write("""
        <button class='button buttonloading' %s onclick='this.style.display=\"none\";document.getElementById(\"button_starting\").style.display=\"\";location.href="/engine/start\"'>
        <i class='fa fa-stop-circle'></i>Start Engine</button>
       <button id='button_starting' class='button buttonloading' style='display:none'> 
        <i class='fa fa-spinner fa-spin'></i>Starting Engine</button>
       """ % disabledtext[0])
      self.wfile.write("""
        <button class='button buttonstopped' %s onclick='this.style.display=\"none\";document.getElementById(\"button_stopping\").style.display=\"\";location.href="/engine/stop\"'>
        <i class='fa fa-play-circle'></i>Stop Engine</button>
        <button id='button_stopping' class='button buttonloading' style='display:none'> 
        <i class='fa fa-spinner fa-spin'></i>Stopping Engine</button>
        """% disabledtext[1])
      
      self.wfile.write("</div><div class='statusdiv'>Engine Status: %s</div>" % engine_status_text)
      
      disabledtext = ["", ""]
      stream_OK_to_transcode = False
      engine_status = acestream_to_http_tc.engine_status()
      if enginerunning:
        if engine_status is not None:
          s = requests.get(engine_status['response']['stat_url'])
          engine_response = json.loads(s.text)
          disabledtext[0] = "disabled style='opacity: 0.4;'"
          acestream_status_text = "Streaming<br />acestream://%s<br />" % engine_status['response']['stream_pid']
          if (time.time() - streamtimer) < 30:
            acestream_status_text+="Wait 30s for stream to settle<br />"
            acestream_status_text+="""
            <script>
            var timeleft = 30;
            var downloadTimer = setInterval(function(){
              document.getElementById("progressBar").value = 30 - --timeleft;
              if(timeleft <= 0){
                clearInterval(downloadTimer);
                location.href="/";
              }
            },1000);
            </script>
            <progress value="0" max="30" id="progressBar"></progress>
            <br />
            """
          elif 'response' in engine_response:
            if 'speed_down' in engine_response['response']:
              if engine_response['response']['status'] == "prebuf":
                acestream_status_text+="Buffering"
              elif int(engine_response['response']['speed_down']) < 100:
                acestream_status_text+="Stream health poor"
              elif int(engine_response['response']['speed_down']) < 300:
                acestream_status_text+="Stream health average"
                stream_OK_to_transcode = True
              else:
                acestream_status_text+="Stream health OK"
                stream_OK_to_transcode = True
              if stream_OK_to_transcode:
                acestream_status_text+="<br />DL Speed: %s kbps<br />Peers %s" % (engine_response['response']['speed_down'], engine_response['response']['peers'])
              else:#reload every 5 seconds if buffering or poor stream health
                self.wfile.write("""<script>
                  setTimeout(function(){
                    window.location.reload(1);
                  }, 5000);
                  </script>""")
            
        else:
          disabledtext[1] = "disabled style='opacity: 0.4;'"
          acestream_status_text = "No stream"
      else:
        disabledtext[0] = "disabled style='opacity: 0.4;'"
        disabledtext[1] = "disabled style='opacity: 0.4;'"
        acestream_status_text = ""
      self.wfile.write('<div><form method="GET" action="/openpid/" id="openpid" style="display:inline"><input type=text name="pid" placeholder="Acestream ID" style="margin-bottom:10px;width:300px;" %s><br>' % disabledtext[0])   
      self.wfile.write("""
        <button class='button buttonloading' %s onclick='this.style.display="none"; document.getElementById("button_ace_starting").style.display=""; document.getElementById("openpid").submit()'>
        <i class='fa fa-stop-circle'></i>Start Acestream</button>
        <button id='button_ace_starting' class='button buttonloading' style='display:none'>
        <i class='fa fa-spinner fa-spin'></i>Starting Acestream</button></form>
      """ % disabledtext[0])
      self.wfile.write("""
        <button class='button buttonstopped' %s onclick='this.style.display="none";document.getElementById("button_ace_stopping").style.display="";location.href="/engine/stopstream"'>
        <i class='fa fa-play-circle'></i>Stop Acestream</button>
        <button id="button_ace_stopping" class='button buttonstopped' style='display:none'> 
        <i class='fa fa-spinner fa-spin'></i>Stopping Acestream</button>
        """ % disabledtext[1])
      self.wfile.write("</div><div class='statusdiv'>Acestream Status: %s</div>" % acestream_status_text)
      
      self.wfile.write("<div>")
      disabledtext = ["", ""]
      if stream_OK_to_transcode:
        if vlcrunning:
          disabledtext[0] = "disabled style='opacity: 0.4;'"
          transcode_status_text = """
          Transcoding<br />Stream: %s://%s/segments/acestream.m3u8<br />
          Kodi: %s://%s/listings/LIVE.strm<br />
          """ % (PROTOCOL, SERVER_IP, PROTOCOL, SERVER_IP)
        else:
          disabledtext[1] = "disabled style='opacity: 0.4;'"
          transcode_status_text = "Not Transcoding"
      else:
        disabledtext[0] = "disabled style='opacity: 0.4;'"
        disabledtext[1] = "disabled style='opacity: 0.4;'"
        transcode_status_text = ""
      self.wfile.write("""
        <button class='button buttonloading' %s onclick='this.style.display=\"none\";document.getElementById(\"transcode_starting\").style.display=\"\";location.href="/transcoding/start\"'>
        <i class='fa fa-stop-circle'></i>Start Transcode</button>
       <button id='transcode_starting' class='button buttonloading' style='display:none'> 
        <i class='fa fa-spinner fa-spin'></i>Starting Transcode</button>
       """ % disabledtext[0])
      self.wfile.write("""
        <button class='button buttonstopped' %s onclick='this.style.display=\"none\";document.getElementById(\"transcode_stopping\").style.display=\"\";location.href="/transcoding/stop\"'>
        <i class='fa fa-play-circle'></i>Stop Transcode</button>
        <button id='transcode_stopping' class='button buttonloading' style='display:none'> 
        <i class='fa fa-spinner fa-spin'></i>Stopping Trancode</button>
        """% disabledtext[1])
      
      self.wfile.write("</div><div class='statusdiv'>Transcode Status: %s</div>" % transcode_status_text) 

      if vlcrunning: disabledtext[0] = ""
      else: disabledtext[0] = "disabled style='opacity: 0.4;'"
      self.wfile.write("<button class='button buttonloading' %s onclick='window.open(\"%s://%s/player.html\", \"\", \"width=660,height=380\");'><i class='fa fa-play-circle'></i>Launch Player</button>" % (disabledtext[0], PROTOCOL, SERVER_IP))
      
      if not temp_stream_saved:  disabledtext[0] = "disabled style='opacity: 0.4;'"
      else: disabledtext[0] = ""
      self.wfile.write('''
       <div>
       <form method="GET" action="/savefile/" id="savefile">
       <input type=text name="savefilename" placeholder="Save filename" style="margin-top:20px; margin-bottom:10px;width:300px;" %s><br />
       <button class='button buttonloading' %s onclick='document.getElementById("savefile").submit()'>
       <i class='fa fa-save'></i>Save Recording</button>
       </form>
       </div>
      ''' % (disabledtext[0], disabledtext[0]))
      

def main():
  global key, USERNAME, PASSWORD
  key = base64.b64encode("%s:%s" % (USERNAME, PASSWORD))
  SocketServer.TCPServer.allow_reuse_address = True
  httpd = SocketServer.TCPServer(("", int(PORT)), Handler)
  print "Running on http://%s:%s" % (SERVER_IP, PORT)
  acestream_to_http_tc.stopengine(dir_path)#start with a clean slate
  httpd.serve_forever()

main()
