from Pages.commons.case_info import CaseInfo


class ProbingResult(object):
    def __init__(self):
        super().__init__()
        self.case_info = CaseInfo()
        self.json_result = {'time_used': 2, 'thresholds': {}, 'faces': [], 'results': []}

    def is_matched(self):
        if self.json_result:
            results = self.json_result['results']
            for result in results:
                if float(result['confidence']) > 70.0:
                    return "Matched"
        return "Non Matched"

    def remove_json_item(self, item):
        if self.json_result['results'].index(item) >= 0:
            self.json_result['results'].remove(item)

