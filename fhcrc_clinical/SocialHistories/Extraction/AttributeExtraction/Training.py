import subprocess
import re
import os
import platform
from SentenceTokenizer import strip_sec_headers_tokenized_text
from fhcrc_clinical.SocialHistories.SystemUtilities.Configuration import STANFORD_NER_PATH, ATTRIB_EXTRACTION_DIR_HOME, STANFORD_NER_LIB_ALL
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import entity_types, attrib_extraction_features


def train(patients, model_path=ATTRIB_EXTRACTION_DIR_HOME, script_path=os.path.join("Extraction","AttributeExtraction", ""),
          stanford_ner_path=STANFORD_NER_PATH,
          train_script_name="train_model.sh"):

    # Check OS: bat is windows, sh is unix
    if platform.system() == "Windows":
        train_script_name = "train_model.bat"

    training_doc_objs = get_documents_from_patients(patients)

    for type in entity_types:
        train_file_name = model_path + r"Train-Files/" + "train-" + type + ".tsv"
        prop_file_name = model_path + r"Prop-Files/" + type + ".prop"
        model_name = model_path + r"Models/" + "model-" + type + ".ser.gz"
        create_train_file(training_doc_objs, train_file_name, type)
        create_prop_file(prop_file_name, train_file_name, attrib_extraction_features, model_name)


        train_model(stanford_ner_path, prop_file_name, script_path+train_script_name)


def create_train_file(training_sent_objs, train_file_name, type):
    """
    Sorry about the crazy embedded FOR loops and indents.
    I will modularize better to make it prettier. - Martin
    """
    ## DEBUG write training sentence data to file (for use with crf suite development)
    with open(train_file_name+".CRFSUITE", "w") as f:
        for sent in training_sent_objs:
            f.write(sent.text)

    train_file = open(train_file_name, 'w')
    for sent_obj in training_sent_objs:
        if len(sent_obj.gold_events) > 0: # if the sentence is predicted to have an event
            sentence = sent_obj.text
            gold_event_set = sent_obj.gold_events
            sent_offset = sent_obj.span_in_doc_start

            for match in re.finditer("\S+", sentence):
                start = match.start()
                end = match.end()
                pointer = sent_offset + start
                word = match.group(0).rstrip(",.:;)").lstrip("(").replace("/", "+=+")  #in training and test we have to make this substitution becase Stanford strips the "/"


                if word not in {"SOCIAL", "HISTORY", "SUBSTANCE",
                                    "ABUSE"}:  # see tokenizer in utils, they must both match
                    train_file.write(word)
                    # Debug line
                    # train_file.write("[" + str(pointer) + "," + str(sent_offset + match.end()) + "]")
                    train_file.write("\t")
                    answer = "0"
                    debug_str = ""
                    for entity in gold_event_set:
                        if answer != "0":
                            break
                        attr_dict = entity.attributes
                        for attr in attr_dict:
                            for span in attr_dict[attr].all_value_spans:
                                attr_start = int(span.start)
                                attr_end = int(span.stop)
                                if attr_dict[attr].type == type and \
                                                        attr_start <= pointer < attr_end:
                                    answer = type
                                    # Debug lines
                                    # answer += "\t" + attr_dict[attr].text +\
                                    #          "[" + str(attr_start) +\
                                    #          "," + str(attr_end) + "]"
                                    debug_str = "--- Sent obj start index: " + str(sent_offset) + "\n" + \
                                                "--- Match obj start index: " + str(start) + "\n" + \
                                                "--- Match obj end index: " + str(end) + "\n" + \
                                                "--- Pointer index: " + str(sent_offset) + " + " + \
                                                str(start) + " = " + str(pointer) + "\n" + \
                                                "--- Attr start index: " + str(attr_start) + "\n" + \
                                                "--- Attr end index: " + str(attr_end) + "\n"
                                    break
                    train_file.write(answer + "\n")
                    # Debug line
                    # train_file.write(debug_str)
                    # print(debug_str)
    train_file.close()


def create_prop_file(prop_file_name, train_file_name, features, model_name):
    prop_file = open(prop_file_name, 'w')
    prop_file.write("trainFile = " + train_file_name + "\n")
    prop_file.write("serializeTo = " + model_name + "\n")
    # prop_file.write("map = word=0,answer=1,temp=2,method=3,type=4,amount=5,freq=6,hist=7\n")
    prop_file.write("map = word=0,answer=1\n")
    for feat in features:
        prop_file.write(feat + "\n")
    prop_file.close()


def train_model(stanford_ner_path, prop_file_name, train_script_name):
    print "Attrib Extraction param values:\n\t$1: " + stanford_ner_path + "\n\t$2: " + prop_file_name + "\n\t$3: " + STANFORD_NER_LIB_ALL
    if platform.system() == "Windows":
        subprocess.call([train_script_name, stanford_ner_path, prop_file_name, STANFORD_NER_LIB_ALL], shell=True)
    else:
        subprocess.call(["./"+train_script_name+" "+stanford_ner_path+" "+prop_file_name + " " + STANFORD_NER_LIB_ALL], shell=True)

def get_documents_from_patients(patients):
    sentences = list()
    for patient in patients:
        for document in patient.doc_list:
            for sent_obj in document.sent_list:
                if (len(sent_obj.gold_events)) > 0:  # if the sentence has an event
                    sentences.append(sent_obj)
    return sentences