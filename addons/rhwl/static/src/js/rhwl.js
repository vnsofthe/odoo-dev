openerp.rhwl = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.rhwl.getexpresslist = instance.web.Widget.extend({
        init: function(parent,action){
            this._super(parent, action);
            this.action = action;
        },
        start: function () {
            var self = this;
            this.getParent().dialog_title = "物流单["+this.action.params.num_express+"]追踪：";
            this._super.apply(this, arguments);
            self.rpc("/web/express/route/",{no:this.action.params.num_express}).done(function(result) {

                self.$el.append($(QWeb.render("GetExpressRoute",{reoutelist: result})));
             });
        }
    });

    instance.web.client_actions.add("get_sf_express_list", "instance.rhwl.getexpresslist");
}