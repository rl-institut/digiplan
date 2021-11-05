(function() {
  "use strict";

  // Variables
  const autocompleteInput = document.getElementById("autocomplete");
  let inputTextStorage = "";
  const loadingSpinner = document.querySelector(".lds-spinner");

  // Autocomplete
  $(function () {
    $("#autocomplete").autocomplete({
      serviceUrl: "/search/",
      onSelect: function (suggestion) {
        let data = JSON.parse(suggestion.data.bbox.replace(/\(/g, '[').replace(/\)/g, ']'))
        let bounds = [[data[0], data[1]], [data[2], data[3]]]
        map.fitBounds(bounds);
        if (store.cold.debugMode) {
          console.log(`You selected: ${suggestion.value}, id: ${suggestion.data.id}, bounds: ${bounds}`);
        }
      },
      showNoSuggestionNotice: true,
      noSuggestionNotice: "Keine Einträge gefunden!",
      autoSelectFirst: true,
      triggerSelectOnValidInput: false
    });
  });

  // Set up an event listener which is True if the event has a dataType of source and
  // the source has no outstanding network requests.
  map.on("sourcedata", function (element) {
    if (store.cold.debugModeVerbose) {
      console.log("Fired sourcedata, element:", element);
    }
    if (element.isSourceLoaded || element.sourceDataType === "visibility") {
      autocompleteInput.removeAttribute("disabled");
      autocompleteInput.value = inputTextStorage;
      autocompleteInput.placeholder = "Search region...";
      autocompleteInput.style.backgroundImage = "url(/static/images/icons/magnifier.svg)";
      loadingSpinner.style.display = "none";
    } else {
      autocompleteInput.setAttribute("disabled", "disabled");
      inputTextStorage = autocompleteInput.value;
      autocompleteInput.value = "";
      autocompleteInput.style.backgroundImage = "none";
      loadingSpinner.style.display = "inline-block";
    }
  });
})();
