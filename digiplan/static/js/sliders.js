// Variables
const SETTINGS_PARAMETERS = JSON.parse(document.getElementById("settings_parameters").textContent);
const SETTINGS_DEPENDENCY_MAP = JSON.parse(document.getElementById("settings_dependency_map").textContent);
const DEPENDENCY_PARAMETERS = JSON.parse(document.getElementById("dependency_parameters").textContent);
const panelContainer = document.getElementById("js-panel-container");
const panelSliders = document.querySelectorAll(".js-slider.js-slider-panel");
const powerPanelSliders = document.querySelectorAll(".js-slider.js-slider-panel.js-power-mix");
const sliderMoreLabels = document.querySelectorAll(".c-slider__label--more > .button");
const powerMixInfoBanner = document.getElementById("js-power-mix");

const powerIcons = {
      "s_h_1": `<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" height="16" width="16" viewBox="0 0 16 16"><path d="m5.22.89l-.18-.44-.45.16c-.13.05-3.13,1.17-4.11,3.39-.61,1.38.02,3,1.41,3.61.35.16.73.23,1.1.23.34,0,.67-.06.99-.19.68-.27,1.22-.78,1.51-1.45.98-2.22-.23-5.2-.28-5.32Zm-.63,4.92c-.39.88-1.42,1.28-2.3.9s-1.28-1.42-.9-2.3c.6-1.37,2.26-2.28,3.08-2.66.27.86.72,2.7.12,4.07Z"/><path d="m14.44,3.17l-.19-.44-.45.17c-.24.09-5.83,2.25-7.59,6.38-.51,1.19-.52,2.5-.04,3.69s1.4,2.13,2.59,2.64c.62.26,1.26.39,1.89.39,1.88,0,3.67-1.1,4.45-2.93,1.76-4.13-.55-9.66-.65-9.9Zm-.26,9.51c-.4.94-1.15,1.67-2.1,2.05-.95.38-1.99.37-2.93-.03s-1.67-1.15-2.05-2.1-.37-1.99.03-2.93c1.32-3.09,5.24-5.06,6.58-5.65.5,1.38,1.8,5.56.48,8.66Z"/></svg>`,
      "s_pv_ff_1": `<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" height="16" width="16" viewBox="0 0 16 16"><path d="m12.07,15v-2.95h3.23L11.94.86h-7.88L.71,12.05h3.22v2.95H.35v1h15.29v-1h-3.58ZM8.51,1.88h2.67l.61,2.03h-3.28V1.88Zm0,3.05h3.59l.61,2.03h-4.2v-2.03Zm0,3.05h4.5l.92,3.05h-5.42v-3.05ZM4.82,1.88h2.67v2.03h-3.28l.61-2.03Zm-.92,3.05h3.59v2.03H3.29l.61-2.03Zm-1.83,6.1l.92-3.05h4.5v3.05H2.07Zm2.88,1.02h6.1v2.95h-6.1v-2.95Z"/></svg>`,
      "s_pv_d_1": `<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" height="16" width="16" viewBox="0 0 16 16"><path d="m15.96,16l-3.91-2.36h.02v-2.92h3.23L11.94,0h-7.88L.71,10.71h3.22v2.92h.02L.04,16h15.92Zm-12.34-1l4.38-2.65,4.38,2.65H3.62ZM8.51.97h2.67l.61,1.95h-3.28V.97Zm0,2.92h3.59l.61,1.95h-4.2v-1.95Zm0,2.92h4.5l.92,2.92h-5.42v-2.92ZM4.82.97h2.67v1.95h-3.28l.61-1.95Zm-.92,2.92h3.59v1.95H3.29l.61-1.95Zm-1.83,5.85l.92-2.92h4.5v2.92H2.07Zm2.88.97h6.1v2.32l-3.05-1.85-3.05,1.85v-2.32Z"/></svg>`,
      "s_w_1": `<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" height="16" width="16" viewBox="0 0 16 16"><path class="cls-1" d="m7.5,0v4.05c-.85.23-1.48,1.01-1.48,1.93,0,.16.02.31.05.46l-3.21,1.85.5.87,3.17-1.83c.25.28.58.48.96.58v7.09H1.49v1h6.01s1,0,1,0h0s6.01,0,6.01,0v-1h-6.01v-7.09c.39-.1.74-.33,1-.63l3.26,1.88.5-.87-3.32-1.91s0,0,0,0c.03-.13.04-.26.04-.4,0-.92-.63-1.71-1.48-1.93V0h-1,0Zm.5,4.98c.55,0,.98.44.98,1s-.44,1-.98,1-.98-.44-.98-1,.44-1,.98-1Z"/></svg>`
};

