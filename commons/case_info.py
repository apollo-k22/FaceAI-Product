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
        self.target_type = 1  # if 1, single photo, if 2, multi-photo, if 3, entire folder as target
