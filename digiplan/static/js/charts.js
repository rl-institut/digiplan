// Goals & scenarios
const renewable_share_goal_div = document.getElementById("renewable_share_goal_chart");
const renewable_share_goal_chart = echarts.init(renewable_share_goal_div);
const co2_emissions_goal_div = document.getElementById("co2_emissions_goal_chart");
const co2_emissions_goal_chart = echarts.init(co2_emissions_goal_div);

// Sidebar
const chart3Element = document.getElementById("chart3");
const chart3 = echarts.init(chart3Element);
const chart4Element = document.getElementById("chart4");
const chart4 = echarts.init(chart4Element);

// Results view
const detailed_overview_chart = echarts.init(document.getElementById("detailed_overview_chart"));
const ghg_overview_chart = echarts.init(document.getElementById("ghg_overview_chart"));
const electricity_overview_chart = echarts.init(document.getElementById("electricity_overview_chart"));
const electricity_THG_chart = echarts.init(document.getElementById("electricity_THG_chart"));
const mobility_overview_chart = echarts.init(document.getElementById("mobility_overview_chart"));
const mobility_THG_chart = echarts.init(document.getElementById("mobility_THG_chart"));

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
  fontSize: 14,
  fontWeight: 300,
  color: '#002C50'
};
const chart_legend = {
  show: true,
    bottom: '15',
    itemWidth: 14,
    itemHeight: 14
};

// CHARTS
const renewable_share_goal = {
  grid: chart_grid_goal,
  tooltip: chart_tooltip,
  textStyle: chart_text_style,
  xAxis: {
    type: 'category',
    data: ['2021', '2045'],
    axisTick: {
      show: false
    }
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
            color: '#C3D1DC'
          }
        },
        {
          value: 90, 
          itemStyle: {
            color: '#06DFA7'
          }
        },
      ],
      markLine: {
        silent: true,
        lineStyle: {
          color: '#00BC8C',
          type: 'solid'
        },
        symbol: 'none',
        data: [{
          yAxis: 90,
          label: {
            show: false
          }
        }]
      }
    },
  ],
}

const co2_emissions_goal = {
  grid: chart_grid_goal,
  tooltip: chart_tooltip,
  textStyle: chart_text_style,
  xAxis: {
    type: 'category',
    data: ['2021', '2045'],
    axisTick: {
      show: false
    }
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
          value: 90, 
          itemStyle: {
            color: '#C3D1DC'
          }
        },
        {
          value: 30, 
          itemStyle: {
            color: '#E6A100'
          }
        },
      ],
      markLine: {
        silent: true,
        lineStyle: {
          color: '#BE880B',
          type: 'solid'
        },
        symbol: 'none',
        data: [{
          yAxis: 30,
          label: {
            show: false
          }
        }]
      }
    },
  ],
}

const option = {
  textStyle: chart_text_style,
  title: {
    text: 'Anteil Erneuerbare \nEnergien (%)',
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    bottom: 10,
    data: ['2021', '2035']
  },
  toolbox: {
    show: false
  },
  calculable: true,
  xAxis: [
    {
      type: 'category',
      data: ['Jahre'],
      axisTick: {
        show: false
      }
    }
  ],
  yAxis: [
    {
      type: 'value',
      max: 100
    }
  ],
  series: [
    {
      name: '2021',
      type: 'bar',
      color: '#C3D1DC',
      barWidth: '32',
      data: [
        60
      ],
    },
    {
      name: '2035',
      type: 'bar',
      color: '#06DFA7',
      barWidth: '32',
      data: [
        80
      ]
    }
  ]
};

const detailed_overview_option = {
  tooltip: chart_tooltip,
  legend: chart_legend,
  grid: chart_grid_results,
  textStyle: chart_text_style,
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Mt CO₂-\nEmissionen',
    nameLocation: 'end',
    width: '76',
    heigth: '32',
  },
  yAxis: {
    type: 'category',
    data: ['Ziel Szenario\n (Verbrauch)',
    'Ziel Szenario\n (Erzeugung)',
    'Mein Szenario\n (Verbrauch)',
    'Mein Szenario\n (Erzeugung)',
    'Status Quo\n (Verbrauch)',
    'Status Quo\n (Erzeugung)'],
    axisTick: {
      show: false
    }
  },
  series: [
    {
      name: 'Wind',
      type: 'bar',
      barWidth: chart_bar_width_sm,
      stack: 'total',
      color: '#1F82C0',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0, 502, 0, 334, 0, 230]
    },
    {
      name: 'Freiflächen - PV',
      type: 'bar',
      stack: 'total',
      color: '#F6B93B',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0, 382, 0, 234, 0, 130 ]
    },
    {
      name: 'Aufdach - PV',
      type: 'bar',
      stack: 'total',
      color: '#FFD660',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0, 312, 0 , 254, 0 , 130]
    },
        {
      name: 'Bioenergie',
      type: 'bar',
      stack: 'total',
      color: '#98D47E',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0, 136, 0, 134, 0, 130]
    },
    {
      name: 'Konventionell',
      type: 'bar',
      stack: 'total',
      color: '#CFCFCF',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0 , 132, 0 , 534,0 , 1130 ]
    },
    {
      name: 'Verbrauch',
      type: 'bar',
      stack: 'total',
      color: '#e9e0c8',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [1450, 0 , 1440, 0 , 1800 ]
    },
  ]
};

