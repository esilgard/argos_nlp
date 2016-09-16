class CSVBatch:
    def __init__(self, id):
        self.id =id
        self.documents = list()

    def add_document(self, doc):
        self.documents.append(doc)