"use strict";

// Disable zoom on double click
map.doubleClickZoom.disable();

// Fly to level of detail of clicked on feature
function flyToLOD(element) {
  // Feature tile user clicked on
  let feature = element.features[0];

  // Get zoom-to level
  let zoom = (feature.layer.maxzoom < 11) ? feature.layer.maxzoom : 11;

  // Fly to center of bounding box and zoom to max zoom of layer
  map.flyTo({
    center: element.lngLat,
    zoom: zoom,
    essential: true
  });
}

// Fly to level of detail of clicked on feature
function fitToBoundingBox(feature) {
  if (feature.properties.bbox) {
    const data = JSON.parse(feature.properties.bbox);
    const coords = data["coordinates"][0];
    const bounds = [coords[0], coords[2]];
    map.fitBounds(bounds);
    if (store.cold.debugMode) {
      console.log(`You selected: ${feature.name ? feature.name : feature.properties.name}, id: ${feature.id}, bounds: ${bounds}`);
    }
  } else {
    if (store.cold.debugMode) {
      console.log(`No bbox on feature with name: ${feature.name}, id: ${feature.id}`);
    }
  }
}

// Fly or Fit
function flyOrFit(element) {
  let feature = element.features[0];
  let cityStates = ["Berlin", "Bremen", "Hamburg"];
  let cityDistricts = ["Kreisfreie Stadt", "Stadtkreis"];
  if (cityStates.includes(feature.properties.name) || cityDistricts.includes(feature.properties.type)) {
    fitToBoundingBox(feature);
  } else if (feature.source === "municipality") {
    if (feature.sourceLayer === "municipality") {
      fitToBoundingBox(feature);
    }
  } else {
    flyToLOD(element);
  }
}
