function add_popup(layer_id, fields, template_id="default") {
  map.on("click", layer_id, function (e) {
    let coordinates;
    // Check if popup already exists:
    if ($('.mapboxgl-popup').length > 0) {return;}

    if ("lat" in e.features[0].properties) {
      // Get coordinates from lat/lon:
      coordinates = [e.features[0].properties.lat, e.features[0].properties.lon];
    } else {
      // Get coordinates from geometry:
      coordinates = e.lngLat;
    }
    var template = $($("#" + template_id + "_popup").prop("content")).find("div");
    var clone = template.clone();
    var table = clone.find("table");
    for (var label in fields) {
      const key = fields[label];
      const value = e.features[0].properties[key];
      let row = $("<tr>");
      row.append($("<td>").text(label));
      row.append($("<td>").text(value));
      table.append(row);
    }
    new maplibregl.Popup().setLngLat(coordinates).setHTML(clone.html()).addTo(map);
  });
}

$(document).ready(function() {
  $('#js-intro-modal').modal('show');
});
