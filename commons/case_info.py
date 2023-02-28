from PyQt5.QtCore import QObject


class CaseInfo(object):

    def __init__(self):
        super().__init__()
        self.case_number = ''
        self.case_PS = ''
        self.examiner_name = ''
        self.examiner_no = ''
        self.remarks = ''
        self.is_used_old_cases = False
        self.subject_image_url = ''
        self.target_image_urls = []
