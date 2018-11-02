<?php
$_GET['date']=preg_replace("#[^0-9\-]#","",$_GET['date']);
exec('/usr/bin/python ../footballscraper.py '.$_GET['date'], $out);
echo $out[0]
?>