const potentialPVLayers = ["potentialarea_pv_agriculture_lfa-off_region", "potentialarea_pv_road_railway_region"];
const potentialWindLayers = [
  "potentialarea_wind_stp_2018_vreg",
  "potentialarea_wind_stp_2027_repowering",
  "potentialarea_wind_stp_2027_search_area_forest_area",
  "potentialarea_wind_stp_2027_search_area_open_area",
  "potentialarea_wind_stp_2027_vr"
];
const potentialWindSwitches = document.querySelectorAll("#id_s_w_3, #id_s_w_4, #id_s_w_4_1, #id_s_w_4_2, #id_s_w_5, #id_s_w_5_1, #id_s_w_5_2");

const sectorSlider = document.querySelectorAll("#id_s_v_3, #id_s_v_4, #id_s_v_5, #id_w_d_wp_3, #id_w_d_wp_4, #id_w_d_wp_5, #id_w_v_3, #id_w_v_4, #id_w_v_5");

const sliderDependencies = {
  "id_w_d_s_1": "id_w_d_s_3",
  "id_w_z_s_1": "id_w_z_s_3",
  "id_v_iv_1": "id_v_iv_3"
};

// Setup

// Order matters. Start with the most specific, and end with most general sliders.
Array.from(Object.keys(SETTINGS_DEPENDENCY_MAP)).forEach(dependent_name => {
  const dependency_names = SETTINGS_DEPENDENCY_MAP[dependent_name];
  Array.from(dependency_names).forEach(dependency_name => {
    $("#id_" + dependency_name).ionRangeSlider({
        onChange: function (data) {
          const msg = eventTopics.DEPENDENCY_PANEL_SLIDER_CHANGE;
          PubSub.publish(msg, {
            dependent: dependent_name,
            dependency: dependency_name,
            data
          });
        }
      }
    );
  });
});
$(".js-slider.js-slider-panel.js-power-mix").ionRangeSlider({
    onChange: function (data) {
      PubSub.publish(eventTopics.POWER_PANEL_SLIDER_CHANGE, data);
    }
  }
);
$(potentialWindSwitches).on("change", function () {
  PubSub.publish(eventTopics.WIND_CONTROL_ACTIVATED);
});
$(".js-slider.js-slider-panel").ionRangeSlider({
    onChange: function (data) {
      PubSub.publish(eventTopics.PANEL_SLIDER_CHANGE, data);
    }
  }
);
$(sectorSlider).ionRangeSlider({
    onChange: function (data) {
      calculate_slider_value(data);
    }
  }
);

$(".js-slider.js-slider-panel").ionRangeSlider({
    onChange: function (data) {
      PubSub.publish(eventTopics.PANEL_SLIDER_CHANGE, data);
    }
  }
);
$(".form-check-input").on(
    'click', function (data) {
      toggleFormFields(data.target.id);
    }
);
$("#id_s_w_5_1").ionRangeSlider({
    onChange: function (data) {
      calculate_max_wind();
    }
  }
);
$("#id_s_w_5_2").ionRangeSlider({
    onChange: function (data) {
      calculate_max_wind();
    }
  }
);
$("#id_s_pv_ff_3").ionRangeSlider({
    onChange: function (data) {
      calculate_max_pv_ff();
    }
  }
);
$("#id_s_pv_ff_4").ionRangeSlider({
    onChange: function (data) {
      calculate_max_pv_ff();
    }
  }
);
$("#id_s_pv_d_3").ionRangeSlider({
    onChange: function (data) {
      let new_max = Math.round(Math.round(store.cold.slider_max.s_pv_d_3) * (data.from/100));
      $(`#id_s_pv_d_1`).data("ionRangeSlider").update({max:new_max});
    }
  }
);
$("#id_w_d_s_3").ionRangeSlider({
    onChange: function (data) {
      $(`#id_w_d_s_1`).data("ionRangeSlider").update({from:data.from});
    }
  }
);
$("#id_w_z_s_3").ionRangeSlider({
    onChange: function (data) {
      $(`#id_w_z_s_1`).data("ionRangeSlider").update({from:data.from});
    }
  }
);
$("#id_v_iv_3").ionRangeSlider({
    onChange: function (data) {
      $(`#id_v_iv_1`).data("ionRangeSlider").update({from:data.from});
    }
  }
);

