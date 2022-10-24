const RESULT_STYLES = JSON.parse(document.getElementById("result_styles").textContent);
const results_tab = document.getElementById("panel_3_results_tab");
const result_views = document.getElementById("result_views");

results_tab.addEventListener("shown.bs.tab", () => {
  PubSub.publish(eventTopics.RESULTS_TAB_CLICKED);
});
result_views.addEventListener("change", () => {
  PubSub.publish(eventTopics.RESULT_VIEW_CHANGED);
});

PubSub.subscribe(eventTopics.RESULTS_TAB_CLICKED, loadResults);
PubSub.subscribe(eventTopics.RESULTS_TAB_CLICKED, changeResultView);
PubSub.subscribe(eventTopics.RESULT_VIEW_CHANGED, changeResultView);


function loadResults(msg) {
  map.setLayoutProperty("results", "visibility", "visible");
  return logMessage(msg);
}

function changeResultView(msg) {
  const view = result_views.value;
  if (!(store.cold.result_views.includes(view))) {
    $.ajax({
      type: "GET",
      url: "results",
      dataType: 'json',
      data: {"scenario_id": 1, "result_view": view},
      success: function(results) {
        updateResultsLayer(view, results);
      }
    });
  }
  map.setPaintProperty("results", "fill-color", RESULT_STYLES[view]);
  return logMessage(msg);
}

function updateResultsLayer(view, results) {
  for (var feature_id in results) {
    const result_feature_state = map.getFeatureState(
      {
        source: "results",
        sourceLayer: "results",
        id: feature_id,
      }
    );
    result_feature_state[view] = results[feature_id];
    map.setFeatureState(
      {
        source: "results",
        sourceLayer: "results",
        id: feature_id,
      },
      result_feature_state
    );
  }
  store.cold.result_views.push(view);
}
