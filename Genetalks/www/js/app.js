var server_ip = '222.240.161.196'; //服务器地址
var port = '8069'; //端口号
var DBname = 'dev'; //数据库名
var options = "";
var cancel = false;
var preBreakNum = 0; //前一次填写的破损数量
var demo = [];
var i = 0;
var preDemoCode = ''; //修改样品代号之前的号码
var hisInfo; //所有试管物流信息
var count = -1;
var numforYingShou = -1;
var receiveNew = []; //新到快递数组
var username = "";
var pwd = "";
var all_count = -1; //医院现有试管数
var hospitalName;
var result = null; //结果查询
var isLogin = false; //用户是否登陆
var relevanceData; //重抽血样品信息

//登陆函数
function login() {
  username = $("#userName").val().trim();
  pwd = $("#pwd").val().trim();
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/login", {
      Username: username,
      Pwd: pwd
    },
    function(data) {
      if (data.statu == 200) {
        hospitalName = data.hospitalName;
        $("#hospitalName").html(data.hospitalName);
        all_count = data.AllCount;
        $("#leftAllCount").html(data.AllCount);
        loadHislog();
        var checking = document.getElementById("remeber");
        //如果记住密码被选中
        if (checking.checked) {
          addCookie("password", pwd, 30);
        } else {
          addCookie("password", "", 0);
        }
        isLogin = true;
        //登陆成功将用户名保存至Cookie,时间为一个月
        addCookie("userName", username, 30);
        activate_page("#mainpage");
      } else if(data.statu==500) {
        alertMsg("提示",data.errtext);
      }else{
        alertMsg("提示","Sorry，登陆出现异常，请稍后再试。。。");
      }
    });
}

//结果查询函数
function loadResult() {
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/result", {
    Username: username,
    Pwd: pwd
  }, function(data) {
    result = data;
    showResult();
  });
}


//结果查询的页面显示函数
function showResult() {
  //写入异常个数
  $("#bs-accordion-0").html("<div style='color:green;margin-bottom:15px;'>特殊样品数：<span onclick='showSpecialDemo()' class='label label-danger'>" + result[0].exception + "</span></div>");
  //先清空一次,防止二次刷新的时候数据累加
  for (var i = 1; i < result.length; i++) { //外循环写入下拉列表,由于第一个为异常，下标从1开始     
    var info = '<div class="panel widget panel-warning" style="margin-bottom: 10px;"><div class="panel-heading"><h4 class="panel-title" data-toggle="collapse" href="#bs-accordion-group-' + i + '" data-parent="#bs-accordion-0">' + result[i].time + '</h4></div><div id="bs-accordion-group-' + i + '" class="panel-collapse collapse"><div class="panel-body"><table class="hovertable"><thead><tr><th style="width: 30%;">姓名</th><th style="width: 20%;">ID号</th><th style="width: 50%;">状态</th></tr></thead><tbody id="tab' + i + '"></tbody></table></div></div></div>';
    $("#bs-accordion-0").append(info);
    for (var j = 0; j < result[i].datas.length; j++) { //内循环写入具体table数据
      var obj = result[i].datas[j];
      var tr = '';
      if (obj.status == '检验结果阳性') { //加个判断 如果状态为阳性或重抽血则背景色改变
        tr = '<tr style="background-color:rgba(241, 221, 221, 1);" id="' + obj.code + '" onclick="goto(this)"><td>' + obj.name + '</td><td>' + obj.code + '</td><td>' + obj.status + '</td></tr>';
      } else if (obj.status == '需重采血') {
        tr = '<tr style="background-color:rgba(251, 247, 226, 1);" id="' + obj.code + '" onclick="goto(this)"><td>' + obj.name + '</td><td>' + obj.code + '</td><td>' + obj.status + '</td></tr>';
      } else {
        tr = '<tr id="' + obj.code + '" onclick="goto(this)"><td>' + obj.name + '</td><td>' + obj.code + '</td><td>' + obj.status + '</td></tr>';
      }
      $("#tab" + i).append(tr);
    }
  }
}

