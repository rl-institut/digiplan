// Variables
const SETTINGS_PARAMETERS = JSON.parse(document.getElementById("settings_parameters").textContent);
const panelContainer = document.getElementById("js-panel-container");
const panelSliders = document.querySelectorAll(".js-slider.js-slider-panel");
const powerPanelSliders = document.querySelectorAll(".js-slider.js-slider-panel.js-power-mix");
const sliderMoreLabels = document.querySelectorAll(".c-slider__label--more > .button");
const powerMixInfoBanner = document.getElementById("js-power-mix");


// Setup

// Order matters. Start with the most specific, and end with most general sliders.
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
  let html = "";

  for (const index of weights.keys()) {
    html += `<span style="width: ${weights[index]}%; background-color: ${colors[index]}; text-align: center; height: 1rem;"></span>`;
  }

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
