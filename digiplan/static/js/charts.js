const chart3 = echarts.init(document.getElementById('chart3'));
const chart4 = echarts.init(document.getElementById('chart4'));
const chart5 = echarts.init(document.getElementById('chart5'));
const chart6 = echarts.init(document.getElementById('chart6'));

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
      data: ['Jahre']
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
      data: [
        60
      ],
    },
    {
      name: '2035',
      type: 'bar',
      color: '#06DFA7',
      data: [
        80
      ]
    }
  ]
};

const optionResults = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'bar'
    }
  ]
};

function resizeChart() {
  setTimeout(function () {
    chart3.resize();
    chart4.resize();
    chart5.resize();
    chart6.resize();
  }, 200);
}

chart3.setOption(option);
chart4.setOption(option);
chart5.setOption(optionResults);
chart6.setOption(optionResults);

window.addEventListener('resize', resizeChart);
