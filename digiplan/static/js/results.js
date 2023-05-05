
const resultsDropdown = document.getElementById("result_views");
const imageResults = document.getElementById("info_tooltip_results");
const simulation_spinner = document.getElementById("simulation_spinner");

// Setup

// Disable settings form submit
$('#settings').submit(false);

resultsDropdown.addEventListener("change", function() {
    PubSub.publish(mapEvent.CHOROPLETH_SELECTED, resultsDropdown.value);
    imageResults.title = resultsDropdown.options[resultsDropdown.selectedIndex].title;
});


// Subscriptions
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, simulate);
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, showSimulationSpinner);
PubSub.subscribe(eventTopics.SIMULATION_FINISHED, showResults);
PubSub.subscribe(eventTopics.SIMULATION_FINISHED, hideSimulationSpinner);


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

function showSimulationSpinner(msg) {
    simulation_spinner.hidden = false;
    return logMessage(msg);
}

function hideSimulationSpinner(msg) {
    simulation_spinner.hidden = true;
    return logMessage(msg);
}
