<script>
  function submitForm() {
    var passwordInput = document.getElementById("password").value;
    
    // Create an XMLHttpRequest object
    var xhr = new XMLHttpRequest();
    
    // Configure the request
    xhr.open("POST", "http://localhost:2222/login", true);
    
    // Set the Content-Type header
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    
    // Send the password as data
    xhr.send("password=" + passwordInput);
  }
</script>
