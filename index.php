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
	
<table border="1">
<tr>
	<td>tzip    1</td>
	<td><?php echo $words[1];?></td>
</tr>
<tr>
	<td>elad</td>
	<td><?php echo $words[3];?></td>
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
			$myfile = fopen("dataOut.txt", "w") or die("Unable to open file!");
			fwrite($myfile, "value is ".$sendTemp."\n");
			fclose($myfile);
		}
	 }

  }
?>
	
<html>
<body>
  <form action="<?php $_PHP_SELF ?>" method="POST">

  SendTemp: <input type="text" name="sendTemp" />
 	<span class="error">* <?php echo $tempErr?></span>
  <input type="submit" />
  </form>
</body>
</html>
	
</body>
</html>
