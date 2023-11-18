import json


class Attributes:
    def __init__(self):
        self.teacher_id = None
        self.section_id = None

    def to_json(self):
        attributes = {
            'teacher_id': self.teacher_id,
            'section_id': self.section_id,
        }

        # section and teacher pointer
        with open('./attributes.json', 'w') as json_file:
            json.dump(attributes, json_file, indent=4)