$(".js-slider").ionRangeSlider();

Array.from(sliderMoreLabels).forEach(moreLabel => {
  moreLabel.addEventListener("click", () => {
    const sliderLabel = moreLabel.parentNode.parentNode.parentNode;
    PubSub.publish(eventTopics.MORE_LABEL_CLICK, sliderLabel);
  });
});

panelContainer.addEventListener("scroll", (e) => {
  document.documentElement.style.setProperty("--scrollPosition", panelContainer.scrollTop + "px");
});


// Subscriptions
PubSub.subscribe(eventTopics.STATES_INITIALIZED, updateSliderMarks);
subscribeToEvents(
  [eventTopics.STATES_INITIALIZED, eventTopics.POWER_PANEL_SLIDER_CHANGE],
  createPercentagesOfPowerSources
);
subscribeToEvents(
  [eventTopics.POWER_PANEL_SLIDER_CHANGE, eventTopics.PANEL_SLIDER_CHANGE],
  showActivePanelSliderOnPanelSliderChange
);
subscribeToEvents(
  [eventTopics.POWER_PANEL_SLIDER_CHANGE, eventTopics.PANEL_SLIDER_CHANGE],
  hidePotentialLayers
);
subscribeToEvents(
  [eventTopics.POWER_PANEL_SLIDER_CHANGE, eventTopics.PANEL_SLIDER_CHANGE],
  checkMainPanelSlider
);
PubSub.subscribe(eventTopics.MORE_LABEL_CLICK, showOrHideSidepanelsOnMoreLabelClick);
PubSub.subscribe(eventTopics.MORE_LABEL_CLICK, showOrHidePotentialLayersOnMoreLabelClick);
PubSub.subscribe(eventTopics.DEPENDENCY_PANEL_SLIDER_CHANGE, (msg, payload) => {
  const {dependent, dependency, data} = payload;
  const value = DEPENDENCY_PARAMETERS[dependency][dependent][data.from];
  const dependentDataElement = $("#id_" + dependent).data("ionRangeSlider");
  dependentDataElement.update({max: value});
});
PubSub.subscribe(eventTopics.PV_CONTROL_ACTIVATED, showPVLayers);
PubSub.subscribe(eventTopics.WIND_CONTROL_ACTIVATED, showWindLayers);


// Subscriber Functions

function checkMainPanelSlider(msg, data) {
  if (sliderDependencies.hasOwnProperty(data.input[0].id)) {
    let target = sliderDependencies[data.input[0].id];
    $('#' + target).data("ionRangeSlider").update({from:data.from});
  }
    if (data.input[0].id === "id_s_v_1") {
    $(`#id_s_v_3`).data("ionRangeSlider").update({from:data.from});
    $(`#id_s_v_4`).data("ionRangeSlider").update({from:data.from});
    $(`#id_s_v_5`).data("ionRangeSlider").update({from:data.from});
  }
  if (data.input[0].id === "id_w_d_wp_1") {
    $(`#id_w_d_wp_3`).data("ionRangeSlider").update({from:data.from});
    $(`#id_w_d_wp_4`).data("ionRangeSlider").update({from:data.from});
    $(`#id_w_d_wp_5`).data("ionRangeSlider").update({from:data.from});
  }
  if (data.input[0].id === "id_w_v_1") {
    $(`#id_w_v_3`).data("ionRangeSlider").update({from:data.from});
    $(`#id_w_v_4`).data("ionRangeSlider").update({from:data.from});
    $(`#id_w_v_5`).data("ionRangeSlider").update({from:data.from});
  }
}

function showOrHidePotentialLayersOnMoreLabelClick(msg, moreLabel) {
  const classes = ["active", "active-sidepanel"];
  const show = moreLabel.classList.contains(classes[0]);
  hidePotentialLayers();
  if (show) {
    const sliderLabel = moreLabel.getElementsByTagName("input")[0];
    if (sliderLabel.id === "id_s_pv_ff_1") {
      PubSub.publish(eventTopics.PV_CONTROL_ACTIVATED);
    }
    if (sliderLabel.id === "id_s_w_1") {
      PubSub.publish(eventTopics.WIND_CONTROL_ACTIVATED);
    }
  }
  return logMessage(msg);
}

