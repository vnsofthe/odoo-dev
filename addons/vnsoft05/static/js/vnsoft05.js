/**
 * Created by Administrator on 2015/7/10.
 */
openerp.vnsoft05 = function(instance){
    instance.web.form.FieldBinary.include({
            init: function(field_manager, node) {
                var self = this;
                this._super.apply(this, arguments);
                this.max_upload_size = 100 * 1024 * 1024;
            }
        }
    );
}