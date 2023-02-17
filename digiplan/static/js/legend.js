const legendElement = document.getElementById("legend");

/**
 * Returns a legend HTML element as a string.
 *
 * Uses nextColumnStartIndex numeric value to determine
 * which legend item belongs in which of two columns
 *
 * @param {string} title - the title of the legend.
 * @param {string} unit - the unit name concerning the value range.
 * @param {Array<string>} colors - 6 hex (with #) or rgb(a) color values as string array.
 * @param {Array<string>} valueRanges - 6 value range strings as string array.
 * @param {number} nextColumnStartIndex - start index of item in the second column.
 * @return {string} - HTML element as a string.
 */
const createLegend = (title, unit, colors, valueRanges, nextColumnStartIndex = 3) => {
  return `
    <div class="legend__heading">
      <span class="legend__title">Legend -&nbsp;</span>
      <span class="legend__detail">${title}</span>
      <div class="legend__unit">(${unit})</div>
    </div>
    <div class="legend__wrap">
      <div class="legend__column">
        ${valueRanges.filter((value, idx) => idx < nextColumnStartIndex).map((value, idx) => `<div class="legend__item" id="legend__item__color-${idx}">${value}</div>`).join(' ')}
      </div>
      <div class="legend__column">
        ${valueRanges.filter((value, idx) => idx >= nextColumnStartIndex).map((value, idx) => `<div class="legend__item" id="legend__item__color-${idx + nextColumnStartIndex}">${value}</div>`).join(' ')}
      </div>
    </div>
    <style>
    ${colors.map((colorValue, idx) => ` #legend__item__color-${idx}:before { background-color: ${colorValue}; }`).join(' ')}
    </style>
  `;
};

window.onload = () => {
  const onLoadUrl = "/static/tests/api/legend.json??lookup=population&lang=en";

  fetchGetJson(onLoadUrl).then(
    (response) => {
      const {title, unit, colors, values} = response;
      legendElement.innerHTML = createLegend(title, unit, colors, values);
    });
};
