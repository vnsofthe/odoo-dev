openerp.web_action_add_button = function (instance) {
    var QWeb = instance.web.qweb;
    instance.web.Sidebar.include({
        init: function(parent) {
            this._super(parent);
            this.items.web_action_add_button = [];
        },
    });
    instance.web.ListView.include({
        init: function(parent, dataset, view_id, options){
            this._super(parent, dataset, view_id, options);
            this.action_buttons = [];
            this.action_buttons_with_menu = [];
            this.$action_buttons_with_menu = undefined;
        },
        load_list: function(data) {
            this._super(data);
            var self = this;
            if (this.ViewManager.action){
                if (this.is_action_enabled('add_button')){
                    if (this.ViewManager.action.id) {
                        this.rpc('/web/action/add/button/get_buttons', {
                            action_id: this.ViewManager.action.id}).done(function(items) {
                                self.action_buttons = [];
                                self.action_buttons_with_menu = [];
                                self.add_web_action_add_button(items);
                                self.add_buttons();
                            });
                    }
                }
            }
        },
        add_buttons: function(){
            var self = this;
            if (this.$action_buttons_with_menu)
                this.$action_buttons_with_menu.remove();

            var el = QWeb.render("WebActionAddButton", {
                action_buttons: this.action_buttons,
                action_buttons_with_menu: this.action_buttons_with_menu,
            });
            this.$action_buttons_with_menu = $(el);
            var sidebar = this.ViewManager.$el.find('.oe_view_manager_sidebar')[0];
            this.$action_buttons_with_menu.insertAfter($(sidebar));
            function buttonclicked (){
                var section = $(this).data('section');
                var index = $(this).data('index');
                var item = self.sidebar.items[section][index];
                self.do_action(item, {
                    on_close: function() {
                        self.reload();
                    },
                });
            }
            this.$action_buttons_with_menu.find('li a').click(buttonclicked);
            this.$action_buttons_with_menu.find('.oe_button').click(buttonclicked);
        },
        add_web_action_add_button: function(items) {
            var self = this;
            _(_(items).keys()).each(function(item) {
                if (item == 'false') {
                    self.action_buttons = items[item];
                } else {
                    self.action_buttons_with_menu.push({
                        name: item,
                        buttons: items[item],
                    });
                }
                _(items[item]).each(function(action) {
                    self.sidebar.items.web_action_add_button[action.id] = action;
                });
            });
        },
    });
};
