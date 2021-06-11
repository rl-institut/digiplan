

var popup_count = 0;

function add_popup(layer_id, fields) {
  map.on("click", layer_id, function (e) {
    var coordinates = e.features[0].geometry.coordinates.slice();
    var template = $($("#popup_template").prop("content")).find("div");
    var clone = template.clone();
    clone.find("h3").text("Header");
    var table = clone.find("table");
    for (var label in fields) {
      key = fields[label];
      value = e.features[0].properties[key];
      row = $("<tr>")
      row.append($("<td>").text(label))
      row.append($("<td>").text(value));
      table.append(row);
    }
    new mapboxgl.Popup().setLngLat(coordinates).setHTML(clone.html()).addTo(map);
  });
}