const ghg_overview_option = {
  backgroundColor: '#FFFFFF',
  textStyle: chart_text_style,
  tooltip: chart_tooltip,
  legend: chart_legend,
  grid: chart_grid_results,
  xAxis:  {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Mt CO₂-\nEmissionen',
    nameLocation: 'end',
    width: '76',
    heigth: '32',
  },
  yAxis: {
    show: true,
    type: 'category',
    data: ['Ziel', 'Szenario', 'Status Quo', '1990'],
    fontWeight: '400',
    axisTick: {
      show: false
    }
  },
  series: [
    {
      name: 'GHG',
      type: 'bar',
      barWidth: chart_bar_width_sm,
      stack: 'total',
      color: '#C8D8E4',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [20, 20, 20, 20]
    },
    {
      name: 'Haushalte',
      type: 'bar',
      barWidth: '25',
      stack: 'total',
      color: '#74A9CF',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [12, 15, 30, 34]
    },
    {
      name: 'Industrie',
      type: 'bar',
        barWidth: '25',
      stack: 'total',
      color: '#FA9FB5',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [20, 20, 31, 34]
    },
    {
      name: 'XXX',
      type: 'bar',
        barWidth: '25',
      stack: 'total',
      color: '#FEC44F',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [5, 12, 15, 24]
    },
    {
      name: 'XXX',
      type: 'bar',
        barWidth: '25',
      stack: 'total',
      color: '#8C96C6',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [15, 20, 30, 34]
    }
  ]
};

const electricity_overview = {
  textStyle: chart_text_style,
  tooltip: chart_tooltip,
  legend: chart_legend,
  grid: chart_grid_results,
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'TWh',
    nameLocation: 'end',
    width: '76',
    heigth: '32',
  },
  yAxis: {
    type: 'category',
    data: ['Bedarf',
    'Ziel',
    'Mein Szeanrio',
    'Status Quo' ],
    axisTick: {
      show: false
    }
  },
  series: [
    {
      name: 'Wind',
      type: 'bar',
      barWidth: chart_bar_width_sm,
      stack: 'total',
      color: '#1F82C0',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0, 502, 400, 334]
    },
    {
      name: 'Freiflächen - PV',
      type: 'bar',
      stack: 'total',
      color: '#F6B93B',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0, 382, 300, 234 ]
    },
    {
      name: 'Aufdach - PV',
      type: 'bar',
      stack: 'total',
      color: '#FFD660',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0, 312, 280 , 254]
    },
        {
      name: 'Bioenergie',
      type: 'bar',
      stack: 'total',
      color: '#98D47E',
      label: {
        show: false
      },
      emphasis: {
      },
      data: [0, 136, 135, 134]
    },
    {
      name: 'Konventionell',
      type: 'bar',
      stack: 'total',
      color: '#1A1A1A',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [0 , 132, 200, 534 ]
    },
    {
      name: 'GHG',
      type: 'bar',
      stack: 'total',
      color: '#F5F5DC',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [400, 0 , 0, 0]
    },
    {
      name: 'Haushalte',
      type: 'bar',
      stack: 'total',
      color: '#A8DADC',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [360, 0 , 0, 0]
    },
     {
      name: 'Industrie',
      type: 'bar',
      stack: 'total',
      color: '#C27BA0',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [300, 0 , 0, 0]
    },
    {
      name: 'Sonstiges',
      type: 'bar',
      stack: 'total',
      color: '#B0BEC5',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [350, 0 , 0, 0]
    },
  ]
};

