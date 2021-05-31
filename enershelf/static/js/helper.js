// Global Helper Functions


// Slider Helper Functions

function getSliderValueById(slider_id) {
  const slider_index = $("#" + slider_id).find("input").val();
  return $("#" + slider_id).parent().parent().parent().find("ul").children().get(slider_index).textContent;
}

function getSliderValueByElement(element) {
  const sliderInput = element[0].querySelector(".slider input");
  const sliderIndex = sliderInput === null ? element.querySelector(".slider input").value : sliderInput.value;
  return $(element).find("ul").children().get(sliderIndex).textContent;
}

function getSliderIndexById(slider_id, value) {
  return $("#" + slider_id).parent().parent().parent().find("ul").children().map(function() { return this.textContent; }).get().indexOf(value);
}

function isSliderElement(element) {
  const sliderInputFn = element[0].querySelector(".slider input");
  const sliderInput = sliderInputFn === null ? element.querySelector(".slider input") : sliderInputFn;
  return sliderInput ? true : false;
}


// Following functions get called by functions OUTSIDE of this file

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

function logMessage(msg) {
  if (store.cold.debugMode) {
    let caller = arguments.callee.caller;
    if (typeof caller === "function") {
      caller = caller.toString().substr("function ".length);
      caller = caller.substr(0, caller.indexOf("("));
    }
    const whatCalledWho = `${msg} triggered\n${caller}`;
    console.log(whatCalledWho);
    return whatCalledWho;
  }
}


// Following functions get called by functions OUTSIDE & INSIDE of this file

function turn_off_layer(layer_form) {
  const layer_id = get_layer_id(layer_form);
  const layers = map.getStyle().layers.filter(layer => layer["id"].startsWith(layer_id));
  $.each(layers, function (i, layer) {
    map.setLayoutProperty(layer["id"], "visibility", "none");
  })
}

function turn_on_layer(layer_form) {
  const layer_id = get_layer_id(layer_form);
  const layer_setup = get_layer_setup(layer_form);
  let layers;
  if (layer_setup == null) {
    if (store.cold.useDistilledMVTs) {
      layers = [layer_id, layer_id + "_distilled"];
    } else {
      layers = [layer_id];
    }
  } else {
    layers = [layer_id + "-" + layer_setup.join("-")];
  }
  $.each(layers, function (i, layer) {
    if (isSliderElement(layer_form)) {
      const valueNow = getSliderValueByElement(layer_form);
      store.cold.wind_distance = valueNow;
      map.setLayoutProperty(`${layer_id}-wind_distance=${valueNow}`, "visibility", "visible");
    } else {
      map.setLayoutProperty(layer, "visibility", "visible");
    }

  })
  return layers;
}


// Following functions get called by functions INSIDE of this file

function get_layer_id(layer_form) {
  return $(layer_form).find(".switch-input")[0].id;
}

function get_layer_setup(layer_form) {
  let setup = $(layer_form).find(".layer-setup");
  if (setup.length > 0) {
    let layer_setup = [];
    setup.children().each(function () {
      const setup_id = $(layer_form).find(".slider")[0].id;
      const value = getSliderValueByElement(layer_form);
      layer_setup.push(setup_id + "=" + value);
    });
    return layer_setup;
  }
}
