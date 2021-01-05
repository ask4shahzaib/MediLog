const cnic = document.getElementById('cnic');
const signUp = document.getElementById('form');


function myFunction() {
  var x = document.getElementById("password");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

form.addEventListener('transform', (e) => {
  let messages = [];
  e.presentDefault();
  if(cnic.value.length != 13)
  {
    messages.push('CNIC must be 13 characters long');
  }

})
