<html>
<head>
<style>
body td{
font-size:12px;
}
</style>
<script>
function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("myTable2");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "desc"; 
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
//        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
//          // If so, mark as a switch and break the loop:
//          shouldSwitch = true;
//          break;
//        }
        if (Number(x.innerHTML) > Number(y.innerHTML)) {
          shouldSwitch = true;
          break;
          }
      } else if (dir == "desc") {
//        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
//          // If so, mark as a switch and break the loop:
//          shouldSwitch = true;
//         break;
//       }
        if (Number(x.innerHTML) < Number(y.innerHTML)) {
          shouldSwitch = true; 
           break;
        }
 }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++; 
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
</script>

</head>
<body>
<table border=1 id="myTable2">
<tr>
<th>Match</th><th>Posted on</th><th>PID</th><th>Language</th><th>Status</th>
<th onclick="sortTable(4)">DL speed</th>
<th onclick="sortTable(5)">Peers</th>
<th>Size</th><th>FPS</th><th>Bitrate (kbps)</th><th>Stream Score</th><th>Last checked</th>
<?
$matches = json_decode(file_get_contents('matches.json'),1);
foreach ($matches as $k=>$m){
  foreach ($m as $sk=>$s){
//print_r($s);
    echo "<tr><td>$k</td><td>".date(DATE_ATOM,$s[7]*1)."</td><td>$sk</td><td>$s[5]</td><td>$s[1]</td><td>$s[2]</td><td>$s[3]</td><td>".($s[4][videoWidth]?$s[4][videoWidth]."x".$s[4][videoHeight]:"")."</td><td>".$s[4][videoFrameRate]."</td><td>".(round($s[4][bitrate]/1000))."</td><td>".round($s[6]*100)."</td><td>".date(DATE_ATOM,$s[0]*1)."</td>";
  }
}
?>
<table>
</body>
</html>
	
