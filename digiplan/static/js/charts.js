const chart3Element = document.getElementById("chart3");
const chart3 = echarts.init(chart3Element);
const chart4Element = document.getElementById("chart4");
const chart4 = echarts.init(chart4Element);
const detailed_overview_chart = echarts.init(document.getElementById("detailed_overview_chart"));
const ghg_overview_chart = echarts.init(document.getElementById("ghg_overview_chart"));

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

function isVisible(element) {
  if (element.offsetParent) return true;
  return false;
}

function resizeChart() {
  setTimeout(function () {
    if (isVisible(chart3Element)) chart3.resize();
    if (isVisible(chart4Element)) chart4.resize();
    detailed_overview_chart.resize();
    ghg_overview_chart.resize();
  }, 200);
}

chart3.setOption(option);
chart4.setOption(option);
detailed_overview_chart.setOption(detailed_overview_option);
ghg_overview_chart.setOption(ghg_overview_option);

window.addEventListener("resize", resizeChart);
document.addEventListener("show.bs.tab", resizeChart);
