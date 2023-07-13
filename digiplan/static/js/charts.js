// Goals & scenarios, initioalize charts
const renewable_share_goal_div = document.getElementById("renewable_share_goal_chart");
const renewable_share_goal_chart = echarts.init(renewable_share_goal_div);
const co2_emissions_goal_div = document.getElementById("co2_emissions_goal_chart");
const co2_emissions_goal_chart = echarts.init(co2_emissions_goal_div);
const renewable_share_scenario_div = document.getElementById("renewable_share_scenario_chart");
const renewable_share_scenario_chart = echarts.init(renewable_share_scenario_div);
const co2_emissions_scenario_div = document.getElementById("co2_emissions_scenario_chart");
const co2_emissions_scenario_chart = echarts.init(co2_emissions_scenario_div);

// Results view, initiliaze charts
const detailed_overview_chart = echarts.init(document.getElementById("detailed_overview_chart"));
const ghg_overview_chart = echarts.init(document.getElementById("ghg_overview_chart"));
const electricity_overview_chart = echarts.init(document.getElementById("electricity_overview_chart"));
const electricity_THG_chart = echarts.init(document.getElementById("electricity_THG_chart"));
const mobility_overview_chart = echarts.init(document.getElementById("mobility_overview_chart"));
const mobility_THG_chart = echarts.init(document.getElementById("mobility_THG_chart"));
const overview_heat_chart = echarts.init(document.getElementById("overview_heat_chart"));
const decentralized_centralized_heat_chart = echarts.init(document.getElementById("decentralized_centralized_heat_chart"));


PubSub.subscribe(eventTopics.MENU_CHANGED, resizeCharts);

// Styling variables
const chart_tooltip = {
  trigger: 'axis',
  axisPointer: {
  type: 'shadow'
  }
};
const chart_bar_width_sm = 16;
const chart_grid_goal = {
  top: '10%',
  left: '15%',
  right: '15%',
  bottom: '18%',
  height: '120',
  containLabel: true
};
const chart_grid_results = {
  top: '10%',
  left: '3%',
  right: '25%',
  bottom: '18%',
  containLabel: true
};
const chart_text_style = {
  fontFamily: "Roboto",
  fontSize: 10,
  //fontWeight: 300,
  //color: '#002C50'
};
const chart_legend = {
  show: true,
  bottom: '0',
  itemWidth: 10,
  itemHeight: 10
};

// Goal variables
// const renewable_share_goal_value = 90;
// const co2_emissions_goal_value = 30;

// CHARTS
const renewable_share_goal = {
  grid: chart_grid_goal,
  tooltip: chart_tooltip,
  textStyle: chart_text_style,
  xAxis: {
    type: 'category',
    data: ['2021', 'Szenario'],
    axisTick: {
      show: false,
    },
    axisLabel: {fontSize: 9}, //, rotate: 20},
  },
  yAxis: {
    show: true,
    type: 'value',
    maxValueSpan: '100'
  },
  series: [
    {
      type: 'bar',
      barWidth: chart_bar_width_sm,
      data: [
        {
          value: 30,
          itemStyle: {
            color: '#D8E2E7'
          }
        },
        {
          value: 90,
          itemStyle: {
            color: '#06DFA7'
          }
        },
      ],
      // markLine: {
      //   silent: true,
      //   lineStyle: {
      //     color: '#06DFA7',
      //     type: 'solid'
      //   },
      //   symbol: 'none',
      //   data: [{
      //     yAxis: renewable_share_goal_value,
      //     label: {
      //       show: false
      //     }
      //   }]
      // }
    },
  ],
};

const co2_emissions_goal = {
  grid: chart_grid_goal,
  tooltip: chart_tooltip,
  textStyle: chart_text_style,
  legend: chart_legend,
  xAxis: {
    type: 'category',
    data: ['Szenario'],
    axisTick: {
      show: false
    },
    axisLabel: {fontSize: 9}, //, rotate: 20},
  },
  yAxis: {
    show: true,
    type: 'value',
    maxValueSpan: '100'
  },
  series: [
    {
      type: 'bar',
      name: 'Regional',
      stack: 'reduc',
      color: '#06DFA7',
      barWidth: chart_bar_width_sm,
      data: [50],
    },
    {
      type: 'bar',
      name: 'Import',
      stack: 'reduc',
      color: '#E8986B',
      barWidth: chart_bar_width_sm,
      data: [20],
    },
      // markLine: {
      //   silent: true,
      //   lineStyle: {
      //     color: '#E8986B',
      //     type: 'solid'
      //   },
      //   symbol: 'none',
      //   data: [{
      //     yAxis: co2_emissions_goal_value,
      //     label: {
      //       show: false
      //     }
      //   }]
      // }
  ],
};

