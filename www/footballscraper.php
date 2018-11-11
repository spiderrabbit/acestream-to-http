<?php
$cache_file='/tmp/fixtures.json';
if (file_exists($cache_file) && (filemtime($cache_file) > (time() - 3600 * 24 ))) {
   $data = file_get_contents($cache_file);
} 
else {
  $_GET['date']=preg_replace("#[^0-9\-]#","",$_GET['date']);
  exec('/usr/bin/python ../footballscraper.py '.$_GET['date'], $out);
  file_put_contents($cache_file, $out[0], LOCK_EX);
  $data = $out[0];
}

echo $data;
?>
