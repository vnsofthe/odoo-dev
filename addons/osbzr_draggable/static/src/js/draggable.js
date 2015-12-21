openerp.osbzr_draggable = function(instance) {
    instance.web.ListView.include({
        load_list: function(data) {
            this._super.apply(this, arguments)

            // 选取列表的表头
            var elements = document.querySelectorAll('table[class=oe_list_content] thead tr[class=oe_list_header_columns] [class^=oe_list_header]');

            Array.prototype.forEach.call(elements, function(element, index) {

                // var element = ele;
                var DIFF_AMOUNT_TRIGGER_MOVE = 20;  // 鼠标位置距离左边界的距离

                if (element.addEventListener) {
                    element.addEventListener('mousedown', drag, false);
                }
                else if (element.attachEvent) {
                    element.attachEvent('onmousedown', drag);
                };

                function drag(e) {
                    e = e || window.event;
                    var style = window.getComputedStyle(element);
                    var origin_width = style.width;
                    var origin_width = parseInt(origin_width.slice(0, origin_width.length - 2));

                    // 获取目标元素的当前的静态位置
                    var origin_rect = element.getBoundingClientRect();
                    var origin_right = origin_rect.right;

                    if (origin_right - e.clientX < DIFF_AMOUNT_TRIGGER_MOVE) {
                        if (document.addEventListener) {  // 标准事件模型
                            document.addEventListener('mouseup', upHandler, true);
                            document.addEventListener('mousemove', moveHandler, true);
                        }
                        else if (document.attachEvent) {  // IE
                            document.setCapture();
                            document.attachEvent('onmouseup', upHandler);
                            document.attachEvent('onmousemove', moveHandler);
                            // 作为mouseup事件看待鼠标捕获的丢失
                            document.attachEvent('onlosecapture', upHandler);
                        }
                    };

                    function moveHandler(e) {
                        e = e || window.event;

                        deltaX = e.clientX - origin_right;

                        element.style.width = origin_width + deltaX + 'px';
                        origin_right = e.clientX;
                        origin_width = origin_width + deltaX;
                    };

                    function upHandler(e) {
                        e = e || window.event;

                        if (document.removeEventListener) {
                            document.removeEventListener('mouseup', upHandler, true);
                            document.removeEventListener('mousemove', moveHandler, true);
                        }
                        else if (document.detachEvent) {
                            document.detachEvent('onlosecapture', upHandler);
                            document.detachEvent('onmouseup', upHandler);
                            document.detachEvent('onmousemove', moveHanlder);
                            document.releaseCapture();
                        };
                    };

                    if (e.stopPropagation) {
                        e.stopPropagation();  // 标准模型
                    }
                    else {
                        e.cancelBubble = true;  // IE
                    };
                };
            });
        },
    });
};