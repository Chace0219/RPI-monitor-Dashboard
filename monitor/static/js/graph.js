//var data = (['24/06/2017 07:57:18.552 am','12.8'],['25/06/2017 07:57:18.552 am','12.7'],['26/06/2017 07:57:18.552 am','12.1'],['27/06/2017 07:57:18.552 am','11.8'],['28/06/2017 07:57:18.552 am','12.9'],['29/06/2017 07:57:18.552 am','12.4'],['30/06/2017 07:57:18.552 am','12.6'],['01/07/2017 07:57:18.552 am','10.8'],['02/07/2017 07:57:18.552 am','12.5'],['03/07/2017 07:57:18.552 am','12.8'],['04/07/2017 07:57:18.552 am','12.3'],['06/07/2017 07:57:18.552 am','12.1']);

var data = ([
[Date.UTC(2013,5,2),0.7695],
[Date.UTC(2013,5,3),0.7648],
[Date.UTC(2013,5,4),0.7645],
[Date.UTC(2013,5,5),0.7638],
[Date.UTC(2013,5,6),0.7549],
[Date.UTC(2013,5,7),0.7562],
[Date.UTC(2013,5,9),0.7574],
[Date.UTC(2013,5,10),0.7543],
[Date.UTC(2013,5,11),0.7510],
[Date.UTC(2013,5,12),0.7498],
[Date.UTC(2013,5,13),0.7477],
[Date.UTC(2013,5,14),0.7492],
[Date.UTC(2013,5,16),0.7487],
[Date.UTC(2013,5,17),0.7480],
[Date.UTC(2013,5,18),0.7466],
[Date.UTC(2013,5,19),0.7521],
[Date.UTC(2013,5,20),0.7564],
[Date.UTC(2013,5,21),0.7621]
]);


Highcharts.chart('graphview', 
{
    chart: {
        zoomType: 'x'
    },
    title: {
        text: ''
    },
    subtitle: {
        text: document.ontouchstart === undefined ?
                'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
    },
    xAxis: {
        type: 'datetime'
    },
    yAxis: {
        title: {
            text: ''
        },
        labels: 
        {
            formatter: function() 
            {
                return this.value + 'A';
            }
        },
    },
    legend: {
        enabled: false
    },
    plotOptions: {
        area: 
        {
            fillColor: 
            {
                linearGradient: {
                    x1: 0,
                    y1: 0,
                    x2: 0,
                    y2: 1
                },
                stops: [
                    [0, Highcharts.getOptions().colors[0]],
                    [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                ]
            },
            marker: {
                radius: 2
            },
            lineWidth: 1,
            states: {
                hover: {
                    lineWidth: 1
                }
            },
            threshold: null
        }
    },

    series: 
    [{
        type: 'line',
        name: 'Site Electric',
        data: data
    }]
});    