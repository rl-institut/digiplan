
const resultsDropdown = document.getElementById("result_views");
const image_results = document.getElementById("info_tooltip_results");

resultsDropdown.addEventListener("change", function() {
   PubSub.publish(mapEvent.CHOROPLETH_SELECTED, resultsDropdown.value);
   image_results.title = resultsDropdown.options[resultsDropdown.selectedIndex].title;
});
