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
      }, redirect: "follow", // manual, *follow, error
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

    // TODO: construct dynamically via emitted id by event
    const url = "/static/tests/api/popup.json??lookup=population&municipality=12lang=en";

    fetchGetJson(url).then(// TODO: for now we assume response has chart. Later determine dynamically.
      (response) => {
        /*
          Construct Popup From Event And Params
        */
        const template = document.getElementById("js-" + template_id + "_popup");
        const clone = template.content.cloneNode(true);
        const html = clone.getElementById("js-" + "popup");
        for (const field in fields) {
          if (field === "title") {
            const titleElement = html.querySelector("#js-popup__title");
            const {title} = response;
            titleElement.innerHTML = title;
          }
          if (field === "municipality") {
            const municipalityElement = html.querySelector("#js-popup__municipality");
            const {municipality} = response;
            municipalityElement.innerHTML = `(${municipality})`;
          }
          if (field === "key-values") {
            const keyValuesElement = html.querySelector("#js-popup__key-values");
            const {
              keyValues: {
                unit,
                year,
                municipalityValue,
                regionTitle,
                regionValue,
              }
            } = response;
            keyValuesElement.innerHTML = `
              <span class="key-values__unit">${unit}</span>
              <span class="key-values__year">${year}</span>
              <span class="key-values__region-value">${municipalityValue}</span>
              <span class="key-values__municipality-title">${regionTitle}</span>:
              <span class="key-values__municipality-value">${regionValue}</span>
            `;
          }
          if (field === "description") {
            const descriptionElement = html.querySelector("#js-popup__description");
            const {description} = response;
            descriptionElement.innerHTML = description;
          }
          if (field === "chart") {

            // Chart Title
            /* const chartTitleElement = html.querySelector("#js-popup__chart-title");
            const {chart: {title}} = response;
            chartTitleElement.innerHTML = title; */

            // Chart
            const chartElement = html.querySelector("#js-popup__chart");
            const chart = echarts.init(chartElement, null, {renderer: 'svg'});
            // TODO: use chartType in payload to construct chart dynamically. For now we assume bar chart type.
            // TODO: In this fetch we always expect one payload item. Make failsafe.
            const {chart: {data: {series}}} = response;
            const xAxisData = createListByName("key", series);
            const yAxisData = createListByName("value", series);
            const option = {
              title: {
                text: 'this is a test'
              },
              animation: false,
              tooltip: {
                trigger: 'axis', 
                axisPointer: {
                  type: 'shadow'
                }
              }, 
              grid: {
                left: '3%', right: '4%', bottom: '3%', containLabel: true
              }, 
              xAxis: [{
                type: 'category', data: xAxisData, axisTick: {
                  alignWithLabel: true
                }
              }], 
              yAxis: [{
                type: 'value'
              }], 
              series: [{
                name: 'Direct', type: 'bar', barWidth: '60%', data: yAxisData,
              }]
            };
            chart.setOption(option);
            requestAnimationFrame(() => {
              new maplibregl.Popup({
                // https://maplibre.org/maplibre-gl-js-docs/api/markers/#popup-parameters
                maxWidth: "280px",
              }).setLngLat(coordinates).setHTML(html.innerHTML).addTo(map);
            });
          }
          if (field === "sources") {
            const sourcesElement = html.querySelector("#js-popup__sources");
            let links = [];
            for (const index in response.sources) {
              const url = response.sources[index].url;
              const name = response.sources[index].name;
              links.push(`<a href="${url}">${name}</a>`);
            }
            sourcesElement.innerHTML = links.join(", ");
          }
        }
      });
  });
}

$(document).ready(function () {
  $('#js-intro-modal').modal('show');
});
