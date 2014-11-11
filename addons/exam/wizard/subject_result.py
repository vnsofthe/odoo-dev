from openerp.osv import osv,fields

class subject_result_wiz(osv.osv_memory):
    
    _name= "subject.result.wiz"
    _description= "Subject Wise Result"
    
    _columns={
                'result_ids': fields.many2many("exam.subject",'subject_result_wiz_rel','result_id',"exam_id","Exam Subjects",select=1),
              }
    
    def result_report(self, cr, uid, ids, context):
            data = self.read(cr, uid, ids)[0]
            
            datas = {
                     'ids': context.get('active_ids',[]),
                     'form': data,
                     
                     'model':'exam.result',
            }
            return {'type': 'ir.actions.report.xml', 'report_name': 'add_exam_result', 'datas':datas }
    
subject_result_wiz()



# def _get_activeresult(self, cr, uid, context=None):
#         list  = []
#         if not list:
#             list.append(ID)
#         return self.pool.get('exam.result').search(cr, uid, [("active","=",True)], context=None)