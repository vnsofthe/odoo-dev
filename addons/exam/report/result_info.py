import time

from openerp.report import report_sxw

class result(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(result, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_lines': self.get_lines,
            'get_exam_data':self.get_exam_data,
            'get_grade':self.get_grade,
        })
        
    def get_grade(self,result_id, student):
        list=[]
        value={}
        for stu_res in student.year.grade_id.grade_ids:
            value.update({'fail':stu_res.fail})
            flag=stu_res.fail
        list.append(value)
        return list

    def get_lines(self,result_id, student):
        list=[]
        for sub_id in result_id:
            value={}
            for sub in sub_id.result_ids:
                list.append({
                              'standard_id':sub_id.standard_id.standard_id.name,
                              'name':sub.subject_id.name,
                              'code':sub.subject_id.code,
                              'maximum_marks':sub.maximum_marks,
                              'minimum_marks':sub.minimum_marks,
                              'obtain_marks':sub.obtain_marks,
                              's_exam_ids':sub_id.s_exam_ids.name
                })
        return list

    def get_exam_data(self,result_id, student):
        list=[]
        value={}
        final_total= 0
        count=0
        per=0.0
        for res in result_id:
            for sub in res.result_ids:
                count+=1
                per=float(res.total/count)
            final_total= final_total + res.total
            value.update({
                              'result':res.result,
                              'percentage':per,
                              'total':final_total,
                })
           
        list.append(value)
        return list

report_sxw.report_sxw('report.result', 'student.student', 'exam/report/result_information_report.rml', parser=result, header="internal")

