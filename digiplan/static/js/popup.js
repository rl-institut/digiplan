"use strict";

function add_popup(layer_id, fields, template_id = "default") {
  map.on("click", layer_id, function (e) {
    let coordinates;
    // Check if popup already exists:
    if ($('.mapboxgl-popup').length > 0) {
      return;
    }

    if ("lat" in e.features[0].properties) {
      // Get coordinates from lat/lon:
      coordinates = [e.features[0].properties.lat, e.features[0].properties.lon];
    } else {
      // Get coordinates from geometry:
      coordinates = e.lngLat;
    }
    const template = document.getElementById(template_id + "_popup");
    const clone = template.content.cloneNode(true);
    const html = clone.getElementById("popup_div");
    const table = html.querySelector("table");
    let tableRows = "";
    for (const label in fields) {
      const key = fields[label];
      const value = e.features[0].properties[key];
      tableRows += `<tr><td>${label}</td><td>${value}</td></tr>`;
    }
    table.innerHTML = tableRows;

    const chartDom = html.querySelector("#popup_chart");
    const myChart = echarts.init(chartDom, null, {renderer: 'svg'});
    let option;

    option = {
      animation: false,
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: [
        {
          type: 'category',
          data: ["2023", "2030", "2045"],
          axisTick: {
            alignWithLabel: true
          }
        }
      ],
      yAxis: [
        {
          type: 'value'
        }
      ],
      series: [
        {
          name: 'Direct',
          type: 'bar',
          barWidth: '60%',
          data: [20000, 22000, 24000]
        }
      ]
    };

    option && myChart.setOption(option);

    requestAnimationFrame(() => {
      new maplibregl.Popup().setLngLat(coordinates).setHTML(html.innerHTML).addTo(map);
    });
  });
}

$(document).ready(function () {
  $('#js-intro-modal').modal('show');
});
