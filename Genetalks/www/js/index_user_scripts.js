(function() {
    "use strict";
    function register_event_handlers() {
        $(".firstPage_btn").css("hieght","200px;");
        //记住用户名的功能
        $("#userName").val(getCookie("userName"));
        $("#pwd").val(getCookie("password"));

        //两个搜索框的监听事件
        $("#searchlog").bind("input propertychange", function() {
            searchHislog();
        });

        $("#resultInp").bind("input propertychange", function() {
            resultSearch();
        });
        $("#receiveScanner").bind("input propertychange", function() {
            showReceiveOderItems();
        });

        //导航栏返回按钮
        $(document).on("click", ".backToMainPage", function(evt) {
            window.history.back();
            showLittleSpan();
        });

        //登陆按钮
        $(document).on("click", "#loginBtn", function(evt) {
            login();
        });

        //注销按钮
        $(document).on("click", "#logoutBtn", function(evt) {
            $("#pwd").val("");
            isLogin = false;
            activate_page("#LoginPage");
        });

        //主页跳转至其他页面
        $(document).on("click", "#uib_w_15", function(evt) {
            showSGWL(hisInfo);
            activate_page("#logisticsMSG");
        });
        $(document).on("click", "#uib_w_16", function(evt) {
            loadReceive();
            activate_page("#receive");
        });
        $(document).on("click", "#uib_w_17", function(evt) {
            yx();
            activate_page("#yangxing");
        });
        $(document).on("click", "#uib_w_18", function(evt) {
            loadResult();
            activate_page("#DemoTrak");
        });
        $(document).on("click", "#uib_w_20", function(evt) {
            ccx();
            activate_page("#chongchouxie");
        });
        $(document).on("click", "#uib_w_19", function(evt) {
            hideSendBtn();
            activate_page("#send");
        });

        //孕妇详细页面返回按钮
        $(document).on("click", ".btn_pregnantWomanMSG", function(evt) {
            window.history.back();
        });

        //设置不自动旋转屏幕
        intel.xdk.device.setAutoRotate(false);
    }
    document.addEventListener("app.Ready", register_event_handlers, false);
    document.addEventListener("intel.xdk.device.ready", function() {
        intel.xdk.device.addVirtualPage();
    }, false);

    document.addEventListener("intel.xdk.device.hardware.back", function() {
        intel.xdk.device.addVirtualPage();
        if (!isLogin) {
            activate_page("#LoginPage");
        }else{
            window.history.back();
        }
    }, false);
})();