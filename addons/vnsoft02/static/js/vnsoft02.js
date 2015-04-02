/**
 * Created by Administrator on 2015/4/2.
 */
openerp.vnsoft02 = function(instance){
    instance.web.Dialog.include({
            open: function () {
                var self = this;
                this._super.apply(this, arguments);
                $(".modal.in").draggable({
                    handle: ".modal-header"
                });
                return this;
            }
        }
    );
}