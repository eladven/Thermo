<!DOCTYPE HTML>
<html> 
<head>
<style>
.error {color: #FF0000;}
</style>
</head>
<body>

<?php
$myfile = fopen("instantDataFile.thr", "r") or die("Unable to open file!");
$line =  fread($myfile,filesize("instantDataFile.thr"));
$words = explode(" ", $line);
fclose($myfile);
?>

<article>
  <header>
    <h1>Heater Control</h1>
    <h3><?php echo "Machine update time: ".$words[0]." : ".$words[2];?></h1>
  </header>
</article>
	
<table border="1" bgcolor="#E8E8E8">
  <tr>
    <th>Place</th>
    <th>temp [c]</th>
  </tr>
  <tr>
    <td>Room</td>
    <td><?php echo $words[4];?></td>
  </tr>
  <tr>
    <td>Heater water</td>
    <td><?php echo $words[6];?></td>
  </tr>
<tr>
  <td>Calculated desired temp</td>
  <td><?php echo $words[8];?></td>
</tr>
<tr>
  <td>Heater is active </td>
  <td><?php echo $words[10];?></td>
</tr>
</table>

<?php
  $tempErr = "";
  $sendTemp = ""; 

  if( $_REQUEST["sendTemp"] )
  {
	 if (empty( $_REQUEST["sendTemp"])) {
     	$tempErr = "SendTemp is required";
     } else {
     	$sendTemp = $_REQUEST['sendTemp'];
     	if (!preg_match("/^[0-9]*$/",$sendTemp)) {
      	 	$tempErr = "Only Digits allowed"; 
		} else{
			$myfile = fopen("/var/www/roomTempFile.thr", "w") or $tempErr = "Unable to open file";
			fwrite($myfile, "roomTemp ".$sendTemp."\n");
			fclose($myfile);
                        $page = $_SERVER['PHP_SELF'];
                        $sec = "2";
                        header("Refresh: $sec; url=$page");
		}
	 }

  }
?>

  <p>Menualy set the room temp:</p>	
  <form action="<?php $_PHP_SELF ?>" method="POST">

  Temp: <input type="text" name="sendTemp" />
 	<span class="error">* <?php echo $tempErr?></span>
  <input type="submit" />
  </form>
	
</body>
</html>
