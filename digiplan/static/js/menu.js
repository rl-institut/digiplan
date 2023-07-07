import {statusquoDropdown, resultsTabs} from "./elements.js";

const menuNextBtn = document.getElementById("menu_next_btn");
const menuPreviousBtn = document.getElementById("menu_previous_btn");
const mapTab = document.getElementById("map-view-tab");
const chartTab = document.getElementById("chart-view-tab");

menuNextBtn.addEventListener("click", function () {
    nextMenuTab();
    PubSub.publish(eventTopics.MENU_CHANGED);
});
menuPreviousBtn.addEventListener("click", function() {
    previousMenuTab();
    PubSub.publish(eventTopics.MENU_CHANGED);
});

mapTab.addEventListener("click", function () {
    PubSub.publish(eventTopics.MAP_VIEW_SELECTED);
});

chartTab.addEventListener("click", function () {
    PubSub.publish(eventTopics.CHART_VIEW_SELECTED);
});

PubSub.subscribe(eventTopics.MENU_STATUS_QUO_SELECTED, setMapChartViewVisibility);
PubSub.subscribe(eventTopics.MENU_STATUS_QUO_SELECTED, showMapView);
PubSub.subscribe(eventTopics.MENU_STATUS_QUO_SELECTED, hidePotentialLayers);
PubSub.subscribe(eventTopics.MENU_SETTINGS_SELECTED, setMapChartViewVisibility);
PubSub.subscribe(eventTopics.MENU_SETTINGS_SELECTED, showMapView);
PubSub.subscribe(eventTopics.MENU_SETTINGS_SELECTED, deactivateChoropleth);
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, setMapChartViewVisibility);
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, hidePotentialLayers);
PubSub.subscribe(eventTopics.MAP_VIEW_SELECTED, setResultsView);
PubSub.subscribe(eventTopics.CHART_VIEW_SELECTED, setResultsView);


function nextMenuTab() {
    const currentTab = getCurrentMenuTab();
    currentTab.classList.toggle("active");
    const currentStep = `step_${currentTab.id.slice(6)}`;
    document.getElementById(currentStep).classList.toggle("active");
    if (currentTab.id === "panel_1_today") {
        menuPreviousBtn.disabled = false;
        document.getElementById("panel_2_settings").classList.toggle("active");
        document.getElementById("step_2_settings").classList.toggle("active");
        PubSub.publish(eventTopics.MENU_SETTINGS_SELECTED);
    }
    if (currentTab.id === "panel_2_settings") {
        menuNextBtn.disabled = true;
        document.getElementById("panel_3_results").classList.toggle("active");
        document.getElementById("step_3_results").classList.toggle("active");
        PubSub.publish(eventTopics.MENU_RESULTS_SELECTED);
    }
}


function previousMenuTab() {
    const currentTab = getCurrentMenuTab();
    currentTab.classList.toggle("active");
    const currentStep = `step_${currentTab.id.slice(6)}`;
    document.getElementById(currentStep).classList.toggle("active");
    if (currentTab.id === "panel_2_settings") {
        menuPreviousBtn.disabled = true;
        document.getElementById("panel_1_today").classList.toggle("active");
        document.getElementById("step_1_today").classList.toggle("active");
        PubSub.publish(eventTopics.MENU_STATUS_QUO_SELECTED);
    }
    if (currentTab.id === "panel_3_results") {
        menuNextBtn.disabled = false;
        document.getElementById("panel_2_settings").classList.toggle("active");
        document.getElementById("step_2_settings").classList.toggle("active");
        PubSub.publish(eventTopics.MENU_SETTINGS_SELECTED);
    }
}

function getCurrentMenuTab() {
    return document.querySelector("#js-panel-container > .panel__content > .tab-content > .active");
}


function showMapView(msg) {
    bootstrap.Tab.getInstance(mapTab).show();
    PubSub.publish(eventTopics.MAP_VIEW_SELECTED);
    return logMessage(msg);
}

function setMapChartViewVisibility(msg) {
    const view_toggle = document.getElementsByClassName("view-toggle")[0];
    view_toggle.hidden = msg !== eventTopics.MENU_RESULTS_SELECTED;
    return logMessage(msg);
}

function setResultsView(msg) {
    if (msg === eventTopics.CHART_VIEW_SELECTED) {
        statusquoDropdown.parentElement.setAttribute("style", "display: none !important");
        resultsTabs.parentElement.setAttribute("style", "");
    } else {
        statusquoDropdown.parentElement.setAttribute("style", "");
        resultsTabs.parentElement.setAttribute("style", "display: none !important");
    }
    return logMessage(msg);
}
