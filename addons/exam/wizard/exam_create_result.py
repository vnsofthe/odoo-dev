from openerp.osv import osv

class exam_create_result(osv.TransientModel):

    _name = 'exam.create.result'

    def generate_result(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}  
        if not context.get('active_ids'):
            
            return {}
        exam_obj = self.pool.get("exam.exam")
        student_obj = self.pool.get('student.student')
        result_obj = self.pool.get("exam.result")
        result_subject_obj = self.pool.get("exam.subject")
        print exam_obj,result_obj,result_subject_obj;
        for result in self.browse(cr, uid, ids, context):
            print 'result',result
            for exam in exam_obj.browse(cr, uid, context.get('active_ids'), context):
                print 'exam', exam
                for timetable in exam.standard_id:
                    print'timetable',timetable
                    student_ids = student_obj.search(cr, uid, [('standard_id', '=', timetable.standard_id.id), ('division_id', '=', timetable.division_id.id), ('medium_id', '=', timetable.medium_id.id)])
                    print student_ids
                    for student in student_obj.browse(cr, uid, student_ids, context):
                        print 'student',student
                        result_exists = result_obj.search(cr, uid, [('standard_id', '=', timetable.standard.id), ('division_id', '=', timetable.division_id.id), ('medium_id', '=', timetable.medium_id.id), ('student_id','=', student.id)])
                        print 'result_exists',result_exists
                        if not result_exists:
                            print exam.id,student.id,timetable.class_id.id 
                            result_id = result_obj.create(cr, uid, {'s_exam_ids': exam.id,
                                                                    'student_id': student.id,
                                                                    'standard_id': timetable.class_id.id,
                                                                    'division_id': timetable.division_id.id,
                                                                    'medium_id': timetable.medium_id.id})
                            print' result_id',result_id
                            
                        
                            for line in timetable.timetable_ids:
                                print 'exam_id',exam_id
                                print 'subject_id'
                                print 'minimum_marks'
                                print 'maximum_marks'
                                
                                result_subject_obj.create(cr, uid, {'exam_id': result_id,
                                                                    'subject_id': line.subject_id and line.subject_id.id or False,
                                                                    'minimum_marks': line.subject_id and line.subject_id.minimum_marks or 0.0,
                                                                    'maximum_marks': line.subject_id and line.subject_id.maximum_marks or 0.0})
                            
        return {}

exam_create_result()
