/**
 * Created by Administrator on 2015/4/2.
 */
openerp.vnsoft_colresizable = function(instance){
    instance.vnsoft_colresizable.ListView = instance.web.ListView.include({
        view_loading: function() {
            this._super.apply(this, arguments);
            $(".oe_list_content>thead>tr>th:first").css("width","25px");
             $(".oe_list_content").colResizable({
                 liveDrag:true,
                 minWidth:25,
             });
        }
    });
}