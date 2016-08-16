from fhcrc_clinical.global_strings import *
from fhcrc_clinical.SocialHistories.DataLoading.DataLoadingGlobals import *


class SubstanceField:
    __version__ = 'SubstanceInfo1.0'

    def __init__(self):
        self.field_name = 'Default'
        self.return_d = {}
        self.value = 'Default'
        self.table = SOC_HISTORIES
        self.substance = ''
        self.field = ''

    def get_version(self):
        """ return algorithm version"""
        return self.__version__

    def get(self, dictionary, field, mrn, accession, patients, mrn_caisis_map):
        """ fill field with value from extraction results """
        try:
            self.get_field_contents(dictionary, field, mrn, accession, patients, mrn_caisis_map)
            return [self.return_d], list
        except RuntimeError:
            return [{ERR_TYPE: 'Warning', ERR_STR: 'ERROR in %s module.' % self.field_name}], Exception

    def get_field_contents(self, dictionary, field, mrn, accession, patients, mrn_caisis_map):
        self.return_d = {NAME: self.field_name, VALUE: None, CONFIDENCE: ('%.2f' % 0.0),
                         KEY: ALL, VERSION: self.get_version(),
                         STARTSTOPS: [], TABLE: self.table}

        # Get the appropriate attribute
        doc, document_found = get_document(patients, mrn, accession, mrn_caisis_map)

        if document_found:
            self.add_doc_field_contents_to_dict(doc)

    def add_doc_field_contents_to_dict(self, doc):
        """@type doc: Document"""
        for event in doc.predicted_events:
            if event.substance_type == self.substance:
                if self.field in event.attributes:
                    self.fill_attribute(event)

                elif self.field == STATUS:
                    self.fill_status(event)

    def fill_attribute(self, event):
        attribute_obj = event.attributes[self.field]  # DocumentAttribute

        # Field value
        self.return_d[VALUE] = attribute_obj.text

        # Field spans
        for span in attribute_obj.all_value_spans:
            self.return_d[STARTSTOPS].append({START: span.start, STOP: span.end})

    def fill_status(self, event):
        # Field value
        self.return_d[VALUE] = event.status

        # Field spans
        for span in event.status_spans:
            self.return_d[STARTSTOPS].append({START: span.start, STOP: span.end})


def get_document(patients, mrn, accession, mrn_caisis_map):
    document = None
    found = False

    caisis_id = mrn_caisis_map[mrn]

    for patient in patients:
        if patient.id == caisis_id:
            for doc in patient.doc_list:
                if doc.id == accession:
                    document = doc
                    found = True
                    break
            break

    return document, found