function showOrHideSidepanelsOnMoreLabelClick(msg, moreLabel) {
  const classes = ["active", "active-sidepanel"];
  const hide = moreLabel.classList.contains(classes[0]) && moreLabel.classList.contains(classes[1]);
  if (hide) {
    moreLabel.classList.remove(...classes);
  } else {
    Array.from(panelSliders).forEach(item => item.parentNode.classList.remove(...classes));
    moreLabel.classList.add(...classes);
  }

  return logMessage(msg);
}

function showActivePanelSliderOnPanelSliderChange(msg, data) {
  Array.from(panelSliders).forEach(item => item.parentNode.classList.remove("active", "active-sidepanel"));
  const sliderLabel = data.input[0].parentNode;
  sliderLabel.classList.add("active");
  return logMessage(msg);
}

function createPercentagesOfPowerSources(msg) {
  let ids = [];
  let values = [];
  Array.from(powerPanelSliders).forEach(function (item) {
    ids.push(item.id);
    values.push($("#" + item.id).data().from);
  });
  const total = getTotalOfValues(values);
  const weights = getWeightsInPercent(values, total);
  const colors = getColorsByIds(ids);
  const icons = getIconsByIds(ids);
  updatePowerMix(weights, colors, icons);
  return logMessage(msg);
}

/* when the other forms get Status Quo marks, there needs to be an iteration over the forms! (line 117)*/
function updateSliderMarks(msg) {
  for (let [slider_name, slider_marks] of Object.entries(store.cold.slider_marks)) {
    let slider = $(`#id_${slider_name}`).data("ionRangeSlider");
    slider.update({
      onUpdate: function (data) {  // jshint ignore:line
        addMarks(data, slider_marks);
      }
    });
  }
  return logMessage(msg);
}

function showPVLayers(msg) {
  hidePotentialLayers();
  for (const layer of potentialPVLayers) {
    map.setLayoutProperty(layer, "visibility", "visible");
  }
  return logMessage(msg);
}

function calculate_slider_value(data) {
  if (data.input[0].id === "id_s_v_3" || data.input[0].id === "id_s_v_4" || data.input[0].id === "id_s_v_5") {
    let factor_hh = $("#id_s_v_3").data("ionRangeSlider").result.from;
    let factor_ind = $("#id_s_v_5").data("ionRangeSlider").result.from;
    let factor_cts = $("#id_s_v_4").data("ionRangeSlider").result.from;
    let demand_hh = store.cold.slider_per_sector.s_v_1.hh;
    let demand_ind = store.cold.slider_per_sector.s_v_1.ind;
    let demand_cts = store.cold.slider_per_sector.s_v_1.cts;
    let new_val = (factor_hh * demand_hh + factor_ind * demand_ind + factor_cts * demand_cts) / (demand_hh + demand_ind + demand_cts);
    $(`#id_s_v_1`).data("ionRangeSlider").update({from:new_val});
  }
  if (data.input[0].id === "id_w_d_wp_3" || data.input[0].id === "id_w_d_wp_4" || data.input[0].id === "id_w_d_wp_5") {
    let factor_hh = $("#id_w_d_wp_3").data("ionRangeSlider").result.from;
    let factor_ind = $("#id_w_d_wp_5").data("ionRangeSlider").result.from;
    let factor_cts = $("#id_w_d_wp_4").data("ionRangeSlider").result.from;
    let demand_hh = store.cold.slider_per_sector.w_d_wp_1.hh;
    let demand_ind = store.cold.slider_per_sector.w_d_wp_1.ind;
    let demand_cts = store.cold.slider_per_sector.w_d_wp_1.cts;
    let new_val = (factor_hh * demand_hh + factor_ind * demand_ind + factor_cts * demand_cts) / (demand_hh + demand_ind + demand_cts);
    $(`#id_w_d_wp_1`).data("ionRangeSlider").update({from:new_val});
  }
  if (data.input[0].id === "id_w_v_3" || data.input[0].id === "id_w_v_4" || data.input[0].id === "id_w_v_5") {
    let factor_hh = $("#id_w_v_3").data("ionRangeSlider").result.from;
    let factor_ind = $("#id_w_v_5").data("ionRangeSlider").result.from;
    let factor_cts = $("#id_w_v_4").data("ionRangeSlider").result.from;
    let demand_hh = store.cold.slider_per_sector.w_d_wp_1.hh;
    let demand_ind = store.cold.slider_per_sector.w_d_wp_1.ind;
    let demand_cts = store.cold.slider_per_sector.w_d_wp_1.cts;
    let new_val = (factor_hh * demand_hh + factor_ind * demand_ind + factor_cts * demand_cts) / (demand_hh + demand_ind + demand_cts);
    $(`#id_w_v_1`).data("ionRangeSlider").update({from:new_val});
  }
}

