if ( window.history.replaceState ) {
  window.history.replaceState( null, null, window.location.href );
}

// function get_today() {
//   var myDate = document.querySelector(myDate);
//   var today = new Date();
//   myDate.value = today.toISOString().substr(0, 10);
// }
window.onload = function() {
  $(document).ready(function() {
    get_today();
});
}



function get_today() {
  document.getElementById("myDate").value = new Date().toISOString().substr(0, 10);
}