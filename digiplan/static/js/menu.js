
const menuNextBtn = document.getElementById("menu_next_btn");
const menuPreviousBtn = document.getElementById("menu_previous_btn");

menuNextBtn.addEventListener("click", nextMenuTab);
menuPreviousBtn.addEventListener("click", previousMenuTab);

PubSub.subscribe(eventTopics.MENU_STATUS_QUO_SELECTED, test);
PubSub.subscribe(eventTopics.MENU_SETTINGS_SELECTED, test);
PubSub.subscribe(eventTopics.MENU_RESULTS_SELECTED, test);


function nextMenuTab() {
    const currentTab = getCurrentMenuTab();
    currentTab.classList.toggle("active");
    if (currentTab.id === "panel_1_today") {
        menuPreviousBtn.disabled = false;
        document.getElementById("panel_2_settings").classList.toggle("active");
        PubSub.publish(eventTopics.MENU_SETTINGS_SELECTED);
    }
    if (currentTab.id === "panel_2_settings") {
        menuNextBtn.disabled = true;
        document.getElementById("panel_3_results").classList.toggle("active");
        PubSub.publish(eventTopics.MENU_RESULTS_SELECTED);
    }
}


function previousMenuTab() {
    const currentTab = getCurrentMenuTab();
    currentTab.classList.toggle("active");
    if (currentTab.id === "panel_2_settings") {
        menuPreviousBtn.disabled = true;
        document.getElementById("panel_1_today").classList.toggle("active");
        PubSub.publish(eventTopics.MENU_STATUS_QUO_SELECTED);
    }
    if (currentTab.id === "panel_3_results") {
        menuNextBtn.disabled = false;
        document.getElementById("panel_2_settings").classList.toggle("active");
        PubSub.publish(eventTopics.MENU_SETTINGS_SELECTED);
    }
}

function getCurrentMenuTab() {
    return document.querySelector("#js-panel-container > .panel__content > .tab-content > .active");
}

function test(msg) {
    logMessage(msg);
}