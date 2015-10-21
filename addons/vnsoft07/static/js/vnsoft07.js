/**
 * Created by Administrator on 2015/4/2.
 */
openerp.vnsoft07 = function(instance){
    instance.web.ListView.include({
            on_sidebar_export: function () {
                if(instance.session.uid==1){
                    new instance.web.DataExport(this, this.dataset).open();
                }else{
                    alert("Export only for Administrator.");
                }
            }
        }
    );
}