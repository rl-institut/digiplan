// Variables

const detailLayers = Array.from(document.getElementsByClassName("static-layer"));


// Event Handler

map.on("load", function () {
  // Layers Detail Panel
  detailLayers.map(layerForm => {
    layerForm.addEventListener("change", () => {
      PubSub.publish(eventTopics.DETAIL_LAYER_SWITCH_CLICK, {layerForm});
    });
  });
  $(".layer-setup").find(".js-range-slider").change(function() {
    const layerForm = $(this).closest("form");
    PubSub.publish(eventTopics.DETAIL_LAYER_SLIDER_CHANGE, {layerForm});
  });
});


// Subscriptions

// On Initial Load
PubSub.subscribe(eventTopics.STATES_INITIALIZED, hideDetailLayers);

// Layers Detail Panel
PubSub.subscribe(eventTopics.DETAIL_LAYER_SWITCH_CLICK, checkLayerOfGivenLayerForm);
PubSub.subscribe(eventTopics.DETAIL_LAYER_SLIDER_CHANGE, filterChanged);

// Subscriber Functions

function hideDetailLayers(msg) {
  detailLayers.map(layer => {
    turn_off_layer(layer);
    $(layer).find(".switch-input")[0].checked = false;
  });
  return logMessage(msg);
}

function showDetailLayers(msg) {
  for (let i = 0; i < detailLayers.length; i++) {
    $(detailLayers[i]).find(".switch-input")[0].checked = (store.cold.staticState & 2 ** i) === 2 ** i;
    check_layer(detailLayers[i]);
  }
  return logMessage(msg);
}

function checkLayerOfGivenLayerForm(msg, {layerForm}) {
  check_layer(layerForm);
  store.cold.staticState = get_static_state();
  return logMessage(msg);
}

function setDetailLayersOnDetailLayersSwitchClick(msg) {
  detailLayers.map(layer => {
    turn_off_layer(layer);
    $(layer).find(".switch-input")[0].checked = false;
  });
  store.cold.staticState = get_static_state();
  return logMessage(msg);
}

function filterChanged(msg, {layerForm}) {
  const layer_id = get_layer_id(layerForm);
  const filter = get_layer_filter(layerForm);
  const layers = get_map_layer_ids(layer_id);
  $.each(layers, function (i, layer) {
    if (filter != null) {
      set_filter(layer, filter);
    }
  })
  return logMessage(msg);
}


// Helper Functions

function get_layer_id(layer_form) {
  return $(layer_form).find(".switch-input")[0].id;
}

function check_layer(layer_form) {
  if ($(layer_form).find(".switch-input")[0].checked) {
    const layer_id = get_layer_id(layer_form)
    const activated_layers = turn_on_layer(layer_form);
    const layers = map.getStyle().layers.filter(layer => layer["id"].startsWith(layer_id));
    const deactivatedLayers = layers.filter(layer => !activated_layers.includes(layer["id"]));
    const waiting = () => {
      if (!map.isStyleLoaded()) {
        requestAnimationFrame(waiting);
      } else {
        $.each(deactivatedLayers, function (i, layer) {
          map.setLayoutProperty(layer["id"], "visibility", "none");
        })
      }
    };
    waiting();
  } else {
    turn_off_layer(layer_form);
  }
}


function turn_off_layer(layer_form) {
  const layer_id = get_layer_id(layer_form);
  const layers = map.getStyle().layers.filter(layer => layer["id"].startsWith(layer_id));
  $.each(layers, function (i, layer) {
    map.setLayoutProperty(layer["id"], "visibility", "none");
  })
}

function turn_on_layer(layer_form) {
  const layer_id = get_layer_id(layer_form);
  const filter = get_layer_filter(layer_form);
  const layers = get_map_layer_ids(layer_id);
  $.each(layers, function (i, layer) {
    map.setLayoutProperty(layer, "visibility", "visible");
    if (filter != null) {
      set_filter(layer, filter);
    }
  })
  return layers;
}

function get_map_layer_ids(layer_id) {
  let layers;
  if (store.cold.useDistilledMVTs) {
    layers = [layer_id, layer_id + "_distilled"];
  } else {
    layers = [layer_id];
  }
  return layers;
}

function get_layer_filter(layer_form) {
  let filter = $(layer_form).find(".js-range-slider");
  if (filter.length > 0) {
    filter_name = filter[0].id.slice(3);
    result = filter.data("ionRangeSlider").result;
    return {
      name: filter_name,
      from: result.from,
      to: result.to
    }
  }
}

function set_filter(layer, filter) {
  lower_bound = [">=", ["get", filter.name], filter.from];
  upper_bound = ["<=", ["get", filter.name], filter.to];
  map.setFilter(layer, ["all", lower_bound, upper_bound]);
}
