const chart1 = echarts.init(document.getElementById('chart1'));
const chart2 = echarts.init(document.getElementById('chart2'));
const chart3 = echarts.init(document.getElementById('chart3'));
const chart4 = echarts.init(document.getElementById('chart4'));

option = {
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
      ],
      markLine: {
        data: [{  name: 'Ziel 2035', yAxis: 90}]
      }
    }
  ]
};

function resizeChart() {
  setTimeout(function () {
    chart1.resize();
    chart2.resize();
    chart3.resize();
    chart4.resize();
  }, 200);
};

chart1.setOption(option);
chart2.setOption(option);
chart3.setOption(option);
chart4.setOption(option);

window.addEventListener('resize', resizeChart);