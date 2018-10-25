<?php
if($_GET['action']=='record'){
    $torecord = json_decode('../torecord.json',1);
    print_r($torecord);
    $torecord[] = $_GET['name'];
    file_put_contents('../torecord.json', json_encode($torecord));
}
