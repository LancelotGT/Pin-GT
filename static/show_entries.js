// helper functions for show_entries.html
// mainly related to Google Map

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: campusPosition,
    zoom: 16,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
  });

  map.addListener('click', function(e) {
    $('#myModal').modal('toggle');
    $('#savePin').click(function() {
        var name = $("input[name=Name]").val();
        var date = $("input[name=Date]").val();
        var time = $("input[name=Time]").val();
        var tags = $("input[name=Tags]").val();
        var location = $("input[name=Tags]").val();
        var description = $("textarea[name=Description]").val();
        postEvent(name, date, time, tags, location, description);
        placeMarkerAndPanTo(e.latLng, map, name, time, date, location, tags, description);
    })
  });
}

function placeMarkerAndPanTo(latLng, map, name, time, date, loc, tags, description) {
    var marker = new google.maps.Marker({
        position: latLng,
        map: map,
        title: name,
    });

    contentString = '<div id="content">'+
    '<div id="siteNotice">'+
    '</div>'+
    '<h3 id="firstHeading" class="firstHeading">' +
    name +
    '</h3>'+
    '<h4>Time:&nbsp' +
    time +
    '&nbspDate:&nbsp' +
    date +
    '</h4>' +
    '<h4>Location:&nbsp' +
    loc +
    '</h4><h4>Tags:&nbsp';
    for (var k = 0; k < tags.length; k++) {
        contentString = contentString + tags[k] + "&nbsp";
    }
    contentString = contentString + '</h4>' +
    '<div id="bodyContent">'+
    '<p>' +
    description +
    '</p>' +
    '</div>'+
    '</div><hr>';

  var infoWindow = new google.maps.InfoWindow();
  infoWindow.setContent(contentString);
  google.maps.event.addListener(marker, 'click', (function(marker) {
    return function() {
        infoWindow.setContent(contentString);
        infoWindow.open(map, marker);
    }
  })(marker));
  map.panTo(latLng);
}

function getEvents(startDate, endDate, tag) {

    // add more filter options here
    input = {
        'startDate': startDate,
        'endDate': endDate,
        'tag': tag
    }

    $.ajax({
        url: '/events',
        method: "GET",
        dataType: "json",
        data: input,
        context: document.body,
        success: addEventInfo
    });
}

function postEvent(name, date, time, tags, location, description) {

    // add more filter options here
    input = {
        'name': name,
        'date': date,
        'time': time,
        'tags': tags,
        'location': location,
        'description': description
    }

    $.ajax({
        url: '/events',
        method: "POST",
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(input),
        context: document.body,
        success: function(data) {
            console.log(data);
        }
    });
}

function addEventInfo(data) {
    var events = data.events // An array of events
    var contentStrings = [];

    for (var i = 0; i < events.length; i++) {
        var name = events[i].Name;
        var description = events[i].Description;
        var position = events[i].latlon;
        var loc = events[i].Location;
        var tags = events[i].Tags;
        var contentString = '';

        for (var j = 0; j < events.length; j++) {
            if (events[j].latlon.lat == position.lat && events[j].latlon.lon == position.lon) {
                name = events[j].Name;
                description = events[j].Description;
                loc = events[j].Location;
                time = events[j].Time;
                date = events[j].Date;
                tags = events[j].Tag;

                contentString = contentString + '<div id="content">'+
                '<div id="siteNotice">'+
                '</div>'+
                '<h3 id="firstHeading" class="firstHeading">' +
                name +
                '</h3>'+
                '<h4>Time:&nbsp' +
                time +
                '&nbspDate:&nbsp' +
                date +
                '</h4>' +
                '<h4>Location:&nbsp' +
                loc +
                '</h4><h4>Tags:&nbsp';
                for (var k = 0; k < tags.length; k++) {
                    contentString = contentString + tags[k] + "&nbsp";
                }
                contentString = contentString + '</h4>' +
                '<div id="bodyContent">'+
                '<p>' +
                description +
                '</p>' +
                '</div>'+
                '</div><hr>';
            }
        }
        contentStrings.push(contentString);
    }

    console.log("Total number of events: " + events.length);
    var infoWindow = new google.maps.InfoWindow(), marker, i;

    for (var i = 0; i < events.length; i++) {

        marker = new google.maps.Marker({
            position: events[i].latlon,
            map: map,
            title: events[i].Name
        });

        google.maps.event.addListener(marker, 'click', (function(marker, i) {
            return function() {
                infoWindow.setContent(contentStrings[i]);
                infoWindow.open(map, marker);
            }
        })(marker, i));
    }

}