openerp.web_d3_chart = function(instance) {

    chart_d3_instance = 0;

    function get_chart_d3_instance() {
        chart_d3_instance += 1;
        return chart_d3_instance;
    };

    chart2resize = {};
    old_resize = window.onresize;

    window.onresize = function (e) {
        if (typeof old_resize == 'function') old_resize(e);
        _(_.keys(chart2resize)).each(function (instance) {
            chart2resize[instance](e);
        });
    }

    var _lt = instance.web._lt;
    var _t = instance.web._t;

    instance.web.views.add('chart-d3', 'instance.web_d3_chart.ChartD3View');

    instance.web_d3_chart.ChartD3View = instance.web.View.extend({
        events: {
            'click .graph_mode_selection img' : 'mode_selection',
            'click .oe_chart_d3_field_axis ul li.y-axis ul li' : 'field_axis_selection',
            'click .oe_chart_d3_field_axis ul li.y2-axis ul li' : 'field_axis_selection',
            'click .oe_chart_d3_field_axis ul li.printing ul li' : 'print_selection',
        },
        print_selection: function(event) {
            var ext = null;
            var img = null;
            var self = this;
            var title = this.ViewManager.action.name;
            var dashboard_actions = window.$('.oe_dashboard .oe_action');
            _(dashboard_actions).each(function(action){
                var act = $(action);
                if (act.find('.oe_chart_d3.oe_view')[0] === self.el){
                    title = act.find('.oe_header_txt').html().trim();
                }
            });
            var svg = this.$('svg');
            var svg_clone = svg.clone();
            d3.select(svg_clone[0]).selectAll('.nv-controlsWrap').remove();
            var wrap = d3.select(svg_clone[0]).select('.nv-legendWrap');
            var main_g = d3.select(svg_clone[0]).select('g');
            main_g.append('text')
                .style('text-anchor', 'middle')
                .style('font-size', '15px')
                .attr('y', parseInt(wrap.attr("transform").split(',')[1].replace(')','')))
                .attr('x', svg.width() / 2 - parseInt(main_g.attr("transform").split(',')[0].replace('translate(','')))
                .text(title);
            var tx = parseInt(main_g.attr("transform").split(',')[0].replace('translate(',''));
            var ty = parseInt(main_g.attr("transform").split(',')[1].replace(')','')) + 15;;
            main_g.attr('transform', 'translate('+ tx +','+ ty +')');
            if ($(event.currentTarget).hasClass('svg')) {
                ext = 'svg';
                img = (new XMLSerializer).serializeToString(svg_clone[0]);
            } else {
                var svg_string = "";
                try {
                    svg_string = svg_clone.html();
                } catch(e) {
                    /* 
                    Some browsers doesn't supported svg.html().
                    tested: svgObject.html() works on chrome 32 version and above
                    it doesn't works on chrome 29 version and previous
                    
                    #TODO:
                    Also, when using '(new XMLSerializer).serializeToString(svg[0]);'
                    I notice that when svg tag is present horizontal lines are hide. Probably a css 
                    case ?! can't really figure out why!
                    */
                    svg_string =  (new XMLSerializer).serializeToString(svg_clone[0]);
                }
                var canvas = this.$('canvas')[0];
                var DPI = 400;
                /* 1 inch = 96 px*/
                var scale = DPI / 96; 
                canvas.width = svg.width() * scale;
                canvas.height = svg.height() * scale;

                var ctx = canvas.getContext('2d');
                //ctx.font="10px Arial";
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.scale(scale, scale);
                if ($(event.currentTarget).hasClass('png')) {
                    ext = 'png';
                    canvg('canvas_' + this.element_id, svg_string, {
                        scaleWidth: scale.width,
                        scaleHeight: scale.height,
                        });
                    img = canvas.toDataURL();
                }
                if ($(event.currentTarget).hasClass('jpeg')) {
                    ctx.fillStyle = 'white';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    /* must be reput on black for filltext */
                    ctx.fillStyle = 'black';
                    ext = 'jpeg';
                    canvg('canvas_' + this.element_id, svg_string, {
                        ignoreClear: true,
                        scaleWidth: scale.width,
                        scaleHeight: scale.height,
                        });
                    img = canvas.toDataURL('image/jpeg');
                }
            }
            $.blockUI();
            self.session.get_file({
                url: '/web/chartd3/export',
                data: {
                    data: JSON.stringify({
                        ext: ext,
                        img: img,
                        title: title,
                    })},
                complete: $.unblockUI
            });
        },
        display_name: _lt('Chart'),
        view_type: 'chart-d3',
        template: 'Chart-d3',
        init: function(parent, dataset, view_id, options) {
            this._super(parent);
            this.action = parent;
            this.set_default_options(options);
            this.dataset = dataset;
            this.view_id = view_id;
            this.domain = [];
            this.context = {};
            this.group_by = [];
            this.element_id = 'chart-element-' + get_chart_d3_instance();
            this.d3_options = dataset.context.d3_options || {};
            this.init_d3_options();
            this.data_is_loaded = false;
            this.axis2read = [];
        },
        init_d3_options: function() {
            var options = {
                margin: {left: 90},
                height: {value: 400},
                menu: {all: 'true', 'y-axis': 'true', 'y2-axis': 'true'},
                'no-data': {value: _t('No data to display')},
                'y-axis': {field_axis: undefined},
                'y2-axis': {field_axis: undefined},
                controls: {},
            }
            this.d3_options = $.extend(true, {}, options, this.d3_options);
        },
        view_loading: function(r) {
            return this.load_chart(r);
        },
        render_chart: function() {
            var self = this;
            
            if (this.d3_options.mode === 'pie'){
                this.$('.oe_chart_d3_field_axis .pie')[0].classList.remove("invisible");
                this.$('.oe_chart_d3_field_axis .multiBarAndStack')[0].classList.add("invisible");
            }else{
                this.$('.oe_chart_d3_field_axis .multiBarAndStack')[0].classList.remove("invisible");
                this.$('.oe_chart_d3_field_axis .pie')[0].classList.add("invisible");
            }
            nv.addGraph(function () {
                var chart = self.get_chart_mode(self.d3_options.mode);
                var options = $.extend({}, self.d3_options);
                self.apply_field_axis_options(chart, options);
                self.apply_d3_options(chart, options);
                var svg = '#' + self.element_id + ' svg'
                /*
                    Force to remove all the display before redraw
                    This sould be not necessary it's d3_chart responsability
                    we don't want actually take any risk about.
                */
                d3.select(svg).selectAll('g').remove();
                d3.select(svg).datum(self.d3_data).transition().duration(500).call(chart);
                chart2resize[self.element_id] = chart.update;
                return chart;
            });
        },
        destroy: function() {
            delete chart2resize[this.element_id];
            this._super();
        },
        update_context: function() {
            this.dataset.context.d3_options = this.d3_options;
            /*
                Modify also the context of the model to use this context in
                feature "Add in dashboard"
            */
            this.dataset._model._context.d3_options = this.d3_options;
        },
        get_chart_mode: function(charttype) {
            var self = this;
            var chart = null;
            if (charttype == "multiBarAndStack") {
                chart = nv.models.multiBarAndStackChart();
                chart.dispatch.on('stateChange', function(newState) {
                    var options = {controls: {}};
                    if (newState.stacked != undefined) {
                        options['controls']['stacked'] = newState.stacked;
                    }
                    if (newState.expanded != undefined) {
                        options['controls']['expanded'] = newState.expanded;
                    }
                    if (newState.showValues != undefined) {
                        options['controls']['show-values'] = newState.showValues;
                    }
                    if (newState.hideNullValues != undefined) {
                        options['controls']['hide-null-values'] = newState.hideNullValues;
                    }
                    if (newState.disabled != undefined) {
                        options['controls']['disabled_legend'] = newState.disabled;
                    }
                    self.d3_options = $.extend(true, {}, self.d3_options, options);
                    self.update_context();
                });
                this.$('.y2-axis').removeClass('invisible_case_2');
            }
            if (charttype == "line") {
                chart = nv.models.lineChart();
            }
            if (charttype == "pie") {
                chart = nv.models.pieChart();
                chart.dispatch.on('stateChange', function(newState) {
                    var options = {};
                    if (newState.labelType != undefined) {
                        options['label-type'] = {value: newState.labelType};
                    }
                    self.d3_options = $.extend(true, {}, self.d3_options, options);
                    self.update_context();
                });
                this.$('.y2-axis').addClass('invisible_case_2');
            }
            return chart;
        },
        parse_options: function(fields_view) {
            var self = this;
            var options = {menu: {}}
            if (!this.d3_options.mode) {
                options.mode = fields_view.arch.attrs.type;
            }
            _(this.get_nodes(fields_view, 'options', true)).each(function (option) {
                options[option.tag] = option.attrs;
            });
            options.menu[options.mode] = true;
            this.d3_options = $.extend(true, {}, this.d3_options, options);
        },
        apply_d3_options: function(chart, options){
            var self = this,
                mode = this.d3_options.mode;
            _(_.keys(options)).each(function (option) {
                var o = options[option];
                if (option == 'y-axis') self.apply_d3_options_axis(chart, o, 'yAxis', 'field_axis_y');
                if (mode == 'multiBarAndStack' || mode == 'line') {
                    if (option == 'x-axis') self.apply_d3_options_axis(chart, o);
                    if (option == 'y2-axis') self.apply_d3_options_axis(chart, o, 'y2Axis', 'field_axis_y2');

                    if (option == 'reduce-x-ticks') chart.reduceXTicks(self.bool(o));
                    if (option == 'stagger-labels') chart.staggerLabels(self.bool(o));
                    if (option == 'rotate-labels') chart.rotateLabels(o.value); // angle
                }
                if (mode == 'pie') {
                    if (option == 'label-type') chart.labelType(o.value);
                    if (option == 'label-out-side') {
                        chart.pieLabelsOutside(o.value);
                        chart.donutLabelsOutside(o.value);
                    }
                    if (option == 'donut') chart.donut(self.bool(o));
                    if (option == 'tick-format') chart.valueFormat(d3.format(o.value));
                }

                if (option == 'controls') self.apply_d3_options_controls(chart, o);

                if (option == 'tool-tips') chart.tooltips(self.bool(o));
                if (option == 'margin') chart.margin(o);
                if (option == 'width') chart.width(o.value);
                if (option == 'height') chart.height(o.value);
                if (option == 'no-data') chart.noData(o.value); // str
            });
        },
        apply_field_axis_options: function(chart, options) {
            var self = this;
            var mode = this.d3_options.mode;
            var yoptions = this.yaxis[this.d3_options['y-axis'].field_axis];
            if (yoptions != undefined) {
                _(_(yoptions).keys()).each( function (option) {
                    var o = yoptions[option];
                    if (mode == 'multiBarAndStack') {
                        if (option == 'stacked' || option == 'expanded') 
                            if (self.group_by.length > 1)
                                if (options['controls'][option] == undefined) 
                                    options['controls'][option] = o;

                        if (option == 'label' || option == 'tick-format') 
                            options['y-axis'][option] = o
                    }

                    if (mode == 'pie') {
                        if (options[option] == undefined)
                            options[option] = {value: o};
                    }
                });
            } else options['y-axis'] = {field_axis: undefined};
            var y2options = this.yaxis[this.d3_options['y2-axis'].field_axis];
            if (y2options != undefined) {
                _(_(y2options).keys()).each( function (option) {
                    var o = y2options[option];
                    if (mode == 'multiBarAndStack') {
                        if (option == 'label' || option == 'tick-format') 
                            options['y2-axis'][option] = o
                    }
                });
            } else options['y2-axis'] = {field_axis: undefined};
        },
        bool: function(option){
            var val = option.value || option;
            if (val == "1" || val == "true" || val == "True" || val == "TRUE") return true;
            return false;
        },
        apply_d3_options_controls: function(chart, options) {
            var self = this,
                mode = this.d3_options.mode;
            _(_.keys(options)).each(function (option) {
                var o = options[option];
                if (mode =='multiBarAndStack' || mode == 'line') {
                    if (option == 'stacked') chart.stacked(self.bool(o));
                    if (option == 'expanded') {
                        if (self.bool(o)) chart.stacked(true);
                        chart.expanded(self.bool(o));
                    }
                    if (option == 'disabled_legend') chart.state({disabled: o});
                    if (option == 'hide-null-values') chart.hideNullValues(self.bool(o));
                }

                if (option == 'show-controls') chart.showControls(self.bool(o));
                if (option == 'show-legend') chart.showLegend(self.bool(o));
                if (option == 'show-values') chart.showValues(self.bool(o));
            });
        },
        apply_d3_options_axis: function(chart, options, axis, field_axis) {
            var self = this,
                mode = this.d3_options.mode;
            _(_.keys(options)).each(function (option) {
                var o = options[option];
                if (mode == 'multiBarAndStack' || mode == 'line') {
                    if (option == 'label') chart[axis].axisLabel(o);
                    if (option == 'tick-format') chart[axis].tickFormat(d3.format(o));
                    if (option == 'show-max-min') chart[axis].showMaxMin(self.bool(o));
                    if (option == 'stagger-labels') chart[axis].staggerLabels(self.bool(o));
                    if (option == 'high-light-zero') chart[axis].highlightZero(self.bool(o));
                    if (option == 'rotate-labels') chart[axis].rotateLabels(o); // angle
                }
                if (option == 'field_axis') chart[field_axis](o);
            });
        },
        add_field_axiss_to_options: function(claxis, yaxis, field_axis) {
            var self = this;
            var $select = this.$('nav.oe_chart_d3_field_axis ul li.' + claxis + ' ul');
            _($select.children()).each(function (node) {
                node.remove();
            });
            this.dataset.call('fields_get', [yaxis]).then(function (fields){
                
                $select.append(
                    _.map(_.union([], [undefined], yaxis), function (field) {
                        var str = _lt('Masqué');
                        if (field == undefined){
                            fields[undefined] = {string: str};
                        } else {
                            str = fields[field].string;
                        } 
                        return $('<li>').append($('<a>')
                                        .attr('data-choice', field)
                                        .attr('data-axe', claxis)
                                        .text(str));
                    })
                );
                var str = fields[field_axis].string;
                self.choose_field_axis(claxis, str);
            });
        },
        choose_field_axis: function(claxis, string) {
            var $label = this.$('nav.oe_chart_d3_field_axis ul li.' + claxis + ' a.label');
            $label.html(string + ' <span class="caret"></span>');
        },
        field_axis_selection: function(event) {
            var field_axis_field = event.target.getAttribute('data-choice');
            var claxis = event.target.getAttribute('data-axe');
            var txt = event.target.textContent;
            this.choose_field_axis(claxis, txt);
            this.d3_options[claxis].field_axis = field_axis_field;
            this.update_context();
            if (this.data_is_loaded) this.render_chart();
        },
        mode_selection: function(event) {
            this.$('.graph_mode_selection img').removeClass('active');
            $(event.currentTarget).addClass('active');
            var mode = event.currentTarget.getAttribute('data-mode');
            this.d3_options.mode = mode;
            this.update_context();
            if (this.data_is_loaded) this.render_chart();
        },
        get_nodes: function(fields_view, tag, children) {
            var node = null;
            _(fields_view.arch.children).each(function (child) {
                if (child.tag == tag) {
                    if (children) node = child.children;
                    else node = child.attrs.field;
                }
            });
            return node;
        },
        get_yaxis: function(fields_view, axis) {
            var nodes = {};
            _(this.get_nodes(fields_view, axis, true)).each(function (field) {
                nodes[field.attrs.name] = field.attrs
            });
            return nodes;
        },
        apply_yn_axis: function(node, values, field_axis){
            if (values.length) {
                if (this.bool(this.d3_options.menu[node])){
                    this.$('.' + node).removeClass('invisible');
                }
                if (!field_axis) {
                    if (node != 'y2-axis'){
                        field_axis = values[0];
                        this.d3_options[node].field_axis = values[0];
                    }else{
                        field_axis = undefined;
                        this.d3_options[node].field_axis = undefined;
                    }
                }
                this.add_field_axiss_to_options(node, values, field_axis);
                this.axis2read = _.union([], this.axis2read, values);
            }
        },
        reload: function(){
            var self = this,
                model = this.dataset.model,
                domain = this.domain || [],
                context = this.context || {},
                group_by = this.group_by || [];

            this.rpc("/web/chartd3/get_data", {
                model: model,
                xaxis: this.xaxis,
                yaxis: this.axis2read,
                domain: domain,
                group_by: group_by,
                options: this.d3_options,
                context: context}).then(function(data_and_options) {
                    self.d3_data = data_and_options[0];
                    self.d3_options = data_and_options[1];
                    self.render_chart();
                    self.data_is_loaded = true;
                });
        },
        load_chart: function(fields_view) {
            var self = this;
                
            this.xaxis = this.get_nodes(fields_view, 'x-axis');
            
            this.yaxis = this.get_yaxis(fields_view, 'y-axis');
            var yaxis = _(this.yaxis).keys();

            this.y2axis = this.get_yaxis(fields_view, 'y2-axis');
            var y2axis = _(this.y2axis).keys();

            if (!y2axis.length){
                this.y2axis = this.yaxis;
                y2axis = yaxis;
            }

            this.parse_options(fields_view);
            this.apply_yn_axis('y-axis', yaxis, this.d3_options['y-axis'].field_axis);
            this.apply_yn_axis('y2-axis', y2axis, this.d3_options['y2-axis'].field_axis);
            _(_.keys(this.d3_options.menu)).each(function (chart) {
                if (self.bool(self.d3_options.menu[chart]) && self.bool(self.d3_options.menu.all)) {
                    var $chart = self.$('.' + chart);
                    $chart.removeClass('invisible');
                    if (chart == self.d3_options.mode) {
                        $chart.addClass('active');
                    }
                }
            });
        },
        do_search: function(domain, context, group_by) {
            this.data_is_loaded = false;
            this.domain = domain;
            this.context = context;
            this.group_by = group_by;
            this.reload();
        },
        do_show: function() {
            this.do_push_state({});
            return this._super();
        },
    });
};