const renewable_share_scenario = {
  grid: chart_grid_goal,
  tooltip: chart_tooltip,
  textStyle: chart_text_style,
  xAxis: {
    type: 'category',
    data: ['2021', 'Szenario'],
    axisTick: {
      show: false,
    },
    axisLabel: {fontSize: 9}, //, rotate: 20},
  },
  yAxis: {
    show: true,
    type: 'value',
    maxValueSpan: '100'
  },
  series: [
    {
      type: 'bar',
      barWidth: chart_bar_width_sm,
      data: [
        {
          value: 30,
          itemStyle: {
            color: '#D8E2E7'
          }
        },
        {
          value: 90,
          itemStyle: {
            color: '#06DFA7'
          }
        },
      ],
      // markLine: {
      //   silent: true,
      //   lineStyle: {
      //     color: '#06DFA7',
      //     type: 'solid'
      //   },
      //   symbol: 'none',
      //   data: [{
      //     yAxis: renewable_share_goal_value,
      //     label: {
      //       show: false
      //     }
      //   }]
      // }
    },
  ],
};

const co2_emissions_scenario = {
  grid: chart_grid_goal,
  tooltip: chart_tooltip,
  textStyle: chart_text_style,
  legend: chart_legend,
  xAxis: {
    type: 'category',
    data: ['Szenario'],
    axisTick: {
      show: false
    },
    axisLabel: {fontSize: 9}, //, rotate: 20},
  },
  yAxis: {
    show: true,
    type: 'value',
    maxValueSpan: '100'
  },
  series: [
    {
      type: 'bar',
      name: 'Regional',
      stack: 'reduc',
      color: '#06DFA7',
      barWidth: chart_bar_width_sm,
      data: [50],
    },
    {
      type: 'bar',
      name: 'Import',
      stack: 'reduc',
      color: '#E8986B',
      barWidth: chart_bar_width_sm,
      data: [20],
    },
      // markLine: {
      //   silent: true,
      //   lineStyle: {
      //     color: '#E8986B',
      //     type: 'solid'
      //   },
      //   symbol: 'none',
      //   data: [{
      //     yAxis: co2_emissions_goal_value,
      //     label: {
      //       show: false
      //     }
      //   }]
      // }
  ],
};

// get options for result view charts
const detailed_overview_option = JSON.parse(document.getElementById("detailed_overview").textContent);
const ghg_overview_option = JSON.parse(document.getElementById("ghg_overview").textContent);
const electricity_overview_option = JSON.parse(document.getElementById("electricity_overview").textContent);
const electricity_ghg_option = JSON.parse(document.getElementById("electricity_ghg").textContent);
const mobility_overview_option = JSON.parse(document.getElementById("mobility_overview").textContent);
const mobility_ghg_option = JSON.parse(document.getElementById("mobility_ghg").textContent);
const overview_heat_option = JSON.parse(document.getElementById("overview_heat").textContent);
const decentralized_centralized_heat_option = JSON.parse(document.getElementById("decentralized_centralized_heat").textContent);

function resizeCharts() {
  setTimeout(function () {
    renewable_share_goal_chart.resize();
    co2_emissions_goal_chart.resize();
    renewable_share_scenario_chart.resize();
    co2_emissions_scenario_chart.resize();
    detailed_overview_chart.resize();
    ghg_overview_chart.resize();
    electricity_overview_chart.resize();
    electricity_THG_chart.resize();
    mobility_overview_chart.resize();
    mobility_THG_chart.resize();
    overview_heat_chart.resize();
    decentralized_centralized_heat_chart.resize();
  }, 200);
}

// Goals & scenarios, setOptions
renewable_share_goal_chart.setOption(renewable_share_goal);
co2_emissions_goal_chart.setOption(co2_emissions_goal);
renewable_share_scenario_chart.setOption(renewable_share_scenario);
co2_emissions_scenario_chart.setOption(co2_emissions_scenario);

// Results, setOptions
detailed_overview_chart.setOption(detailed_overview_option);
ghg_overview_chart.setOption(ghg_overview_option);
electricity_overview_chart.setOption(electricity_overview_option);
electricity_THG_chart.setOption(electricity_ghg_option);
mobility_overview_chart.setOption(mobility_overview_option);
mobility_THG_chart.setOption(mobility_ghg_option);
overview_heat_chart.setOption(overview_heat_option);
decentralized_centralized_heat_chart.setOption(decentralized_centralized_heat_option);

resizeCharts();

window.addEventListener("resize", resizeCharts);
document.addEventListener("show.bs.tab", resizeCharts);


function createChart(div_id, options) {
  const chartElement = document.getElementById(div_id);
  let chart;
  if (echarts.getInstanceByDom(chartElement)) {
    chart =  echarts.getInstanceByDom(chartElement);
    chart.clear();
  } else {
    chart = echarts.init(chartElement, null, {renderer: 'svg'});
  }
  chart.setOption(options);
  chart.resize();
}