//结果查询页面的搜索函数
function resultSearch() {
  var inp = $("#resultInp").val().trim(); //获得输入框输入的值
  if (inp != "") {
    $.post("http://" + server_ip + ":" + port + "/web/crmapp/result", {
      Username: username,
      Pwd: pwd,
      name: inp
    }, function(data) {
      showResultSearch(data);
    });
  } else {
    showResult();
  }
}

//显示特殊样品的函数
function showSpecialDemo() {
  var specialDemos = [];
  for (var i = 1; i < result.length; i++) {
    for (var j = 0; j < result[i].datas.length; j++) {
      var obj = result[i].datas[j];
      if (obj.status == '检验结果阳性' || obj.status == '需重采血') {
        var specialDemo = {
          status: obj.status,
          code: obj.code,
          name: obj.name,
          time: result[i].time
        };
        specialDemos.push(specialDemo);
      }
    }
  }
  showResultSearch(specialDemos);
}

//结果查询页面搜索结果和特殊样品结果展示
function showResultSearch(obj) {
  if (obj.length > 0) {
    var tab = '<table class="hovertable" id="result" style="margin-bottom:10px;"><tr><th style="width:30%">时间</th><th style="width:30%">姓名(代号)</th><th style="width:40%">状态</th></tr></table>';
    $("#bs-accordion-0").html(tab); //写入table框架
    for (var i = 0; i < obj.length; i++) {
      var dat = obj[i];
      var res = '';
      if (dat.status == '检验结果阳性') { //加个判断 如果状态为阳性或重抽血则背景色改变
        res = '<tr style="background-color:rgba(241, 221, 221, 1);" id="' + dat.code + '" onclick="goto(this)"><td>' + dat.time + '</td><td>' + dat.name + '<br>(' + dat.code + ')' + '</td><td>' + dat.status + '</td></tr>';
      } else if (dat.status == '需重采血') {
        res = '<tr style="background-color:rgba(251, 247, 226, 1);" id="' + dat.code + '" onclick="goto(this)"><td>' + dat.time + '</td><td>' + dat.name + '<br>(' + dat.code + ')' + '</td><td>' + dat.status + '</td></tr>';
      } else {
        res = '<tr id="' + dat.code + '" onclick="goto(this)"><td>' + dat.time + '</td><td>' + dat.name + '<br>(' + dat.code + ')' + '</td><td>' + dat.status + '</td></tr>';
      }
      $("#result").append(res); //逐个写入数据
    }
    var back = '<button type="button" class="btn btn-info btn-block" onclick="javascript:showResult()"><i class="glyphicon glyphicon-chevron-left button-icon-left" data-position="left"></i>返回</button>';
    $("#bs-accordion-0").append(back);
  } else {
    $("#bs-accordion-0").html('<div class="alert alert-danger" role="alert">无搜索结果！</div>');
  }
}

// function showDemos123() {
//   for (var i = 0; i < demo.length; i++) {
//     $("#123").append("{demo:" + demo[i].code + ",perdemo:" + demo[i].preCode + "}");
//   }
//   $("#123").append("<br>-------------------------------<br>");
// }

//隐藏提交订单按钮的函数
function hideSendBtn() {
  if (demo.length < 1) {
    $("#confrimOut").hide();
    $("#body-one").hide();
    $("#breakNumErr").hide();
  }
}

//扫描物流单号的侧边按钮，切换手动输入和扫码输入功能
function writeBySelf() {
  if (options != "write") {
    $("#scanner").removeAttr("onclick");
    //$("#scanner").removeAttr("placeholder");
    $("#scanner").attr({
      "placeholder": "请输入订单号码..."
    });
    $("#scannerLogo").removeAttr("class");
    $("#scannerLogo").addClass("glyphicon glyphicon-barcode");
    options = "write";
  } else {
    $("#scanner").attr({
      "onclick": "wuliu()"
    });
    $("#scanner").attr({
      "placeholder": "扫码或点击右侧手动填写"
    });
    $("#scannerLogo").removeAttr("class");
    $("#scannerLogo").addClass("glyphicon glyphicon-pencil");
    options = "wuliu";
  }
}

//扫描物流单号函数
function wuliu() {
  options = "wuliu";
  intel.xdk.device.scanBarcode();
}

