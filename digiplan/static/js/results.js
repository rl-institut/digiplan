
const resultsDropdown = document.getElementById("result_views");
const imageResults = document.getElementById("info_tooltip_results");

// Setup

// Disable settings form submit
$('#settings').submit(false);

resultsDropdown.addEventListener("change", function() {
    PubSub.publish(mapEvent.CHOROPLETH_SELECTED, resultsDropdown.value);
    imageResults.title = resultsDropdown.options[resultsDropdown.selectedIndex].title;
});


// Subscriptions
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, simulate);
PubSub.subscribe(eventTopics.SIMULATION_FINISHED, showResults);


// Subscriber Functions

function simulate(msg) {
    const settings = document.getElementById("settings");
    const formData = new FormData(settings); // jshint ignore:line
    $.ajax({
        url : "/oemof/simulate",
        type : "POST",
        processData: false,
        contentType: false,
        data : formData,
        success : function(json) {
            map_store.cold.state.simulation_id = json.simulation_id;
            PubSub.publish(eventTopics.SIMULATION_FINISHED, json.simulation_id);
        },
    });
    return logMessage(msg);
}

function showResults(msg, simulation_id) {
    $.ajax({
        url : "/visualization",
        type : "GET",
        data : {
            simulation_ids: simulation_id,
            visualization: "total_system_costs",
        },
        success : function(json) {
            console.log(json);
        },
    });
    return logMessage(msg);
}
