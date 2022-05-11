const chart1 = echarts.init(document.getElementById('chart1'));
const chart2 = echarts.init(document.getElementById('chart2'));
const chart3 = echarts.init(document.getElementById('chart3'));
const chart4 = echarts.init(document.getElementById('chart4'));

const option = {
  title: {
    text: 'Anteil Erneuerbare Energien (%)',
    textStyle: {
      color: '#002C50',
      fontWeight: 'normal',
      fontFamily: 'Roboto',
      fontSize: 14
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  dataset: {
    source: [
      ['Kategorie', '2021'],
      ['2021', 100]
    ]
  },
  xAxis: { type: 'category' },
  yAxis: {},
  series: [{ type: 'bar' }],
  color: [
    '#002C50',
    '#FFE8B3'
  ],
  label: {
    normal: {
      position: 'top',
      distance: 10,
      show: true,
      formatter: ['Label Text'].join('\n')
    }
  }
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