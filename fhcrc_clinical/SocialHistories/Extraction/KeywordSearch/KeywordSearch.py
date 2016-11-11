import re, os

from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import Span


class KeywordHitJSON:
    def __init__(self, substance):
        self.alg_version = ""
        self.initialize_version(substance)

        self.name = substance + KEYWORD_HIT_NAME
        self.confidence = 0
        self.spans = []
        self.table = KEYWORD_HIT_TABLE
        self.value = NEGATIVE

    def initialize_version(self, substance):
        if substance == TOBACCO:
            self.alg_version = TOB_KEYWORD_VERSION
        elif substance == ALCOHOL:
            self.alg_version = ALC_KEYWORD_VERSION


class KeywordHit:
    def __init__(self, text, span_start, span_end):
        self.text = text
        self.span_start = span_start
        self.span_end = span_end

def search_keywords_in_sentence(text):
    for substance in KEYWORD_SUBSTANCES:
        regex = get_regex_from_file(substance)
        has_hit = find_keyword_hits_sentence(text, regex, substance)
        if has_hit:
            return True
    return False

def search_keywords(patients):
    docs_with_hits = set()
    for substance in KEYWORD_SUBSTANCES:
        regex = get_regex_from_file(substance)
        docs_with_substance = find_keyword_hits(patients, regex, substance)

        for doc in docs_with_substance:
            docs_with_hits.add(doc)

    return docs_with_hits


def get_regex_from_file(substance):
    filename = os.path.dirname(__file__) + os.sep + substance + KEYWORD_FILE_SUFFIX
    with open(filename, "r") as regex_file:
        regex_lines = regex_file.readlines()
        regexes = [r[:-1] for r in regex_lines]     # remove "\n" at end of each regex line

    # OR regexes together to get one big regex
    regex = r"((" + ")|(".join(regexes) + "))"
    return regex


def find_keyword_hits_sentence(text, regex, substance):
    matches = re.findall(regex, text, re.IGNORECASE) #finditer
    if len(matches) > 0:
        return True
    else:
        return False

def find_keyword_hits(patients, regex, substance):
    docs_with_hits = []

    for patient in patients:
        for doc in patient.doc_list:
            keywordhit_json = KeywordHitJSON(substance)

            doc_hits = find_doc_hits(doc, regex, keywordhit_json)
            doc.keyword_hits[substance].extend(doc_hits)
            doc.keyword_hits_json[substance] = keywordhit_json
            if doc_hits:
                docs_with_hits.append(doc)

    return docs_with_hits


def find_doc_hits(doc, regex, keywordhit_json=None):
    matches = re.finditer(regex, doc.text, re.IGNORECASE)
    hits = []
    for match in matches:
        keyword_text = match.group()
        span = match.span()
        span_start = span[0]
        span_end = span[1]

        hit = KeywordHit(keyword_text, span_start, span_end)
        hits.append(hit)

        if keywordhit_json:
            add_json_hit(keywordhit_json, span_start, span_end)

    return hits


def add_json_hit(keywordhit_json, span_start, span_end):
    span = Span(span_start, span_end)
    keywordhit_json.spans.append(span)
    keywordhit_json.value = POSITIVE
