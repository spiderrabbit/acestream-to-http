<?php
if($_GET['action']=='record'){
    $torecord = json_decode(file_get_contents('../torecord.json'),1);
    if (!in_array($_GET['name'],$torecord)){
      $torecord[] = $_GET['name'];
      file_put_contents('../torecord.json', json_encode($torecord));
    }
    echo "OK";
}