//系统统一扫码函数
document.addEventListener("intel.xdk.device.barcode.scan", function(evt) {
  intel.xdk.notification.beep(2);
  if (evt.type == "intel.xdk.device.barcode.scan") {
    if (evt.success === true) {
      var url = evt.codedata;
      if (options == "addDemo") {
        if (!isExist(url)) {
          var oneDemo = {
            code: url,
            preCode: ""
          };
          demo.push(oneDemo);
          $("#body-one").show();
          $("#confrimOut").show();
          showDemo();
          $('#continueScan').modal('show');
        } else {
          alertMsg("提示","该样品已经扫描");
        }
      } else if (options == "wuliu") {
        $("#scanner").val(url);
      } else if (options == "recieve") {
        $("#receiveScanner").val(url);
        showReceiveOderItems();
      } else {
        cancel = true;
        if (options == "addDemo" || options == "wuliu") {
          activate_subpage("#send");
        } else if (options == "recieve") {
          activate_subpage("#recieve");
        }
      }
    }
  }
});

//向样品代号的td中拼接一个input输入框
function changeDemoCode(obj) {
  $(obj).removeAttr("onclick");
  preDemoCode = $(obj).text().trim();
  var id = obj.id;
  id = id.substring(1, id.length);
  $(obj).html("<input class='form-control on input-xs' id='i" + id + "' onblur='fillDemoCode(this)' value=" + $(obj).text() + "></input>");
  $("#i" + id).focus();
}

//将input框中的值填充到td中
function fillDemoCode(obj) {
  var id = obj.id;
  id = id.substring(1, id.length);
  var text = obj.value.trim();
  if (!isExist(text)) {
    changeFromDemo(text);
    $("#t" + id).html(text);
  } else {
    $("#t" + id).html(preDemoCode);
  }
  $("#t" + id).attr({
    "onclick": "changeDemoCode(this)"
  });
}

//从样品代号序列中修改一个样品
function changeFromDemo(afterCode) {
  for (var i = 0; i < demo.length; i++) {
    if (preDemoCode == demo[i].code) {
      demo[i].code = afterCode;
      $("#" + preDemoCode).attr("id", afterCode);
      return;
    }
  }
}

//从样品代号序列中删除一个样品
function delFromDemo(obj) {
  var td = obj.parentNode.parentNode.previousSibling;
  var code = td.innerHTML.trim();
  for (var i = 0; i < demo.length; i++) {
    if (code == demo[i].code) {
      for (var j = i; j < demo.length; j++) {
        if (j == (demo.length - 1)) {
          demo.pop(demo[j]);
        } else {
          demo[j] = demo[j + 1];
        }
      }
    }
  }
  showDemo();
}

//新增样品时判断demo中是否存在该样品
function isExist(code) {
  for (var i in demo) {
    if (demo[i].code == code) {
      return true;
    }
  }
  return false;
}

//展示样品代号序列的函数
function showDemo() {
  if (demo.length < 1) {
    $("#body-one").hide();
    $("#confrimOut").hide();
    preBreakNum = 0;
    $(".breakCount").text(0);
  } else {
    $("#tbody_y").html("");
    for (var i = 0; i < demo.length; i++) {
      if (demo[i].preCode != "") {
        $("#tbody_y").append("<tr><td>" + (i + 1) + "</td><td id='t" + demo[i].code + "'onclick='changeDemoCode(this)'>" + demo[i].code + "</td><td><div class='btn-group'><input id=" + demo[i].code + " type='button' class='btn btn-primary btn-xs' onclick='relevance(this)' value='重关联'/><input type='button' onclick='delFromDemo(this)' class='btn btn-danger btn-xs' value='删除'></div></td></tr>");
        for (var j = 0; j < relevanceData.length; j++) {
          if (demo[i].preCode == relevanceData[j].id) {
            $("#tbody_y").append("<tr><td colspan='2' style='color:blue'>" + relevanceData[j].name + "<span class='label label-info'>" + relevanceData[j].id + "</span></td><td><button id='r" + demo[i].preCode + "' class='btn btn-warning btn-xs' onclick='delRelevance(this)'>取消关联</button></td></tr>");
          }
        }
      } else {
        $("#tbody_y").append("<tr><td>" + (i + 1) + "</td><td id='t" + demo[i].code + "'onclick='changeDemoCode(this)'>" + demo[i].code + "</td><td><div class='btn-group'><input id=" + demo[i].code + " type='button' class='btn btn-primary btn-xs' onclick='relevance(this)' value='关联'/><input type='button' onclick='delFromDemo(this)' class='btn btn-danger btn-xs' value='删除'></div></td></tr>");
      }
    }
    $(".demoCount").text(demo.length);
    $(".allCount").text(demo.length);
  }
}