const electricity_THG = {
  textStyle: chart_text_style,
  tooltip: chart_tooltip,
  legend: chart_legend,
  grid: chart_grid_results,
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Mt CO₂-\nEmissionen',
    nameLocation: 'end',
    width: '76',
    heigth: '32',
  },
  yAxis: {
    type: 'category',
    data: ['Ziel',
    'Mein Szenario',
    'Status Quo',
    '1990' ],
    axisTick: {
      show: false
    }
  },
  series: [
    {
      name: 'GHG',
      type: 'bar',
      barWidth: chart_bar_width_sm,
      stack: 'total',
      color: '#F5F5DC',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [10, 30, 34, 37]
    },
    {
      name: 'Haushalte',
      type: 'bar',
      stack: 'total',
      color: '#A8DADC',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [20, 25 , 27, 30]
    },
     {
      name: 'Industrie',
      type: 'bar',
      stack: 'total',
      color: '#C27BA0',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [30, 40, 50, 60]
    },
    {
      name: 'Sonstiges',
      type: 'bar',
      stack: 'total',
      color: '#B0BEC5',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [30, 40 , 45, 50]
    },
  ]
};

const mobility_overview = {
  textStyle: chart_text_style,
  tooltip: chart_tooltip,
  legend: chart_legend,
  grid: chart_grid_results,
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Anzahl Autos',
    nameLocation: 'end',
    width: '76',
    heigth: '32',
  },
  yAxis: {
    type: 'category',
    data: ['Ziel\nSzenario',
    'Mein \nSzenario',
    'Status Quo'
    ],
    axisTick: {
      show: false
    }
  },
  series: [
    {
      name: 'Diesel',
      type: 'bar',
      barWidth: chart_bar_width_sm,
      stack: 'total',
      color: '#647078',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [50, 222, 400]
    },
    {
      name: 'Benzin',
      type: 'bar',
      stack: 'total',
      color: '#866E18',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [20, 182, 350]
    },
    {
      name: 'Hybrid',
      type: 'bar',
      stack: 'total',
      color: '#8FDCE1',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [100, 100, 140]
    },
        {
      name: 'E-Auto',
      type: 'bar',
      stack: 'total',
      color: '#98D47E',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [500, 300, 100]
    },
  ]
};

const mobility_THG = {
  textStyle: chart_text_style,
  tooltip: chart_tooltip,
  legend: chart_legend,
  grid: chart_grid_results,
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Mt CO₂-\nEmissionen',
    nameLocation: 'end',
    width: '76',
    heigth: '32'
  },
  yAxis: {
    type: 'category',
    data: ['Ziel',
    'Mein Szenario',
    'Status Quo',
    '1990' ],
    axisTick: {
      show: false
    }
  },
  series: [
    {
      name: 'Sockel',
      type: 'bar',
      barWidth: chart_bar_width_sm,
      stack: 'total',
      color: '#C8D8E4',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [30, 30, 30, 30]
    },
    {
      name: 'Konventionell',
      type: 'bar',
      stack: 'total',
      color: '#647078',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [15, 25 , 65, 100]
    },
     {
      name: 'Erneuerbare Energien',
      type: 'bar',
      stack: 'total',
      color: '#A8E7BA',
      label: {
        show: false
      },
      emphasis: {
        focus: 'series'
      },
      data: [65, 65, 38, 10]
    },
  ]
};

function isVisible(element) {
  if (element.offsetParent) return true;
  return false;
}

function resizeCharts() {
  setTimeout(function () {
    if (isVisible(renewable_share_goal_div)) renewable_share_goal_chart.resize();
    if (isVisible(co2_emissions_goal_div)) co2_emissions_goal_chart.resize();
    if (isVisible(chart3Element)) chart3.resize();
    if (isVisible(chart4Element)) chart4.resize();
    detailed_overview_chart.resize();
    ghg_overview_chart.resize();
    electricity_overview_chart.resize();
    electricity_THG_chart.resize();
    mobility_overview_chart.resize();
    mobility_THG_chart.resize();
  }, 200);
}

// Goals & scenarios
renewable_share_goal_chart.setOption(renewable_share_goal);
co2_emissions_goal_chart.setOption(co2_emissions_goal);

// Sidebar
chart3.setOption(option);
chart4.setOption(option);

// Results
detailed_overview_chart.setOption(detailed_overview_option);
ghg_overview_chart.setOption(ghg_overview_option);
electricity_overview_chart.setOption(electricity_overview);
electricity_THG_chart.setOption(electricity_THG);
mobility_overview_chart.setOption(mobility_overview);
mobility_THG_chart.setOption(mobility_THG);

window.addEventListener("resize", resizeCharts);
document.addEventListener("show.bs.tab", resizeCharts);
