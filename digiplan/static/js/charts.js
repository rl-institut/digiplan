// Sidebar
const anteil_ee_chart = echarts.init(document.getElementById("anteil_ee_chart"));
const co2_emissionen_chart = echarts.init(document.getElementById("co2_emissionen_chart"));
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

const anteil_ee = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    top: '10%',
    left: '15%',
    right: '15%',
    bottom: '18%',
    height: '120',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['0','2021', '2045', '0'],
    boundaryGap: false
  },
  yAxis: {
    show: true,
    type: 'value',
    maxValueSpan: '100',
    nameLocation: 'end',
    nameTextStyle: 'Roboto',
    width: '76',
    heigth: '32',
    fontWeight: '300',
    fontSize: '14',
  },
  series: [
    {
      type: 'line',
      boundaryGap: false,
      smooth: 0.6,
      lineStyle: {
        color: '#06DFA7',
        width: 1
      },
      data: [90,90,90,90]
    },
    { 
      type: 'bar',
      barWidth:'16',
      data: [
        {
          value: 0, 
          itemStyle: {
            color: '#F4F6F7'
          }
        },
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
    },
  ],
}

const co2_emissionen = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    top: '10%',
    left: '15%',
    right: '15%',
    bottom: '18%',
    height: '120',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['0','2021', '2045', '0'],
    boundaryGap: false
  },
  yAxis: {
    show: true,
    type: 'value',
    maxValueSpan: '100',
    nameLocation: 'end',
    nameTextStyle: 'Roboto',
    width: '76',
    heigth: '32',
    fontWeight: '300',
    fontSize: '14',
  },
  series: [
    {
      type: 'line',
      boundaryGap: false,
      smooth: 0.6,
      lineStyle: {
        color: '#E6A100',
        width: 1
      },
      data: [30,30,30,30]
    },
    { 
      type: 'bar',
      barWidth:'16',
      data: [
        {
          value: 0, 
          itemStyle: {
            color: '#F4F6F7'
          }
        },
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
    },
  ],
}

const option = {
  title: {
    text: 'Anteil Erneuerbare \nEnergien (%)',
    textStyle: {
      color: '#002C50',
      fontWeight: 300,
      fontFamily: 'Roboto',
      fontSize: 14
    }
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
      // prettier-ignore
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
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  legend: {
    show: true,
    bottom: '15',
    itemWidth: 14,
    itemHeight: 14
  },
  grid: {
    top: '10%',
    left: '3%',
    right: '25%',
    bottom: '18%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Mt CO₂-\nEmissionen',
      nameLocation: 'end',
      nameTextStyle: 'Roboto',
        width: '76',
        heigth: '32',
      fontWeight: '300',
      fontSize: '14'
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
      barWidth: '16',
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
  fontStyle: 'Roboto',
  fontSize: '14',
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  legend: {
    show: true,
    bottom: '15',
    itemWidth: 14,
    itemHeight: 14
  },
  grid: {
    top: '10%',
    left: '3%',
    right: '25%',
    bottom: '18%',
    containLabel: true
  },
  xAxis:  {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Mt CO₂-\nEmissionen',
      nameLocation: 'end',
      nameTextStyle: 'Roboto',
        width: '76',
        heigth: '32',
      fontWeight: '300',
      fontSize: '14',

  },
  yAxis: {
    show: true,
    type: 'category',
    data: ['Ziel', 'Szenario', 'Status Quo', '1990'],
    nameTextStyle: 'Roboto',
    fontWeight: '400',
    fontSize: '14',
    axisTick: {
      show: false
    }
  },
  series: [
    {
      name: 'GHG',
      type: 'bar',
      barWidth: '16',
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
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  legend: {
    show: true,
    bottom: '15',
    itemWidth: 14,
    itemHeight: 14
  },
  grid: {
    top: '10%',
    left: '3%',
    right: '25%',
    bottom: '18%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'TWh',
      nameLocation: 'end',
      nameTextStyle: 'Roboto',
        width: '76',
        heigth: '32',
      fontWeight: '300',
      fontSize: '14'
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
      barWidth: '16',
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
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  legend: {
    show: true,
    bottom: '15',
    itemWidth: 14,
    itemHeight: 14
  },
  grid: {
    top: '10%',
    left: '3%',
    right: '25%',
    bottom: '18%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Mt CO₂-\nEmissionen',
      nameLocation: 'end',
      nameTextStyle: 'Roboto',
        width: '76',
        heigth: '32',
      fontWeight: '300',
      fontSize: '14'
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
      barWidth: '16',
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
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  legend: {
    show: true,
    bottom: '15',
    itemWidth: 14,
    itemHeight: 14
  },
  grid: {
    top: '10%',
    left: '3%',
    right: '25%',
    bottom: '18%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Anzahl Autos',
      nameLocation: 'end',
      nameTextStyle: 'Roboto',
        width: '76',
        heigth: '32',
      fontWeight: '300',
      fontSize: '14'
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
      barWidth: '16',
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
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  legend: {
    show: true,
    bottom: '15',
    itemWidth: 14,
    itemHeight: 14
  },
  grid: {
    top: '10%',
    left: '3%',
    right: '25%',
    bottom: '18%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    show: true,
    position: 'bottom',
    name: 'Mt CO₂-\nEmissionen',
      nameLocation: 'end',
      nameTextStyle: 'Roboto',
        width: '76',
        heigth: '32',
      fontWeight: '300',
      fontSize: '14'
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
      barWidth: '16',
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
    anteil_ee_chart.resize();
    co2_emissionen_chart.resize();
    chart3.resize();
    chart4.resize();
    detailed_overview_chart.resize();
    ghg_overview_chart.resize();
    electricity_overview_chart.resize();
    electricity_THG_chart.resize();
    mobility_overview_chart.resize();
    mobility_THG_chart.resize();
  }, 200);
}

// Sidebar
anteil_ee_chart.setOption(anteil_ee);
co2_emissionen_chart.setOption(co2_emissionen);
chart3.setOption(option);
chart4.setOption(option);
detailed_overview_chart.setOption(detailed_overview_option);
ghg_overview_chart.setOption(ghg_overview_option);
electricity_overview_chart.setOption(electricity_overview);
electricity_THG_chart.setOption(electricity_THG);
mobility_overview_chart.setOption(mobility_overview);
mobility_THG_chart.setOption(mobility_THG);

window.addEventListener("resize", resizeCharts);
document.addEventListener("show.bs.tab", resizeCharts);
