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
subscribeToEventTopicsGroup(
  [eventTopics.STATES_INITIALIZED, eventTopics.POWER_PANEL_SLIDER_CHANGE],
  createPercentagesOfPowerSources
);
subscribeToEventTopicsGroup(
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
    html += `<div style="width: ${weights[index]}%;"><svg width="16" height="16" version="1.1" fill="currentColor" viewBox="0 0 16.933 16.933" xmlns="http://www.w3.org/2000/svg"><path d="M9.3,15.9H1.3L2.8,5h5.2L9.3,15.9z M2.3,15h6L7.1,5.9H3.5L2.3,15z"/><path d="M6.8,4.5l-0.9,0c0-0.9,0.5-2.6,2.6-2.6h7.2v0.9H8.5C6.9,2.8,6.8,4.3,6.8,4.5z"/><path d="M4.8,4.5H3.9V3.9c0.1-1.4,1-3.9,3.8-3.9h7v0.9h-7C5,0.8,4.8,3.8,4.8,3.9L4.8,4.5z"/></svg></div>`;
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
