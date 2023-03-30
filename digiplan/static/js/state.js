// Subscriptions

PubSub.subscribe(mapEvent.MAP_LOADED, init_map_location);
PubSub.subscribe(mapEvent.MAP_LAYERS_LOADED, init_states);


const store = initStore();

function initStore() {
  const store_cold_init = JSON.parse(document.getElementById("store_cold_init").textContent);
  return new Store(store_cold_init);
}


// Subscriber Functions

function init_states(msg) {
  const url_states = get_states_from_url();
  store.cold.domain = url_states.domain;

  // Layers
  if ("static" in url_states) {
    store.cold.staticState = url_states.static;
  }

  PubSub.publish(eventTopics.STATES_INITIALIZED);
  return logMessage(msg);
}

function init_map_location(msg) {
  const url_states = get_states_from_url();
  if ("x" in url_states && "y" in url_states && "z" in url_states) {
    map.flyTo({
      center: [url_states.x, url_states.y],
      zoom: url_states.z,
      essential: true
    });
  }
  return logMessage(msg);
}


// Helper Functions

function get_static_state() {
  let static_state = 0;
  for (let i = 0; i < detailLayers.length; i++) {
    if ($(detailLayers[i]).find(layerInputClass)[0].checked) {
      static_state += 2 ** i;
    }
  }
  return static_state;
}

function get_states_from_url() {
  // Read url and split into domain and GET parameters
  const url = window.location !== window.parent.location ? document.referrer : document.location.href;
  let params_raw = url.split("?");
  const params = {"domain": params_raw[0]};
  if (params_raw.length < 2) {
    return params;
  }

  // Extract all parameters as dict
  params_raw = params_raw[1].split("&");
  for (let i = 0; i < params_raw.length; i++) {
    const k_v_raw = params_raw[i].split("=");
    params[k_v_raw[0]] = k_v_raw[1];
  }
  return params;
}
