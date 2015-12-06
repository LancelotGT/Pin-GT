// helper functions for show_entries.html
// mainly related to Google Map

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: campusPosition,
    zoom: 16,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
  });
  customizeMap();

  map.addListener('click', function(e) {
    $('#myModal').modal('toggle');
    $('#savePin').click(function() {
        var name = $("input[name=Name]").val();
        var date = $("input[name=Date]").val();
        var time = $("input[name=Time]").val();
        var tags = $("input[name=Tags]").val();
        var location = $("input[name=Location]").val();
        var description = $("textarea[name=Description]").val();
        var latlon = {'lat': e.latLng.lat(), 'lon': e.latLng.lng()};
        postEvent(name, date, time, tags, location, latlon, description);
        placeMarkerAndPanTo(e.latLng, map, name, time, date, location, tags, description);
    })
  });
}

// turn off road labels and change some colors for the map
function customizeMap() {
  map.set('styles', [
  {
    featureType: 'road',
    elementType: 'geometry',
    stylers: [
      { color: '#000000' },
      { weight: 0.3 }
    ]
  }, {
    featureType: 'road',
    elementType: 'labels',
    stylers: [
      { saturation: -100 },
      { invert_lightness: true }
    ]
  }, {
    featureType: 'landscape',
    elementType: 'geometry',
    stylers: [
      { hue: '#ffff00' },
      { gamma: 1.4 },
      { saturation: 82 },
      { lightness: 20 }
    ]
  }, {
    featureType: 'poi.school',
    elementType: 'geometry',
    stylers: [
      { hue: '#fff700' },
      { lightness: -15 },
      { saturation: 99 }
    ]
  }, {
    featureType: 'road',
    elementType: 'labels',
    stylers: [{visibility: 'off'}]
  }
]);

}
function placeMarkerAndPanTo(latlng, map, name, time, date, loc, tags, description) {
    var iconBase = 'https://maps.google.com/mapfiles/kml/shapes/';
    var marker = new google.maps.Marker({
        position: latlng,
        map: map,
        title: name,
        icon: iconBase + 'schools_maps.png'
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

    tags = tags.split(';');
    for (var k = 0; k < tags.length; k++) {
        contentString = contentString + tags[k] + "&nbsp";
    }
    contentString = contentString + '</h4>' +
    '<div id="bodyContent">'+
    '<p>' +
    description +
    '</p>' +
    '</div>'+
    '</div><hr>' +
    '<button onclick="deleteEvent(' +
    activityId +
    ')">Delete event</button>';

    var infoWindow = new google.maps.InfoWindow();
    infoWindow.setContent(contentString);
    google.maps.event.addListener(marker, 'click', (function(marker) {
        return function() {
            infoWindow.setContent(contentString);
            infoWindow.open(map, marker);
        }
    })(marker));
    map.panTo(latlng);
    location.reload();
}

function getEvents(startDate, endDate, tag) {

    // add more filter options here
    var input = {
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

function postEvent(name, date, time, tags, location, latlon, description) {

    // add more filter options here
    var input = {
        'name': name,
        'date': date,
        'time': time,
        'tags': tags.split(';'),
        'location': location,
        'latlon': latlon,
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

function edit(i) {
    var event = events[i];
    $("#edit_name").val(event.Name);
    $("#edit_date").val(event.Date);
    $("#edit_time").val(event.Time);
    $("#edit_tags").val(event.Tag.join(";"));
    $("#edit_loc").val(event.Location);
    $("#edit_desc").html(event.Description);
    $('#editModal').modal('toggle');
}

function subscribe(i) {
    var actID = events[i].activityId;
    var input = {
        'activityID': activityId,
    }
    $.ajax({
        url: '/notification',
        method: "POST",
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(input),
        context: document.body,
        success: function(data) {
            console.log(data);
        }
    });
}

function editEvent(activityId, name, date, time, tags, location, description) {

    var input = {
        'activityID': activityId,
        'name': name,
        'date': date,
        'time': time,
        'tags': tags.split(';'),
        'location': location,
        'description': description
    }

    $.ajax({
        url: '/events',
        method: "UPDATE",
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(input),
        context: document.body,
        success: function(data) {
            initMap();
            getEvents(start_date, end_date, $('#tags option:selected').text());
        }
    });
}

function deleteEvent(activityId) {
    var input = {
        'activityID': activityId
    }

    $.ajax({
        url: '/events',
        method: "DELETE",
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(input),
        context: document.body,
        success: function(data) {
            initMap();
            getEvents(start_date, end_date, $('#tags option:selected').text());
        }
    });
}

function addEventInfo(data) {
    events = data.events // An array of events
    var contentStrings = [];
    var names = [];
    var descriptions = [];
    var locs = [];

    for (var i = 0; i < events.length; i++) {
        var name = events[i].Name;
        var description = events[i].Description;
        var position = events[i].latlon;
        var loc = events[i].Location;
        var tags = events[i].Tags;
        var contentString = '';

        for (var j = 0; j < events.length; j++) {
            if (events[j].latlon[1] == position[1] && events[j].latlon[0] == position[0]) {
                name = events[j].Name;
                activityId = events[j].ActivityId;
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
                '</div><hr>' +
                '<button onclick="subscribe(' +
                j +
                ')">subscribe</button>' +
                '<button onclick="edit(' +
                j +
                ')">Edit event</button>' +
                '<button onclick="deleteEvent(' +
                activityId +
                ')">Delete event</button>';
            }
        }
        contentStrings.push(contentString);
    }

    console.log("Total number of events: " + events.length);
    var infoWindow = new google.maps.InfoWindow(), marker, i;

    for (var i = 0; i < events.length; i++) {
        var iconBase = 'https://maps.google.com/mapfiles/kml/shapes/';
        var location = {
            'lat': events[i].latlon[1],
            'lng': events[i].latlon[0]
        }

        marker = new google.maps.Marker({
            position: location,
            map: map,
            title: events[i].Name,
            icon: iconBase + 'schools_maps.png'
        });

        google.maps.event.addListener(marker, 'click', (function(marker, i) {
            return function() {
                infoWindow.setContent(contentStrings[i]);
                infoWindow.open(map, marker);
            }
        })(marker, i));
    }

}