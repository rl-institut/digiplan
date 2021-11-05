
const state_filter = $("#id_state");
const district_filter = $("#id_district");

state_filter.on("change", function () {
  PubSub.publish(eventTopics.STATE_FILTER_CHANGE, state_filter.val());
});
district_filter.on("change", function () {
  PubSub.publish(eventTopics.DISTRICT_FILTER_CHANGE);
});

PubSub.subscribe(eventTopics.STATE_FILTER_CHANGE, change_districts);
PubSub.subscribe(eventTopics.DISTRICT_FILTER_CHANGE, change_region_filter);

function change_districts(msg, states) {
  if (states.length == 0) {
    district_filter.select2().prop("disabled", true);
    return logMessage(msg);
  }
  $.ajax({
    type: "GET",
    url: "districts",
    dataType: 'json',
    data: {"states": states},
    success: function(results) {
      district_filter.find('option').remove().end();
      $.each(results.districts, function (i, district) {
        district_filter.append(
          $('<option>', {
            value: district,
            text : district
          })
        );
      });
      district_filter.select2().prop("disabled", false);
      PubSub.publish(eventTopics.DISTRICT_FILTER_CHANGE);
    }
  });
  return logMessage(msg);
}

function change_region_filter(msg) {
  $.each(detailLayers, function(i, layerForm) {
    layer_id = get_layer_id(layerForm);
    if (store.cold.region_filter_layers.includes(layer_id)) {
      PubSub.publish(eventTopics.DETAIL_LAYER_SELECT_CHANGE, {layerForm});
    }
  });
  return logMessage(msg);
}
