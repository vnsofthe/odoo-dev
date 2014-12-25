openerp.rhwl = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.rhwl.getexpresslist = instance.web.Widget.extend({
        template: "ChangePassword",
        init: function(parent,action){
            this._super(parent, action);
            this.action = action;
        },
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            console.log(this.action)
        }
    });

    instance.web.client_actions.add("get_sf_express_list", "instance.rhwl.getexpresslist");
}