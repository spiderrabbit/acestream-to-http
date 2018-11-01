import acestream_to_http_tc
import ConfigParser
import sys, psutil, os, hashlib, time, requests, json

dir_path = os.path.dirname(os.path.realpath(__file__))+"/www"  #change this to where you want to store files. Must have "listings" and "segments" subdirectories writeable by 
stream_pid = sys.argv[1]

Config = ConfigParser.ConfigParser()
Config.read('/home/acestream/.config/acestream-to-http/acestream_to_http.conf')
PORT = Config.get('main', 'port')
SERVER_IP = Config.get('main', 'domain')
USERNAME = Config.get('main', 'username')
PASSWORD = Config.get('main', 'password')
PROTOCOL = Config.get('main', 'protocol')

if stream_pid == 'stopstream':
  acestream_to_http_tc.stopengine(dir_path)
  
else:
  enginerunning = False
  if "acestreamengine" in (p.name() for p in psutil.process_iter()): 
    enginerunning=True

  if enginerunning == False:
    acestream_to_http_tc.startengine(dir_path)
    time.sleep(5)
    
  acestream_to_http_tc.stopvlc(dir_path)#stop any existing transcoding


  stream_uid = hashlib.sha1(stream_pid).hexdigest()
  r = requests.get('http://127.0.0.1:6878/ace/getstream?format=json&sid={0}&id={1}'.format(stream_uid, stream_pid))
  out = json.loads(r.text)
  if out['response'] is not None:
    out['response']['stream_pid'] = stream_pid
    #pid_stat_url = [stream_pid, json.loads(r.text)['response']['stat_url'], json.loads(r.text)['response']['playback_url'], r.text, stream_pid]
    with open('/tmp/pid_stat_url', 'w') as f: f.write(json.dumps(out))

    time.sleep(5)

    acestream_to_http_tc.startvlc(dir_path, PROTOCOL, USERNAME, PASSWORD, SERVER_IP)

    print '{0}://{1}:{2}@{3}/segments/acestream.m3u8'.format(PROTOCOL, USERNAME, PASSWORD, SERVER_IP)
  else:
    print out['error']

  #speed_down is in kilobytes / sec