//关联重抽血对象函数
function relevance(obj) {
  /*设置表格中字体的位置居中*/
  $("table").css("text-align", "center");
  $("table thead tr th").css("text-align", "center");
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/reuse", {
      Username: username,
      Pwd: pwd,
      IsTakeBlood: "yes"
    },
    function(data) {
      relevanceData = data;
      var tbody = $("#relevance_bd");
      tbody.html("");
      for (var i in data) {
        var newtr = $("<tr id='" + data[i].id + "," + obj.id + "'onclick='inputRelevanceId(this)'></tr>").appendTo(tbody); //动态插入一行
        var newtd2 = $("<td style='color:blue'>").appendTo(newtr);
        newtd2.html(data[i].name + "<span class='label label-info'>" + data[i].id + "</span>");
        var newtd3 = $("<td>").appendTo(newtr);
        for (var j = 0; j < demo.length; j++) {
          if (demo[j].preCode == data[i].id) {
            newtd3.html("<span class='label label-success'>" + demo[j].code + "</span>");
          }
        };
      }
    });
  $('#relevance').modal('show');
}

//向发货样品数组中指定对象添加重抽血关联
function inputRelevanceId(obj) {
  var str = obj.id;
  var arr = str.split(",");
  for (var i = 0; i < demo.length; i++) {
    if (demo[i].code == arr[1]) {
      demo[i].preCode = arr[0];
    }
  }
  showDemo();
  $('#relevance').modal('hide');
}

//取消关联
function delRelevance(obj) {
  var id = obj.id;
  id = id.substring(1, id.length);
  for (var i = 0; i < demo.length; i++) {
    if (demo[i].preCode == id) {
      demo[i].preCode = "";
    }
  }
  showDemo();
}

//调用扫码功能添加样品
function addDemo() {
  options = "addDemo";
  intel.xdk.device.scanBarcode();
  // var oneDemo = {
  //   code: i++,
  //   preCode: ""
  // };
  // demo.push(oneDemo);
  // $("#body-one").show();
  // $("#confrimOut").show();
  // showDemo();
  // $('#continueScan').modal('show');
}

//添加损坏样品数
function addBreak() {
  var breakText = $("#breakInput").val().trim();
  var breakNum = parseInt(breakText);
  var preallCount = parseInt($("#allCount").text().trim());
  if (isNaN(breakNum)) {
    $("#breakInputDiv").removeAttr("class");
    $("#breakInputDiv").addClass("form-group has-error has-feedback");
    $("#breakNumErr div").text("我只认得数字哦~");
    $("#breakNumErr").show();
    //$("#element").popover('show');
  } else {
    if (breakNum > preallCount) {
      $("#breakInputDiv").removeAttr("class");
      $("#breakInputDiv").addClass("form-group has-error has-feedback");
      $("#breakNumErr div").text("破损数大于总数了。。。");
      $("#breakNumErr").show();
    } else {
      $("#breakInputDiv").removeAttr("class");
      $(".breakCount").text(breakNum);
      $(".demoCount").text(preallCount - breakNum);
      $("#toggle1").removeAttr("class");
      $("#toggle1").addClass("panel-collapse collapse");
      $("#breakNumErr").hide();
      preBreakNum = breakNum;
    }
  }
}

//提交发货信息
function upload() {
  var demoText = '';
  for (var i = 0; i < demo.length; i++) {
    if (i == demo.length - 1) {
      demoText += '{"code":"' + demo[i].code + '","preCode":"' + demo[i].preCode + '"}';
    } else {
      demoText += '{"code":"' + demo[i].code + '","preCode":"' + demo[i].preCode + '"},';
    }
  }
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/deliver", {
    Username: username,
    Pwd: pwd,
    packageID: $("#scanner").val(),
    damaged: preBreakNum,
    demos: "[" + demoText + "]"
  }, function(data) {
    if (data.statu == '200') {
      $(".breakCount").text(0);
      $("#scanner").val("");
      preBreakNum = 0;
      demo.length = 0;
      $("#body-one").hide();
      $("#confrimOut").hide();
      $("#sendConfrim").modal("hide");
      alertMsg("提示","提交成功！");
    } else {
      alertMsg("提示","提交失败，请重试！");
    }
  });
}

