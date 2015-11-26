// helper functions for show_entries.html
// mainly related to Google Map

function initMap() {
  pos = {lat: 33.776020, lng: -84.397111};
  map = new google.maps.Map(document.getElementById('map'), {
    center: pos,
    zoom: 17,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
  });
}

function postEvent(name, location, description) {

    var contentString = '<div id="content">'+
      '<div id="siteNotice">'+
      '</div>'+
      '<h1 id="firstHeading" class="firstHeading">' +
      name +
      '</h1>'+
      '<div id="bodyContent">'+
      '<p>' +
      description +
      '</p>' +
      '</div>'+
      '</div>';

    var infowindow = new google.maps.InfoWindow({
        content: contentString
    });

    var marker = new google.maps.Marker({
        position: position,
        map: map,
        title: 'Uluru (Ayers Rock)'
    });

    marker.addListener('click', function() {
        infowindow.open(map, marker);
    });
}

function getLonLat(location) {
    _url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + location;
    $.ajax({
        url: _url,
        method: "GET",
        dataType: "json",
        context: document.body,
        success: function(data) {
            console.log(data);
        }
    })
}