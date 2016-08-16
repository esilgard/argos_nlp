class PreDoc:
    def __init__(self, time, text, mrn):
        self.timestamp=time
        self.text=text
        self.mrn=mrn
        self.possible_ids = set()
        self.caisis_id = None
        self.obscured_id=None

    def set_obscured_id(self, id):
        self.obscured_id = id