//扫描收货快递单号
function shouHuo() {
  options = "recieve";
  intel.xdk.device.scanBarcode();
}

//获得当前时间和一个月之前的函数
function getTimes() {
  var today = new Date();
  var aMouthAgo = new Date();
  aMouthAgo.setDate(aMouthAgo.getDate() - 30);
  var startTime = aMouthAgo.getFullYear() + "/" + (aMouthAgo.getMonth() + 1) + "/" + (aMouthAgo.getDate() > 10 ? aMouthAgo.getDate() : "0" + aMouthAgo.getDate());
  var endTime = today.getFullYear() + "/" + (today.getMonth() + 1) + "/" + (today.getDate() > 10 ? today.getDate() : "0" + today.getDate());
  return [startTime, endTime];
}

//收货页面显示时触发
function loadReceive() {
  if (receiveNew.length > 0) {
    $("#hasNewOrder").show();
    $("#receiveConfirm").hide();
    $("#noNewOrder").hide();
    $("#receiveMark").hide();
    var shtbody = $("#receiveTbody");
    shtbody.html("");
    for (var i in receiveNew) {
      var newtr = $("<tr/>").appendTo(shtbody);
      var newtd1 = $("<td/>").appendTo(newtr);
      newtd1.html(receiveNew[i].time); //时间
      var newtd2 = $("<td id='receivedGoodsId'/>").appendTo(newtr);
      newtd2.html(receiveNew[i].logIdCompany[0]); //快递单号
      var newtd3 = $("<td/>").appendTo(newtr);
      newtd3.html(receiveNew[i].state); //状态
    }
  } else {
    $("#hasNewOrder").hide();
    $("#noNewOrder").show();
  }
}

//收货页面的侧边按钮，切换手动输入和扫码输入功能
function receiveWriteBySelf() {
  if (options != "receiveWrite") {
    $("#receiveScanner").removeAttr("onclick");
    $("#receiveScanner").attr({
      "placeholder": "请输入订单号码..."
    });
    $("#receiveScannerLogo").removeAttr("class");
    $("#receiveScannerLogo").addClass("glyphicon glyphicon-barcode");
    options = "receiveWrite";
  } else {
    $("#receiveScanner").attr({
      "onclick": "shouHuo()"
    });
    $("#receiveScanner").attr({
      "placeholder": "请扫码或点击右侧输入单号"
    });
    $("#receiveScannerLogo").removeAttr("class");
    $("#receiveScannerLogo").addClass("glyphicon glyphicon-pencil");
  }
}

//展示新快递里的试管数
function showReceiveOderItems() {
  var orderId = $("#receiveScanner").val();
  console.log(orderId);
  var shtbody = $("#receiveConfirmTbody");
  shtbody.html("");
  for (var i = 0; i < receiveNew.length; i++) {
    if (orderId == (receiveNew[i].logIdCompany[0])) {
      //向服务器发送快递单号，获得应收试管数
      $.post("http://" + server_ip + ":" + port + "/web/crmapp/goodsnum", {
        Username: username,
        Pwd: pwd,
        goodsID: orderId
      }, function(data) {
        $("#receiveConfirm").show();
        var newtr = $("<tr/>").appendTo(shtbody);
        var newtd1 = $("<td/>").appendTo(newtr);
        newtd1.html(orderId); //快递单号
        var newtd2 = $("<td id='numforYingShou'/>").appendTo(newtr);
        newtd2.html(data.goodsNum); //应收试管数
        var newtd3 = $("<td/>").appendTo(newtr);
        $("<input type='text' class='form-control input-sm' id='secvalue'/>").appendTo(newtd3);
      });
    }else{
      $("#receiveConfirm").hide();
    } 
  }
}

