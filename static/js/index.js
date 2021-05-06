function stringlength(inputtxt, minlength, maxlength) {
  var field = inputtxt.value;
  var mnlen = minlength;
  var mxlen = maxlength;

  if (field.length < mnlen || field.length > mxlen) {
    alert(
      "Please input the userid between " +
        mnlen +
        " and " +
        mxlen +
        " characters"
    );
    return false;
  } else {
    return true;
  }
}

// For form validation
function validateForm(){
	var cnic = document.forms["form1"]["your-CNIC"].value;
	var phone = document.forms["form1"]["your-phone"].value;

	if (!(cnic.length==13)) {
        document.getElementById('cnic').innerHTML = "CNIC must be 13 digits long *"
    }
    if (phone.length<1) {
        document.getElementById('error-phone').innerHTML = " Please Enter Your Phone *";      
    }
      
    if(phone.length<1 || cnic.length<1){
       	return false;
    }            
}
