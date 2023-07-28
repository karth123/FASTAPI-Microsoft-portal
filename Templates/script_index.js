$(document).ready(function() {
  function loadContent(url) {
    $.ajax({
      url: url,
      method: "GET",
      success: function(data) {
        $("#content").html(data);
      }
    });
  }

  var initialLink = $(".topnav a.active").attr("href");
  loadContent(initialLink);

  $(".topnav a").click(function(e) {
    e.preventDefault();
    var url = $(this).attr("href");
    if (url.startsWith('/')) {
      loadContent(url);
      $(".topnav a").removeClass("active");
      $(this).addClass("active");
    } else {
      window.location.href = url;
    }
  });
});
