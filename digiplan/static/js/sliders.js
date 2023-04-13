// Variables
const SETTINGS_PARAMETERS = JSON.parse(document.getElementById("settings_parameters").textContent);
const SETTINGS_DEPENDENCY_MAP = JSON.parse(document.getElementById("settings_dependency_map").textContent);
const DEPENDENCY_PARAMETERS = JSON.parse(document.getElementById("dependency_parameters").textContent);
const panelContainer = document.getElementById("js-panel-container");
const panelSliders = document.querySelectorAll(".js-slider.js-slider-panel");
const powerPanelSliders = document.querySelectorAll(".js-slider.js-slider-panel.js-power-mix");
const sliderMoreLabels = document.querySelectorAll(".c-slider__label--more > .button");
const powerMixInfoBanner = document.getElementById("js-power-mix");


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
      const msg = eventTopics.POWER_PANEL_SLIDER_CHANGE;
      PubSub.publish(msg, data);
    }
  }
);
$(".js-slider.js-slider-panel").ionRangeSlider({
    onChange: function (data) {
      const msg = eventTopics.PANEL_SLIDER_CHANGE;
      PubSub.publish(msg, data);
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
PubSub.subscribe(eventTopics.MORE_LABEL_CLICK, showOrHideSidepanelsOnMoreLabelClick);
PubSub.subscribe(eventTopics.DEPENDENCY_PANEL_SLIDER_CHANGE, (msg, payload) => {
  const {dependent, dependency, data} = payload;
  const value = DEPENDENCY_PARAMETERS[dependency][dependent][data.from];
  const dependentDataElement = $("#id_" + dependent).data("ionRangeSlider");
  dependentDataElement.update({max: value});
});


// Subscriber Functions

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

$('#settings').submit(false);

function sendSettings() {
  var form = document.getElementById("settings");
  var formData = new FormData(form); // jshint ignore:line
  $.ajax({
      url : "",
      type : "POST",
      processData: false,
      contentType: false,
      data : formData,
      success : function(json) {
        $('#post-text').val('');
        console.log(json);
      },
  });
}
