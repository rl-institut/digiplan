// Variables
const rangeSliders = document.getElementsByClassName("js-range-slider");
const energyMix = document.getElementById("js-energy-mix");

// Setup
$(".js-range-slider").ionRangeSlider({
    onChange: function (data) {
      const msg = eventTopics.SLIDER_CHANGE;
      PubSub.publish(msg, data);
    }
  }
);


// Subscriptions
PubSub.subscribe(eventTopics.STATES_INITIALIZED, updateSliderMarks);
PubSub.subscribe(eventTopics.STATES_INITIALIZED, createPercentagesOfPowerSources);
PubSub.subscribe(eventTopics.SLIDER_CHANGE, createPercentagesOfPowerSources);

// Subscriber Functions

function createPercentagesOfPowerSources(msg) {
  let ids = [];
  let values = [];
  Array.from(rangeSliders).forEach(function (item) {
    ids.push(item.id);
    values.push($("#" + item.id).data().from);
  });
  const total = getTotalOfValues(values);
  const weights = getWeightsInPercent(values, total);
  const colors = getColorsByIds(ids);
  updateEnergyMix(weights, colors);
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
  const colorsById = {
    "id_bio": "#bae6fd",
    "id_conventional": "#fecdd3",
    "id_pv_ground": "#fef08a",
    "id_pv_roof": "#a7f3d0",
  };
  let colors = [];
  for (let id of ids) {
    colors.push(colorsById[id]);
  }
  return colors;
}

function updateEnergyMix(weights, colors) {
  const msg = "Unequal amount of weights and colors";
  if (weights.length !== colors.length) throw new Error(msg);
  let html = "";

  for (const index of weights.keys()) {
    html += `<span style="width: ${weights[index]}%; background-color: ${colors[index]}; text-align: center; height: 1rem;"></span>`;
  }

  energyMix.innerHTML = html;
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
