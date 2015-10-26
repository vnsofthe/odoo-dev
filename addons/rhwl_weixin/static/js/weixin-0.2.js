$.extend({
    getUrlVars: function () {
        var vars = [], hash;
        var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
        for (var i = 0; i < hashes.length; i++) {
            hash = hashes[i].split('=');
            vars.push(hash[0]);
            vars[hash[0]] = hash[1];
        }
        return vars;
    },
    getUrlVar: function (name) {
        return $.getUrlVars()[name];
    }
});

function charts_sale(idname,opt,model){
    // 路径配置
        require.config({
            paths: {
                echarts: 'http://echarts.baidu.com/build/dist'
            }
        });

        // 使用
        require(
            model,
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                var myChart = ec.init(document.getElementById(idname));

                var option = opt;

                // 为echarts对象加载数据
                myChart.setOption(option);
            }
        );
}

function sale_report1(){
    $.ajax({
            type: "POST",
            url: "/web/charts/sale/?openid=" + $.getUrlVar("openid") +"&code="+$.getUrlVar("code"),
            data: {},
            success: function (data) {
                //console.log(data);
                var option = {
                    title : {
                                text: '销售量分析'
                            },
                    tooltip: {show: true},

                    legend: {
                            selectedMode:"single",
                            selected: {'当月' : false,"上月":false,'三个月':false,'六个月':false,'一年':false },
                            data: ['总销量',"当月","上月","三个月","六个月","一年"]},
                    xAxis: [
                        {
                            type: 'category',
                            data: [],
                            axisLabel : {
                                show: true,
                                interval: 'auto',    // {number}
                                margin: 3
                            }
                        }
                    ],
                    yAxis: [ {type: 'value'}],
                    series: [
                        {"name": "总销量","type": "bar","data": [] },
                        {"name": "当月","type": "bar","data": [] },
                        {"name": "上月","type": "bar","data": [] },
                        {"name": "三个月","type": "bar","data": [] },
                        {"name": "六个月","type": "bar","data": [] },
                        {"name": "一年","type": "bar","data": [] }
                    ]
                };
                $.each(data,function(i,v){
                   option.xAxis[0].data[i]=v[1];
                   option.series[0].data[i]=v[2];
                   option.series[1].data[i]=v[3];
                   option.series[2].data[i]=v[4];
                   option.series[3].data[i]=v[5];
                   option.series[4].data[i]=v[6];
                   option.series[5].data[i]=v[7];
                });
                charts_sale("main",option,['echarts','echarts/chart/bar']);
            }
        });
}

function sale_report2(){
    var option = {
            title : { text: '样品检测异常比率'},
            tooltip : { trigger: 'axis' },
            legend: { data:["正常","重采血","阳性"] },

            grid: {y: 70, y2:30, x2:20},
            xAxis : [
                {
                    type : 'category',
                    data : [ ],
                    axisLabel : {
                                show: true,
                                interval: 'auto'
                            }
                }
            ],
            yAxis : [ {type : 'value'} ],
            series : [
                {
                    name:'正常',
                    type:'bar',
                    stack: '状态',
                    data:[]
                },
                {
                    name:'重采血',
                    type:'bar',
                    stack: '状态',
                    data:[]
                },
                {
                    name:'阳性',
                    type:'bar',
                    stack: '状态',
                    data:[]
                }
            ]
        };


    $.ajax({
        type: "POST",
        url: "/web/charts/sale2/?openid=" + $.getUrlVar("openid") +"&code="+$.getUrlVar("code"),
        data: {},
        success: function (data) {
            console.log(data);
            $.each(data,function(i,v){
                option.xAxis[0].data[i] = v[1];
                option.series[0].data[i]=v[2]-v[3]-v[4];
                option.series[1].data[i]=v[3];
                option.series[2].data[i]=v[4];
            });

            charts_sale("main",option,['echarts','echarts/chart/bar']);
        }
    });
}
//获取参数对象
//alert($.getUrlVars());
//获取参数a的值
//alert($.getUrlVar('a'));