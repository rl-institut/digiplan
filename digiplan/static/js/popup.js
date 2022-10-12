"use strict";

async function fetchGetJson(url) {
  try {
    // Default options are marked with *
    const response = await fetch(url, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      mode: "cors", // no-cors, *cors, same-origin
      cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
      credentials: "same-origin", // include, *same-origin, omit
      headers: {
        "Content-Type": "application/json",
      },
      redirect: "follow", // manual, *follow, error
      referrerPolicy: "no-referrer", // no-referrer, *client
    });
    return await response.json(); // parses JSON response into native JavaScript objects
  } catch (err) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw err;
  }
}

function createCoordinates(event) {
  if ("lat" in event.features[0].properties) {
    return [event.features[0].properties.lat, event.features[0].properties.lon];
  }
  return event.lngLat;
}

function createListByName(name, series) {
  let list = [];
  for (const item in series) {
    list.push(series[item][name]);
  }
  return list;
}

function add_popup(layer_id, fields, template_id = "default") {
  map.on("click", layer_id, function (event) {
    /*
      Check if popup already exists
    */
    if ($('.mapboxgl-popup').length > 0) {
      return;
    }

    /*
      Construct Coordinates From Event
    */
    const coordinates = createCoordinates(event);

    /*
      Construct Popup From Event And Params
    */
    const template = document.getElementById(template_id + "_popup");
    const clone = template.content.cloneNode(true);
    const html = clone.getElementById("popup_div");
    const table = html.querySelector("table");
    let tableRows = "";
    for (const label in fields) {
      const key = fields[label];
      const value = event.features[0].properties[key];
      tableRows += `<tr><td>${label}</td><td>${value}</td></tr>`;
    }
    table.innerHTML = tableRows;

    /*
      Init Chart
    */
    const chartDom = html.querySelector("#popup_chart");
    const myChart = echarts.init(chartDom, null, {renderer: 'svg'});

    // TODO: construct dynamically via emitted id by event
    const url = "/static/tests/api/popup.json??lookup=population&municipality=12lang=en";

    fetchGetJson(url).then(
      // TODO: for now we assume response has chart. Later determine dynamically.
      (data) => {
        /*
          Construct Chart
        */
        // TODO: use chartType in payload to construct chart dynamically. For now we assume bar chart type.
        // TODO: In this fetch we always expect one payload item. Make failsafe.
        const series = data.chart.payload[0].data.series;
        const xAxisData = createListByName("key", series);
        const yAxisData = createListByName("value", series);
        const option = {
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
              data: xAxisData,
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
              data: yAxisData,
            }
          ]
        };
        myChart.setOption(option);
        requestAnimationFrame(() => {
          new maplibregl.Popup().setLngLat(coordinates).setHTML(html.innerHTML).addTo(map);
        });
      }
    );
  });
}

$(document).ready(function () {
  $('#js-intro-modal').modal('show');
});
