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
  $(".layer-setup").find(".slider").on("changed.zf.slider", function () {
    const layerForm = $(this).closest("form");
    PubSub.publish(eventTopics.DETAIL_LAYER_SLIDER_CHANGE, {layerForm});
  });
});


// Subscriptions

// On Initial Load
PubSub.subscribe(eventTopics.STATES_INITIALIZED, hideDetailLayers);

// Layers Detail Panel
PubSub.subscribe(eventTopics.DETAIL_LAYER_SWITCH_CLICK, checkLayerOfGivenLayerForm);

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

function setDetailLayersOnDetailLayersSwitchClick (msg) {
  detailLayers.map(layer => {
    turn_off_layer(layer);
    $(layer).find(".switch-input")[0].checked = false;
  });
  store.cold.staticState = get_static_state();
  return logMessage(msg);
}


// Helper Functions
