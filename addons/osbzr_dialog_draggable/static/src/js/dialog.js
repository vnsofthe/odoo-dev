// http://www.3e3c.com/erp/odoo/171.html
openerp.osbzr_dialog_draggable = function(instance) {

    instance.web.Dialog.include({
        open: function() {
            var self = this;
            this._super.apply(this, arguments);
            $(".modal.in").draggable({
                handle: ".modal-header"
            });
            return this;
        }
    });
}