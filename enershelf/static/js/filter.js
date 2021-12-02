'use strict';

const state_filter = $("#id_state");
const district_filter = $("#id_district");

state_filter.on("change", function () {
  PubSub.publish(eventTopics.STATE_FILTER_CHANGE, state_filter.val());
});
district_filter.on("change", function () {
  PubSub.publish(eventTopics.DISTRICT_FILTER_CHANGE);
});

PubSub.subscribe(eventTopics.STATE_FILTER_CHANGE, activate_state);
PubSub.subscribe(eventTopics.DISTRICT_FILTER_CHANGE, change_region_filter);


function activate_state(msg, state) {
  if (state.length == 0) {
    district_filter.prop("disabled", true);
    return logMessage(msg);
  }
  $.ajax({
    type: "GET",
    url: "state",
    dataType: 'json',
    data: {"state": state},
    success: function(results) {
      map.flyTo(
        {
          center: results.center,
          zoom: store.cold.zoom_levels.state[0],
          speed: 0.5
        }
      );

      district_filter.find('option').remove().end();
      $.each(results.districts, function (i, district) {
        district_filter.append(
          $('<option>', {
            value: district,
            text : district
          })
        );
      });
      district_filter.prop("disabled", false);
      PubSub.publish(eventTopics.DISTRICT_FILTER_CHANGE);
    }
  });
  return logMessage(msg);
}

function change_region_filter(msg) {
  $.each(detailLayers, function(i, layerForm) {
    let layer_id = get_layer_id(layerForm);
    if (store.cold.region_filter_layers.includes(layer_id)) {
      PubSub.publish(eventTopics.DETAIL_LAYER_SELECT_CHANGE, {layerForm});
    }
  });
  return logMessage(msg);
}