function calculate_max_wind() {
  let slider_one = $("#id_s_w_5_1").data("ionRangeSlider").result.from / 100;
  let slider_two = $("#id_s_w_5_2").data("ionRangeSlider").result.from / 100;
  let new_max = slider_one * Math.round(store.cold.slider_max.s_w_5_1) + slider_two * Math.round(store.cold.slider_max.s_w_5_2);
  $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(new_max)});
}

function calculate_max_pv_ff() {
  let slider_one = $("#id_s_pv_ff_3").data("ionRangeSlider").result.from / 100;
  let slider_two = $("#id_s_pv_ff_4").data("ionRangeSlider").result.from / 100;
  let new_max = slider_one * Math.round(store.cold.slider_max.s_pv_ff_3) + slider_two * Math.round(store.cold.slider_max.s_pv_ff_4);
  $(`#id_s_pv_ff_1`).data("ionRangeSlider").update({max:Math.round(new_max)});
}

function toggleFormFields(formfield_id) {
  if (formfield_id === "id_s_w_3") {
    if (document.getElementById("id_s_w_4").checked === false && document.getElementById("id_s_w_5").checked === false) {
      document.getElementById("id_s_w_3").checked = true;
    }
    else {
      document.getElementById("id_s_w_4").checked = false;
      document.getElementById("id_s_w_4_1").disabled = true;
      document.getElementById("id_s_w_4_2").disabled = true;
      document.getElementById("id_s_w_5").checked = false;
      $(`#id_s_w_5_1`).data("ionRangeSlider").update({block:true});
      $(`#id_s_w_5_2`).data("ionRangeSlider").update({block:true});
      $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_3)});
    }
  }
  if (formfield_id === "id_s_w_4") {
    if (document.getElementById("id_s_w_3").checked === false && document.getElementById("id_s_w_5").checked === false) {
      document.getElementById("id_s_w_4").checked = true;
    }
    else {
      if (document.getElementById("id_s_w_4_1").checked === true && document.getElementById("id_s_w_4_2").checked === true) {
        $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_1) + Math.round(store.cold.slider_max.s_w_4_2)});
      }
      if (document.getElementById("id_s_w_4_1").checked === false && document.getElementById("id_s_w_4_2").checked === true) {
        $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_2)});
      }
      if (document.getElementById("id_s_w_4_1").checked === true && document.getElementById("id_s_w_4_2").checked === false) {
        $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_1)});
      }
      document.getElementById("id_s_w_3").checked = false;
      document.getElementById("id_s_w_4_1").disabled = false;
      document.getElementById("id_s_w_4_2").disabled = false;
      document.getElementById("id_s_w_5").checked = false;
      $(`#id_s_w_5_1`).data("ionRangeSlider").update({block: true});
      $(`#id_s_w_5_2`).data("ionRangeSlider").update({block: true});
    }
  }
  if (formfield_id === "id_s_w_4_1") {
    if (document.getElementById("id_s_w_4_2").checked === false) {
      document.getElementById("id_s_w_4_1").checked = true;
      $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_1)});
    }
    if (document.getElementById("id_s_w_4_1").checked === true && document.getElementById("id_s_w_4_2").checked === true) {
      $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_1) + Math.round(store.cold.slider_max.s_w_4_2)});
    }
    if (document.getElementById("id_s_w_4_1").checked === false && document.getElementById("id_s_w_4_2").checked === true) {
      $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_2)});
    }
  }
  if (formfield_id === "id_s_w_4_2") {
    if (document.getElementById("id_s_w_4_1").checked === false) {
      document.getElementById("id_s_w_4_2").checked = true;
      $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_2)});
    }
    if (document.getElementById("id_s_w_4_1").checked === true && document.getElementById("id_s_w_4_2").checked === true) {
      $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_1) + Math.round(store.cold.slider_max.s_w_4_2)});
    }
    if (document.getElementById("id_s_w_4_1").checked === true && document.getElementById("id_s_w_4_2").checked === false) {
      $(`#id_s_w_1`).data("ionRangeSlider").update({max:Math.round(store.cold.slider_max.s_w_4_1)});
    }
  }
  if (formfield_id === "id_s_w_5") {
    if (document.getElementById("id_s_w_3").checked === false && document.getElementById("id_s_w_4").checked === false) {
      document.getElementById("id_s_w_5").checked = true;
    }
    else {
      document.getElementById("id_s_w_3").checked = false;
      document.getElementById("id_s_w_4").checked = false;
      document.getElementById("id_s_w_4_1").disabled = true;
      document.getElementById("id_s_w_4_2").disabled = true;
      $(`#id_s_w_5_1`).data("ionRangeSlider").update({block:false});
      $(`#id_s_w_5_2`).data("ionRangeSlider").update({block:false});
      calculate_max_wind();
    }
  }
}

