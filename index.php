<!DOCTYPE HTML> 
<html>
<head>
<style>
.error {color: #FF0000;}
</style>
</head>
<body> 

<?php

$mode = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
   $gender = test_input($_POST["mode"]);
}

function test_input($data) {
   $data = trim($data);
   $data = stripslashes($data);
   $data = htmlspecialchars($data);
   return $data;
}
?>

<h2>Thermo Control</h2>
<form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>"> 
  Mode:
  <input type="radio" name="mode" <?php if (isset($mode) && $mode=="byWeb") echo "checked";?>  value="byWeb">ByWeb
  <input type="radio" name="mode" <?php if (isset($mode) && $mode=="byControler") echo "checked";?>  value="byControler">ByControler
   <br><br>
</form>

<?php
echo "<h2>Your Input:</h2>";
echo $gender;
?>

</body>
</html>