//确认收货按钮：确认应收试管和实收试管数
function sureForSH() {
  var num=$("#numforYingShou").text();
  var goodsId=$("#receivedGoodsId").text();
  var secvalue = $('#secvalue').val();
  var marksValue ="";
  if (num!= secvalue) { //不匹配时显示备注信息
    $("#receiveMark").show();
    marksValue = $("#markId01").val();
    if (marksValue.trim() == "") {
      alertMsg("提示","请填写原因");
      return;
    }
  }else{
    $("#receiveMark").hide();
  }
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/receive", {
    Username: username,
    Pwd: pwd,
    actualNumber: secvalue,
    marks: marksValue,
    hospitalName: hospitalName,
    goodsId:goodsId
  }, function(data) {
    alertMsg("提示","提交成功！");
    $("#receiveScanner").val("");
    loadHislog();
    loadReceive();
  });
}

//按要求搜索历史物流
function searchHislog() {
  var searchval = $('#searchlog').val().trim();
  var i = -1;
  var hislogs = [];
  for (var index in hisInfo) {
    var company = hisInfo[index].logIdCompany[1];
    var logId = hisInfo[index].logIdCompany[0];
    if ((hisInfo[index].time).match(searchval)) {
      i++;
      hislogs[i] = hisInfo[index];
    } else if ((hisInfo[index].state).match(searchval)) {
      i++;
      hislogs[i] = hisInfo[index];
    } else if ((company).match(searchval)) {
      i++;
      hislogs[i] = hisInfo[index];
    } else if ((logId).match(searchval)) {
      i++;
      hislogs[i] = hisInfo[index];
    } else if (searchval == "") {
      showSGWL(hisInfo);
    }
  }
  showSGWL(hislogs);
}

//加载所有物流函数
function loadHislog() {
  var Time = getTimes();
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/express", {
    Username: username,
    Pwd: pwd,
    startTime: Time[0],
    endTime: Time[1]
  }, function(data) {
    hisInfo = data;
    receiveNew = [];
    for (var i in data) {
      if (data[i].is_receiv && data[i].state == "待确认") {
        receiveNew.push(data[i]);
        console.log(data[i]);
      }
    }
    showLittleSpan();
  });
}

//显示试管物流的函数
function showSGWL(data) {
  var di = 0;
  var ri = 0;
  var deliverData = [];
  var receiveData = [];
  for (var i in data) {
    if (data[i].is_receiv) {
      receiveData[ri] = data[i];
      ri++;
    } else if (data[i].is_deliver) {
      deliverData[di] = data[i];
      di++;
    }
  }

  $("#logtb_deliver01").html("");
  $("#logtb_receive01").html("");
  //医院发出去的物流信息
  for (var i in deliverData) {
    var newtr = $("<tr/>").appendTo($("#logtb_deliver01"));
    var newtd1 = $("<td/>").appendTo(newtr);
    newtd1.get(0).innerHTML = deliverData[i].time;
    var newtd2 = $("<td/>").appendTo(newtr);
    newtd2.get(0).innerHTML = deliverData[i].logIdCompany;
    var newtd3 = $("<td/>").appendTo(newtr);
    newtd3.get(0).innerHTML = deliverData[i].state;
  }
  //医院接收的物流信息
  for (var i in receiveData) {
    var newtr = $("<tr/>").appendTo($("#logtb_receive01"));
    var newtd1 = $("<td/>").appendTo(newtr);
    newtd1.get(0).innerHTML = receiveData[i].time;
    var newtd2 = $("<td/>").appendTo(newtr);
    newtd2.get(0).innerHTML = receiveData[i].logIdCompany;
    var newtd3 = $("<td/>").appendTo(newtr);
    newtd3.get(0).innerHTML = receiveData[i].state;
  }
}

//重抽血页面
function ccx() {
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/reuse", {
      Username: username,
      Pwd: pwd,
      IsTakeBlood: "yes"
    },
    function(data) {
      var tbody = $("#tbd");
      showYxCcx(tbody, data, 1);
    });
}

//阳性样品页面
function yx() {
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/except", {
      Username: username,
      Pwd: pwd,
      isPositive: "yes"
    },
    function(data) {
      var tbody = $("#tbd2");
      showYxCcx(tbody, data, 0);
    });
}