function showWindLayers(msg) {
  hidePotentialLayers();
  if (document.getElementById("id_s_w_3").checked) {
    map.setLayoutProperty("potentialarea_wind_stp_2018_vreg", "visibility", "visible");
  }
  if (document.getElementById("id_s_w_4").checked) {
    if (document.getElementById("id_s_w_4_1").checked) {
      map.setLayoutProperty("potentialarea_wind_stp_2027_vr", "visibility", "visible");
    }
    if (document.getElementById("id_s_w_4_2").checked) {
      map.setLayoutProperty("potentialarea_wind_stp_2027_repowering", "visibility", "visible");
    }
  }
  if (document.getElementById("id_s_w_5").checked) {
    map.setLayoutProperty("potentialarea_wind_stp_2027_search_area_open_area", "visibility", "visible");
    map.setLayoutProperty("potentialarea_wind_stp_2027_search_area_forest_area", "visibility", "visible");
  }
  return logMessage(msg);
}

function hidePotentialLayers(msg) {
  for (const layer of potentialPVLayers.concat(potentialWindLayers)) {
    map.setLayoutProperty(layer, "visibility", "none");
  }
  return logMessage(msg);
}


// Helper Functions

function getColorsByIds(ids) {
  let colors = [];
  for (let id of ids) {
    const cleanedId = id.replace(/^id_/, "");
    colors.push(SETTINGS_PARAMETERS[cleanedId].color);
  }
  return colors;
}

function getIconsByIds(ids) {
  let icons = [];
  for (let id of ids) {
    const cleanedId = id.replace(/^id_/, "");
    icons.push(powerIcons[cleanedId]);
  }
  return icons;
}

function updatePowerMix(weights, colors, icons) {
  const msg = "Unequal amount of weights and colors";
  if (weights.length !== colors.length) throw new Error(msg);
  let html = `<div class="power-mix__chart"><div class="power-mix__icons">`;
  for (const index of weights.keys()) {
    html += `<div style="width: ${weights[index]}%;">${icons[index]}</div>`;
  }
  html += `</div><div class="power-mix__colors">`;
  for (const index of weights.keys()) {
    html += `<div style="width: ${weights[index]}%; background-color: ${colors[index]}; text-align: center; height: 1rem;"></div>`;
  }
  html += `</div></div>`;
  powerMixInfoBanner.innerHTML = html;
}

function getWeightsInPercent(values, total) {
  let weights = [];
  for (const value of values) {
    weights.push((parseInt(value) / parseInt(total)) * 100);
  }
  return weights;
}

function getTotalOfValues(values) {
  let total = 0;
  for (const value of values) {
    total += value;
  }
  return total;
}

function convertToPercent(num, min, max) {
  return (num - min) / (max - min) * 100;
}

function addMarks(data, marks) {
  let html = "";

  for (let i = 0; i < marks.length; i++) {
    let percent = convertToPercent(marks[i][1], data.min, data.max);
    // Fix percentage due to offset
    percent = percent - 2.5 - (3.5 * percent / 100);
    html += `<span class="showcase__mark" style="left: ${percent}%">`;
    html += marks[i][0];
    html += '</span>';
  }

  data.slider.append(html);
}


$(document).ready(function () {
  document.getElementById("id_s_w_4_1").checked = true;
  document.getElementById("id_s_w_4_1").disabled = true;
  document.getElementById("id_s_w_4_2").disabled = true;
  document.getElementById("id_s_w_3").checked = true;
  $(`#id_s_w_5_1`).data("ionRangeSlider").update({from:13, block:true});
  $(`#id_s_w_5_2`).data("ionRangeSlider").update({from:13, block:true});
  document.getElementById("id_s_w_5_1").disabled = true;
  document.getElementById("id_s_w_5_2").disabled = true;
  $(`#id_s_h_1`).data("ionRangeSlider").update({block:true});
  calculate_max_pv_ff();
});
