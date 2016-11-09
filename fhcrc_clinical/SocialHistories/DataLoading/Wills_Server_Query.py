import pyodbc
import platform

from fhcrc_clinical.SocialHistories.DataLoading.DataLoadingGlobals import TEST_JOB_IDS, TRAIN_JOB_IDS, entity_types
from fhcrc_clinical.SocialHistories.DataModeling.DataModels import DocumentEvent, AnnotatedAttribute, Span


def main():
    '''Runs a standalone test version of the Server Query '''
    cur = __get_server_connection()
    results = __execute_data_pull(cur, "train") # possible values: "train" and "test"
    for r in results:
        print r
    patient_doc_annotations = __organize_data(results)
    return patient_doc_annotations


def get_labkey_test_data():
    '''Returns test data in labkey derived from the set of job_ids defined in the DataLoadingGlobals.py file'''
    cur = __get_server_connection()
    results = __execute_data_pull(cur, "test")
    patient_doc_annotations = __organize_data(results)
    return patient_doc_annotations


def get_labkey_training_data():
    '''Returns training data in labkey derived from the set of job_ids defined in the DataLoadingGlobals.py file'''
    cur = __get_server_connection()
    results = __execute_data_pull(cur, "train")
    patient_doc_annotations = __organize_data(results)
    return patient_doc_annotations


def __get_server_connection():
    config_dict = __parse_odbc_file()
    server = config_dict["server"]
    db = config_dict["database"]
    odbc_driver = config_dict["driver"]
    connStr = (
        'DRIVER={' + odbc_driver + '};\
            SERVER=' + server + ';\
            DATABASE=' + db + ';\
            Trusted_Connection=yes')
    conn = pyodbc.connect(connStr)
    return conn.cursor()


def __execute_data_pull(connection_curser, data_division):
    cur = connection_curser
    job_ids = []
    if data_division == "test":
        job_ids = TEST_JOB_IDS
    elif data_division =="train":
        job_ids = TRAIN_JOB_IDS
    query_string = "SELECT nlp.FieldResult.*, nlp.Report.JobRunId, nlp.Report.MRN,\
        nlp.Report.ReportNo, nlp.Report.Status,\
        nlp.StartStopPosition.StartPosition, nlp.StartStopPosition.StopPosition \
    FROM nlp.FieldResult\
    JOIN nlp.StartStopPosition\
    ON nlp.FieldResult.FieldResultId = nlp.StartStopPosition.FieldResultId\
    JOIN nlp.Report \
    ON nlp.FieldResult.ReportId = nlp.Report.ReportId" + \
                   __AND_nlp_Report_JobRunID_IN(job_ids) +\
                   "AND nlp.Report.Status = 'approved'\
    AND nlp.Report.IterationId = nlp.FieldResult.IterationId \
    AND nlp.FieldResult.TargetTable = 'SocialHistories'"
    cur.execute(query_string)
    columns = [column[0] for column in cur.description]
    results = []
    for row in cur.fetchall():
        results.append(dict(zip(columns, row)))
    return results


def __AND_nlp_Report_JobRunID_IN(list_jobids):
    query_str=" AND nlp.Report.JobRunID IN ("
    for num in list_jobids:
        query_str += str(num) + ", "
    query_str = query_str.rstrip(", ")
    query_str += ") "
    return query_str


