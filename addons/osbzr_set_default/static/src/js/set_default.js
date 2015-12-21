openerp.osbzr_set_default = function(session) {
    var _t = session.web._t;
    var has_action_id = false;
    var instance = openerp;
    session.web.Sidebar = session.web.Sidebar.extend({
       start: function() {
                var self = this;
                this._super(this);
                var view = this.getParent();
                if(view.fields_view.type=='form'){           
                        self.add_items('other', [
                            {   label: _t('Set Defaults'),
                                callback: self.on_click_set_defaults
                                },
                                ]);
                }     
            },
        on_click_set_defaults:function(item) {
            var view = this.getParent();
            view.open_defaults_dialog();
        },
    }); 
};