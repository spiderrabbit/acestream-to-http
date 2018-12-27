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
  else{
    $status = ['current_recording'=>''];
  }
  $status['ip'] = @file_get_contents("http://ipinfo.io/ip");
  $status['diskfreespace'] = disk_free_space("/home/acestream");
  echo json_encode($status);
}
else if($_GET['action']=='listings'){
  echo file_get_contents('listings/recordings.json');
}
else if($_GET['action']=='deleterecordedfile'){
  //delete recording + transcoded 
  $recorded = json_decode(file_get_contents('listings/recordings.json'),1);
  $matchname = $recorded[$_GET['recording']];
  $transcodedmatchname = "TRANSCODED_".$matchname;
  $transcodedkey = array_search($transcodedmatchname, $recorded);
  unlink('listings/'.$matchname.'.mp4');
  unlink('listings/'.$transcodedmatchname.'.mp4');
  unlink('store/'.$_GET['recording'].'.mp4');
  unlink('store/'.$transcodedkey.'.mp4');
  //rebuild recordings json
  unset($recorded[$_GET['recording']]);
  unset($recorded[$transcodedkey]);
  file_put_contents('listings/recordings.json', json_encode($recorded));
}
// <rss version="2.0">
//   <channel>
//     <title>Karaoke</title>
//     <link>http://vk-karaoke.appspot.com/rss</link>
//     <description>https://vk.com/vkkar</description>
//     <lastBuildDate>Thu, 23 Jun 2016 16:00:00 GMT</lastBuildDate>
//     <generator>vkkar</generator>
//     <ttl>3600</ttl>
//     <item>
//       <title>test.mp3</title>
//       <link>http://vk-karaoke.appspot.com/u/140%20%D0%A3%D0%B4%D0%B0%D1%80%D0%BE%D0%B2%20%D0%92%20%D0%9C%D0%B8%D0%BD%D1%83%D1%82%D1%83%20-%20%D0%9E%D0%B9%2C%20%D0%9E%D0%B9.mp3</link>
//       <guid isPermaLink="true">344191188</guid>
//       <pubDate>Thu, 23 Jun 2016 16:00:09 GMT</pubDate>
//       <enclosure url="http://cs611223.vk.me/u9488564/audios/d16a787f7d21.mp3?extra=uRsIn3dT8ffJYzFYpd-SkROo9MYP0huTsFTRlxIo70VAer3B4LurmEXPLsrdP_b9DdEKVU15nD1xL5jYBOm3pyN7tF31UysfGZ5bRzlriMzrI_iQt0QhRWynCdeMeCve7V0SQCPL2_Ejiw" length="0" type="audio/mpeg"/>
//     </item>
//   </channel>
// </rss>

// else if($_GET['action']=='listings'){
//   $recordings = json_decode(file_get_contents('listings/recordings.json'),1);
//   print_r($recordings);
//   $dirlist = scandir('listings');
//   for ($i=0; $i< count($dirlist); $i++){
//     if (substr($dirlist[$i],-3)=="mp4"){
//       $outdirlist[$dirlist[$i]]=True;
//       }
//     }
//   print_r($outdirlist);
//   unset($outdirlist['live_stream_from_start.mp4']);
//   foreach ($outdirlist as $k=>$v){
//     if (substr($k,0,10)=="PROCESSED_"){
//       unset($outdirlist[substr($k,10)]);
//     }
//   }
//   print_r($outdirlist);
// }

?>
