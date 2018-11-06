<?php
$store = '../torecord.json';
if($_GET['action']=='record'){
  $torecord = json_decode(file_get_contents($store),1);
  if (!in_array($_GET['name'],$torecord)){
    $torecord[] = $_GET['name'];
    file_put_contents($store, json_encode($torecord));
  }
  echo "OK";
}
else if($_GET['action']=='torecord'){
  $torecord = json_decode(file_get_contents($store),1);
  for ($i=0; $i<count($torecord);$i++){
    $timestr = preg_replace("#[^0-9:-]#","",substr($torecord[$i],-16));
    if (strlen($timestr)==15){
      $matchtime=strtotime($timestr."Z");
      if ($matchtime and (time() - $matchtime) < 7200){#remove listings more than 2 hours old
        $newtorecord[] = $torecord[$i];
      }
    }
  }
  file_put_contents($store, json_encode($newtorecord));
  echo json_encode($newtorecord);
}
else if($_GET['action']=='deleterecording'){
  $torecord = json_decode(file_get_contents($store),1);
  for ($i=0; $i<count($torecord);$i++){
    if ($_GET['name'] != $torecord[$i]) $newtorecord[] = $torecord[$i];
  }
  file_put_contents($store, json_encode($newtorecord));
  echo json_encode($newtorecord);
}
else if($_GET['action']=='playstream'){
  $stream_id = preg_replace("#[^0-9a-z]#","",$_GET['stream_id']);
  if (strlen($stream_id)==40){
    $command = '/usr/bin/python /home/acestream/acestream-to-http/playstream.py '.$stream_id.' live_stream_from_start';
    exec($command. " > /dev/null &");
  }
  else echo "ERROR";
}
else if($_GET['action']=='stopstream'){
  $command = '/usr/bin/python /home/acestream/acestream-to-http/playstream.py stopstream';
  exec($command. " > /dev/null &");
}

else if($_GET['action']=='status'){
  $status = [];
  $current_recording = file_get_contents('/tmp/current_recording');
  if (strlen($current_recording)>0){
    $status = ['current_recording'=>$current_recording];
  }
  echo json_encode($status);
}
