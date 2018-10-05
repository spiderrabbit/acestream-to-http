<?php
header("Content-Type: application/rss+xml; charset=ISO-8859-1");
?>
<xml version="1.0" encoding="ISO-8859-1"?>
<rss version="2.0">
    <channel>
        <title>Acestream RSS feed</title>
        <description>RSS feed of working acestream links</description>
        <language>en-gb</language>
<?php
$matches = json_decode(file_get_contents('../matches.json'),1);
foreach ($matches as $k=>$m){
  foreach ($m as $sk=>$s){
echo"            <item>
                <title>$k</title>
                <pid>$sk</pid>
                <posted>$s[7]</posted>
                <language>$s[5]</language>
                <dl_speed>$s[2]</dl_speed>
                <peers>$s[3]</peers>
		<size>".($s[4][videoWidth]?$s[4][videoWidth]."x".$s[4][videoHeight]:"")."</size>
		<fps>".$s[4][videoFrameRate]."</fps>
		<bitrate>".$s[4][bitrate]."</bitrate>
		<last_checked>$s[0]</last_checked>
            </item>
";
#echo "<tr><td>$k</td><td>".date(DATE_ATOM,$s[7])."</td><td>$sk</td><td>$s[5]</td><td>$s[1]</td><td>$s[2]</td><td>$s[3]</td><td>".($s[
#4][videoWidth]?$s[4][videoWidth]."x".$s[4][videoHeight]:"")."</td><td>".$s[4][videoFrameRate]."</td><td>".(round($s[4][bitrate]/1000))."</td><td>$s[6]</td><td>".date(DATE_ATOM,$s[1])."</td>";

  }
}

?>
    </channel>
</rss>
