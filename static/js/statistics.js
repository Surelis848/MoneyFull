
// 'Add Purchase' form resubmission on page reload

if ( window.history.replaceState ) {
  window.history.replaceState( null, null, window.location.href );
}

// getting today's date as a default when page fully loads

window.onload = function() {
  $(document).ready(function() {
    get_today();
});
}

function get_today() {
  document.getElementById("myDate").value = new Date().toISOString().substr(0, 10);
}