def __organize_data(sql_results):
    '''Takes the raw results from the SQL pull, and formats it into dictionaries in the following form:
    {abstractor_Id: {MRN: {doc_id: {"Alcohol"||"Tobacco" : DocumentEventObj}}}'''
    abstractorId_root_dict = dict()
    for row in sql_results:
        if row['CreatedBy'] not in abstractorId_root_dict:
            abstractorId_root_dict[row['CreatedBy']]=dict()
        if row['MRN'] not in abstractorId_root_dict[row['CreatedBy']]:
            abstractorId_root_dict[row['CreatedBy']][row['MRN']] = dict()
        if row['ReportNo'] not in abstractorId_root_dict[row['CreatedBy']][row['MRN']]:
            abstractorId_root_dict[row['CreatedBy']][row['MRN']][row['ReportNo']] = dict()
        if "Alcohol" in row['Field']:
            if "Alcohol" not in abstractorId_root_dict[row['CreatedBy']][row['MRN']][row['ReportNo']]:
                abstractorId_root_dict[row['CreatedBy']][row['MRN']][row['ReportNo']]["Alcohol"]=list()
            abstractorId_root_dict[row['CreatedBy']][row['MRN']][row['ReportNo']]["Alcohol"].append(__create_doc_event_obj(row, "Alcohol"))
        if "Tobacco" in row['Field']:
            if "Tobacco" not in abstractorId_root_dict[row['CreatedBy']][row['MRN']][row['ReportNo']]:
                abstractorId_root_dict[row['CreatedBy']][row['MRN']][row['ReportNo']]["Tobacco"] = list()
            abstractorId_root_dict[row['CreatedBy']][row['MRN']][row['ReportNo']]["Tobacco"].append(__create_doc_event_obj(row, "Tobacco"))

    for aid, mrn_dict in abstractorId_root_dict.iteritems():
        for mrn, docid_dict in mrn_dict.iteritems():
            for docid, subs_dict in docid_dict.iteritems():
                for subs, list_of_attribs in subs_dict.iteritems():
                    # condense list of objects to a single obj with attribs and spans
                    event = __unify_attribs_into_event(DocumentEvent(subs), [x.status_spans[0] for x in list_of_attribs])
                    # set condensed event in substance dictionary
                    subs_dict[subs] = event
    return abstractorId_root_dict


def __create_doc_event_obj(row, substance):
    event = DocumentEvent(substance)
    event.status_spans.append((row['Field'], row['Value'], row['StartPosition'], row['StopPosition']))
    return event


def __unify_attribs_into_event(event, attrib_list):
    for attrib in attrib_list:
        if "Status" in attrib[0]:
            event.status = attrib[1]
            event.status_spans.append(Span(attrib[2], attrib[3]))
        else:
            for t in entity_types:
                if t in attrib[0]:
                    attrib_type = t
                    attrib_text = attrib[1]
                    attrib_span_begin = attrib[2]
                    attrib_span_end = attrib[3]

                    if attrib_type not in event.attributes:
                        aa = AnnotatedAttribute(attrib_type, [Span(attrib_span_begin, attrib_span_end)], attrib_text)
                        event.attributes[attrib_type]=aa
                    else:
                        event.attributes[attrib_type].all_value_spans.append(Span(attrib_span_begin, attrib_span_end))
    return event


def __parse_odbc_file():
    if platform.system() == 'Linux':
        path = "/etc/nlp-abstraction-pipeline/config/odbc_settings"
    if platform.system() == "Windows":
        path = "%USERPROFILE%\AppData\Local\\nlp-abstraction-pipeline\\config\\odbc_settings"
    with open(path, "rb") as f:
        lines = f.readlines()

    config_dict = dict()
    for line in lines:
        line = line.rstrip()
        if line != "":
            splits = line.split("=")
            config_dict[splits[0].lower()] = splits[1]
    return config_dict


def get_document_text(document_metadata):
    doc_ids = __get_document_ids(document_metadata)
    docid_text_dict = __execute_docid_text_dict_query(doc_ids)
    return docid_text_dict


def __get_document_ids(document_metadata):
    doc_ids = set()
    for annotator, patients in document_metadata.iteritems():
        for patient, documents in patients.iteritems():
            for docu_id in documents:
                doc_ids.add(docu_id)
    return doc_ids


def __execute_docid_text_dict_query(doc_ids):
    query = "SELECT nlp.Report.ReportNo,nlp.Report.ReportText FROM nlp.Report" + \
            __WHERE_nlp_report_ReportNo_IN(doc_ids)
    cur = __get_server_connection()
    cur.execute(query)
    columns = [column[0] for column in cur.description]
    results = {}
    for row in cur.fetchall():
        results[row[0]] = row[1]
    return results


def __WHERE_nlp_report_ReportNo_IN(doc_ids):
    line = " WHERE nlp.Report.ReportNo IN ("
    for id in doc_ids:
        line += "\'"+str(id) + "\', "

    line = line.rstrip(", ")
    line += ")"
    return line

if __name__ == "__main__":
    main()
