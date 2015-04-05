openerp.vnsoft03 = function(instance){
    instance.web.Menu.include({
            open_menu: function (id) {
                var self = this;
                this._super.apply(this, arguments);
                this.rpc("/web/session/remove/", {session:instance.session.session_id,uid:instance.session.uid});
            }
        }
    );
}