//阳性重抽血的页面展示函数
function showYxCcx(tbody, data) {
  tbody.html("");
  for (var i in data) {
    var newtr = $("<tr id='" + data[i].id + "'onclick='goto(this)'></tr>").appendTo(tbody); //动态插入一行
    var newtd1 = $("<td>").appendTo(newtr); //动态插入一列
    newtd1.html(data[i].time);
    var newtd2 = $("<td style='color:blue;'>").appendTo(newtr);
    newtd2.html(data[i].name + "<span class='label label-info'>" + data[i].id + "</span>");
    var newtd3 = $("<td>").appendTo(newtr);
    newtd3.html(data[i].status);
    if ("未通知" == data[i].status) {
      newtr.addClass("danger");
      newtd3.css("color", "red");
    } else if ("已通知" == data[i].status) {
      newtr.addClass("success");
      newtd3.css("color", "green");
    } else {
      newtr.addClass("warning");
      newtd3.css("color", "blue");
    }
  }
}

//跳转到孕妇详细页面函数
function goto(obj, from) { //当选中一个tr点击的时候 查看详情的跳转函数 携带一个序列号跳到张鹏页面
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/woman", {
    Username: username,
    Pwd: pwd,
    pregnantWomanID: obj.id
  }, function(data) {
    console.log(data);
    options = "pregnantWomanMSG";
    activate_page("#pregnantWomanMSG");
    $("#pregnantWomanID").html(obj.id);
    $("#pregnantWomanName").text(data.pregnantWomanName);
    $("#gestationalWeeks").text(data.gestationalWeeks);
    $("#takeBloodTime").text(data.takeBloodTime);
    $("#state").text(data.state);
    $("#phoneNumber").attr("href", "tel:" + data.phoneNumber);
    $("#phoneNumber").html(data.phoneNumber);
    $("#emergencyCall").attr("href", "tel:" + data.emergencyCall);
    $("#emergencyCall").html(data.emergencyCall);
    $("#reTakeBloodID").text(data.reTakeBloodID);
    $("#report").text(data.report);
    $(".notice").attr("id", "p" + obj.id);
    if (data.btn == "1") {
      $("#notice").show();
      $("#noticeCancel").hide();
      $("#Inform").text("未通知该孕妇");
    } else if (data.btn == "0") {
      $("#notice").hide();
      $("#noticeCancel").show();
      $("#Inform").text("已通知该孕妇");
    } else {
      $("#notice").hide();
      $("#noticeCancel").hide();
      $("#Inform").text("已通知该孕妇");
    }
  });
}

//通知和取消通知函数
function Notice(obj, btn) {
  var id = obj.id;
  id = id.substring(1, id.length);
  $.post("http://" + server_ip + ":" + port + "/web/crmapp/notice/", {
    Username: username,
    Pwd: pwd,
    id: id,
    btn: btn
  }, function(data) {
    if (data.statu == "200") {
      if ($("#notice").is(':visible')) {
        $("#notice").hide();
        $("#noticeCancel").show();
      } else {
        $("#notice").show();
        $("#noticeCancel").hide();
      }
      yx();
      ccx();
      alertMsg("提示","修改成功！");
    } else {
      alertMsg("提示","修改失败，请重试");
    }
  });
};

//存Cookie的函数
function addCookie(name, value, expiresHours) {
  var cookieString = name + "=" + escape(value);
  //判断是否设置过期时间 
  if (expiresHours > 0) {
    var date = new Date();
    date.setTime(date.getTime + expiresHours * 3600 * 1000);
    cookieString = cookieString + "; expires=" + date.toGMTString();
  }
  document.cookie = cookieString;
}

//取Cookie的函数
function getCookie(name) {
  var strCookie = document.cookie;
  var arrCookie = strCookie.split("; ");
  for (var i = 0; i < arrCookie.length; i++) {
    var arr = arrCookie[i].split("=");
    if (arr[0] == name) return arr[1];
  }
  return "";
}

//显示数量小标签
function showLittleSpan() {
  if (receiveNew.length > 1) {
    $("#receive_tip_num").show();
    $("#receive_tip_num").html(receiveNew.length); //收货数量小标签
  } else {
    $("#receive_tip_num").hide();
  }
}

function alertMsg(title,msg){
  $("#alertTitle").html(title);
  $("#alertContent").html(msg);
  $('#alert').modal('show');
}