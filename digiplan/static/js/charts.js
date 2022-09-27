const chart1 = echarts.init(document.getElementById('chart1'));
const chart2 = echarts.init(document.getElementById('chart2'));
const chart3 = echarts.init(document.getElementById('chart3'));
const chart4 = echarts.init(document.getElementById('chart4'));
const chart5 = echarts.init(document.getElementById('chart5'));
const chart6 = echarts.init(document.getElementById('chart6'));

regionChart1 = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200],
      type: 'bar'
    }
  ]
};

regionChart2 = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200],
      type: 'bar'
    }
  ]
};

resultChart1 = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200],
      type: 'bar'
    }
  ]
};

resultChart2 = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200],
      type: 'bar'
    }
  ]
};

resultViewChart1 = {
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

resultViewChart2 = {
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

/* option = {
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
}; */

function resizeChart() {
  setTimeout(function () {
    chart1.resize();
    chart2.resize();
    chart3.resize();
    chart4.resize();
    chart5.resize();
    chart6.resize();
  }, 200);
};

chart1.setOption(regionChart1);
chart2.setOption(regionChart2);
chart3.setOption(resultChart1);
chart4.setOption(resultChart2);
chart5.setOption(resultViewChart1);
chart6.setOption(resultViewChart2);

window.addEventListener('resize', resizeChart);
