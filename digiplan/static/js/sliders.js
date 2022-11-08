
PubSub.subscribe(eventTopics.STATES_INITIALIZED, updateSliderMarks);


function updateSliderMarks(msg) {
  for (let [slider_name, slider_marks] of Object.entries(store.cold.slider_marks)) {
    let slider = $(`#id_${slider_name}`).data("ionRangeSlider");
    slider.update({
      onUpdate: function(data) {  // jshint ignore:line
        addMarks(data, slider_marks);
      }
    });
  }
  return logMessage(msg);
}

function convertToPercent(num, min, max) {
  return (num - min) / (max - min) * 100;
}

function addMarks(data, marks) {
  var html = '';
  var left_p = "";

  for (var i = 0; i < marks.length; i++) {
    let left = convertToPercent(marks[i][1], data.min, data.max);
    left_p = left + "%";
    html += '<span class="showcase__mark" style="left: ' + left_p + '">';
    html += marks[i][0];
    html += '</span>';
  }

  data.slider.append(html);
}
