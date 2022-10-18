const legendElement = document.getElementById("legend");

const createLegend = (title, colors, values, divider = 3) => {
  return `
    <div class="legend__heading">
      <span class="legend__title">Legend -&nbsp;</span>
      <span class="legend__detail">${title}</span>
    </div>
    <div class="legend__wrap">
      <div class="legend__column">
        ${values.filter((value, idx) => idx < divider).map((value, idx) => `<div class="legend__item" id="legend__item__color-${idx}">${value}</div>`).join(' ')}
      </div>
      <div class="legend__column">
        ${values.filter((value, idx) => idx >= divider).map((value, idx) => `<div class="legend__item" id="legend__item__color-${idx + divider}">${value}</div>`).join(' ')}
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
      const {title, colors, values} = response;
      legendElement.innerHTML = createLegend(title, colors, values);
    });
};
