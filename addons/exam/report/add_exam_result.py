import time
from openerp.report import report_sxw


class add_exam_result(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(add_exam_result, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_result_detail':self._get_result_detail,
        })

    def _get_result_detail(self, subject_ids, result):
        sub_obj = self.pool.get('exam.subject')
        subject_ids = sub_obj.search(self.cr, self.uid, [('exam_id','=',result.id),('subject_id','in',subject_ids)])
        result_data = []
        for subject in sub_obj.browse(self.cr, self.uid, subject_ids):
                
                result_data.append({
                    'subject':subject.subject_id and subject.subject_id.name or '',
                    'max_mark':subject.maximum_marks or '',
                    'mini_marks':subject.minimum_marks or '',
                    'obt_marks':subject.obtain_marks or '',
                 })
                
        return result_data

report_sxw.report_sxw('report.add_exam_result', 'exam.result', 'addons/exam/report/exam_result_report.rml', parser=add_exam_result, header="internal")



#        