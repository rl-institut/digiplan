
const resultsDropdown = document.getElementById("result_views");

resultsDropdown.addEventListener("click", function() {
   PubSub.publish(mapEvent.CHOROPLETH_SELECTED, resultsDropdown.value);
});
