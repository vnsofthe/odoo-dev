/**
 * Created by Administrator on 2015/7/10.
 */
openerp.rhwl_gene = function(instance){
    instance.web.form.FieldBinary.include({
            init: function(field_manager, node) {
                var self = this;
                this._super.apply(this, arguments);
                this.max_upload_size = 100 * 1024 * 1024;
            }
        }
    );

    instance.web.rhwl_gene = instance.web.rhwl_gene || {};
    instance.web.views.add('tree_rhwl_gene_tjs_online', 'instance.web.rhwl_gene.CompareListView');
    instance.web.rhwl_gene.CompareListView = instance.web.ListView.extend({
        init: function() {
            var self = this;
            this._super.apply(this, arguments);
            this.on('list_view_loaded', this, function() {
                if(self.__parentedParent.$el.find('.oe_generate_po').length == 0){
                    var button = $("<button type='button' class='oe_button oe_generate_po'>在线接收</button>")
                        .click(this.proxy('generate_gene_order'));
                    var tt = $("<span class='oe_alternative'><span class='oe_fade'>或 </span></span>")
                    self.__parentedParent.$el.find('.oe_list_buttons').append(tt).append(button);
                }
            });
        },
        generate_gene_order: function () {
            var self = this;
            new instance.web.Model(self.dataset.model).call("action_get_online_genes",[self.dataset.context.tender_id,self.dataset.context]).then(function(result) {
                location.reload() ;
            });
        },
    });
}

