import {resultsTabs, futureDropdown} from "./elements.js";

const menuNextBtn = document.getElementById("menu_next_btn");
const menuPreviousBtn = document.getElementById("menu_previous_btn");
const regionChart = document.getElementById("region_chart_2045");

const menuTabs = [
    {
        name: "challenges",
        event: eventTopics.MENU_CHALLENGES_SELECTED
    },
    {
        name: "today",
        event: eventTopics.MENU_STATUS_QUO_SELECTED
    },
    {
        name: "scenarios",
        event: eventTopics.MENU_SCENARIOS_SELECTED
    },
    {
        name: "settings",
        event: eventTopics.MENU_SETTINGS_SELECTED
    },
    {
        name: "results",
        event: eventTopics.MENU_RESULTS_SELECTED
    },
];

menuNextBtn.addEventListener("click", function () {
    nextMenuTab();
    PubSub.publish(eventTopics.MENU_CHANGED);
});
menuPreviousBtn.addEventListener("click", function() {
    previousMenuTab();
    PubSub.publish(eventTopics.MENU_CHANGED);
});

PubSub.subscribe(eventTopics.MENU_CHALLENGES_SELECTED, showEmpowerplanContent);
PubSub.subscribe(eventTopics.MENU_STATUS_QUO_SELECTED, setMapChartViewVisibility);
PubSub.subscribe(eventTopics.MENU_STATUS_QUO_SELECTED, hidePotentialLayers);
PubSub.subscribe(eventTopics.MENU_STATUS_QUO_SELECTED, hideEmpowerplanContent);
PubSub.subscribe(eventTopics.MENU_SETTINGS_SELECTED, setMapChartViewVisibility);
PubSub.subscribe(eventTopics.MENU_SETTINGS_SELECTED, deactivateChoropleth);
PubSub.subscribe(eventTopics.MENU_SETTINGS_SELECTED, terminateSimulation);
PubSub.subscribe(eventTopics.MENU_SETTINGS_SELECTED, hideEmpowerplanContent);
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, setMapChartViewVisibility);
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, hidePotentialLayers);
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, hideEmpowerplanContent);
PubSub.subscribe(eventTopics.MENU_SCENARIOS_SELECTED, showEmpowerplanContent);
PubSub.subscribe(eventTopics.MAP_VIEW_SELECTED, setResultsView);
PubSub.subscribe(eventTopics.CHART_VIEW_SELECTED, setResultsView);


function nextMenuTab() {
    const currentTab = getCurrentMenuTab();
    currentTab.classList.toggle("active");
    const tabIndex = parseInt(currentTab.id.slice(6, 7));
    const currentStep = `step_${tabIndex}_${menuTabs[tabIndex - 1].name}`;
    document.getElementById(currentStep).classList.toggle("active");
    const nextPanel = `panel_${tabIndex + 1}_${menuTabs[tabIndex].name}`;
    const nextStep = `step_${tabIndex + 1}_${menuTabs[tabIndex].name}`;
    document.getElementById(nextPanel).classList.toggle("active");
    document.getElementById(nextStep).classList.toggle("active");
    PubSub.publish(menuTabs[tabIndex].event);
    menuPreviousBtn.disabled = false;
    if (tabIndex >= menuTabs.length - 1) {
        menuNextBtn.disabled = true;
    }
}


function previousMenuTab() {
    const currentTab = getCurrentMenuTab();
    currentTab.classList.toggle("active");
    const tabIndex = parseInt(currentTab.id.slice(6, 7));
    const currentStep = `step_${tabIndex}_${menuTabs[tabIndex - 1].name}`;
    document.getElementById(currentStep).classList.toggle("active");
    const nextPanel = `panel_${tabIndex - 1}_${menuTabs[tabIndex - 2].name}`;
    const nextStep = `step_${tabIndex - 1}_${menuTabs[tabIndex - 2].name}`;
    document.getElementById(nextPanel).classList.toggle("active");
    document.getElementById(nextStep).classList.toggle("active");
    PubSub.publish(menuTabs[tabIndex - 2].event);
    menuNextBtn.disabled = false;
    if (tabIndex === 2) {
        menuPreviousBtn.disabled = true;
    }
}

function getCurrentMenuTab() {
    return document.querySelector("#js-panel-container > .panel__content > .tab-content > .active");
}

function setMapChartViewVisibility(msg) {
    const view_toggle = document.getElementsByClassName("view-toggle")[0];
    view_toggle.hidden = msg !== eventTopics.MENU_RESULTS_SELECTED;
    return logMessage(msg);
}

function setResultsView(msg) {
    if (msg === eventTopics.CHART_VIEW_SELECTED) {
        futureDropdown.parentElement.setAttribute("style", "display: none !important");
        regionChart.setAttribute("style", "display: none");
        resultsTabs.parentElement.setAttribute("style", "");
    } else {
        futureDropdown.parentElement.setAttribute("style", "");
        regionChart.setAttribute("style", "");
        resultsTabs.parentElement.setAttribute("style", "display: none !important");
    }
    return logMessage(msg);
}

function terminateSimulation(msg) {
    if (store.cold.task_id != null) {
        $.ajax({
            url: "/oemof/terminate",
            type: "POST",
            data: {task_id: store.cold.task_id},
            success: function () {
                store.cold.task_id = null;
            }
        });
        document.getElementById("simulation_spinner").hidden = true;
    }
    return logMessage(msg);
}

function showEmpowerplanContent(msg) {
    const contentID = msg === "MENU_CHALLENGES_SELECTED" ? "challenges" : "scenarios";
    const content = document.getElementById(contentID);
    content.hidden = false;
    content.style.alignItems = "center";
    content.style.padding = "3rem";
    document.getElementById("mainTabContent").hidden = true;
    return logMessage(msg);
}

function hideEmpowerplanContent(msg) {
    for (const contentID of ["challenges", "scenarios"]) {
        const content = document.getElementById(contentID);
        content.hidden = true;
        content.style.alignItems = null;
        content.style.padding = "0rem";
    }
    if (msg === "MENU_SETTINGS_SELECTED") {
        document.getElementById("map-view-tab").click();
    }
    document.getElementById("mainTabContent").hidden = false;
    map.resize();
    return logMessage(msg);
}
