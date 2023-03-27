
const resultsDropdown = document.getElementById("result_views");

resultsDropdown.addEventListener("change", function() {
   PubSub.publish(mapEvent.CHOROPLETH_SELECTED, resultsDropdown.value);
});
