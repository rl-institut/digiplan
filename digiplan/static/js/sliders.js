// Variables
const SETTINGS_PARAMETERS = JSON.parse(document.getElementById("settings_parameters").textContent);
const SETTINGS_DEPENDENCY_MAP = JSON.parse(document.getElementById("settings_dependency_map").textContent);
const DEPENDENCY_PARAMETERS = JSON.parse(document.getElementById("dependency_parameters").textContent);
const panelContainer = document.getElementById("js-panel-container");
const panelSliders = document.querySelectorAll(".js-slider.js-slider-panel");
const powerPanelSliders = document.querySelectorAll(".js-slider.js-slider-panel.js-power-mix");
const sliderMoreLabels = document.querySelectorAll(".c-slider__label--more > .button");
const powerMixInfoBanner = document.getElementById("js-power-mix");


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
  "id_w_z_wp_1": "id_w_z_wp_3",
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
$("#id_w_z_wp_3").ionRangeSlider({
    onChange: function (data) {
      $(`#id_w_z_wp_1`).data("ionRangeSlider").update({from:data.from});
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
  updatePowerMix(weights, colors);
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
    let factor_ind = $("#id_s_v_4").data("ionRangeSlider").result.from;
    let factor_cts = $("#id_s_v_5").data("ionRangeSlider").result.from;
    let demand_hh = store.cold.slider_per_sector.s_v_1.hh;
    let demand_ind = store.cold.slider_per_sector.s_v_1.ind;
    let demand_cts = store.cold.slider_per_sector.s_v_1.cts;
    let new_val = (factor_hh * demand_hh + factor_ind * demand_ind + factor_cts * demand_cts) / (demand_hh + demand_ind + demand_cts);
    $(`#id_s_v_1`).data("ionRangeSlider").update({from:new_val});
  }
  if (data.input[0].id === "id_w_d_wp_3" || data.input[0].id === "id_w_d_wp_4" || data.input[0].id === "id_w_d_wp_5") {
    let factor_hh = $("#id_w_d_wp_3").data("ionRangeSlider").result.from;
    let factor_ind = $("#id_w_d_wp_4").data("ionRangeSlider").result.from;
    let factor_cts = $("#id_w_d_wp_5").data("ionRangeSlider").result.from;
    let demand_hh = store.cold.slider_per_sector.w_d_wp_1.hh;
    let demand_ind = store.cold.slider_per_sector.w_d_wp_1.ind;
    let demand_cts = store.cold.slider_per_sector.w_d_wp_1.cts;
    let new_val = (factor_hh * demand_hh + factor_ind * demand_ind + factor_cts * demand_cts) / (demand_hh + demand_ind + demand_cts);
    $(`#id_w_d_wp_1`).data("ionRangeSlider").update({from:new_val});
  }
  if (data.input[0].id === "id_w_v_3" || data.input[0].id === "id_w_v_4" || data.input[0].id === "id_w_v_5") {
    console.log("here");
    let factor_hh = $("#id_w_v_3").data("ionRangeSlider").result.from;
    let factor_ind = $("#id_w_v_4").data("ionRangeSlider").result.from;
    let factor_cts = $("#id_w_v_5").data("ionRangeSlider").result.from;
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

function updatePowerMix(weights, colors) {
  const msg = "Unequal amount of weights and colors";
  if (weights.length !== colors.length) throw new Error(msg);
  let html = `<div class="power-mix__chart"><div class="power-mix__icons">`;
  for (const index of weights.keys()) {
    html += `<div style="width: ${weights[index]}%;"><svg width="16" height="16" version="1.1" fill="currentColor" viewBox="0 0 16.933 16.933" xmlns="http://www.w3.org/2000/svg"><path d="m4.3692 1.0589-3.4923 11.64h0.71107 2.6443v3.176h1.0589v-3.176h6.3516v3.176h1.0563v-3.176h3.3574l-3.4918-11.64h-8.1954zm0.78703 1.0583h2.7812v2.1151h-3.4163l0.6351-2.1151zm3.8401 0h2.7812l0.6351 2.1151h-3.4163v-2.1151zm-4.793 3.174h3.7341v2.1172h-4.3692l0.6351-2.1172zm4.793 0h3.7341l0.6351 2.1172h-4.3692v-2.1172zm-5.7459 3.1755h4.6871v3.176h-5.6405l0.95343-3.176zm5.7459 0h4.6871l0.95343 3.176h-5.6405v-3.176z"/></svg></div>`;
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
    const percent = convertToPercent(marks[i][1], data.min, data.max);
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
