# -*- coding: utf-8 -*-
"""
Created on Mon Aug 08 14:00:30 2016

@author: esilgard
"""
import os
## link Florian's sentence level annotations to document ids with char offsets

labels = {'S':'user','N':'non','P':'past','C':'current','U':'unknown'}

gold_sentences_directory = 'path_to_the_directory_that_holds_florians_gold_sentence_annotations'  # these were called  things like "tob" and "smoke" based on keyword hits
clinic_note_files_directory = 'path_to_the_directory_that_holds_the_note_files'   # this assumes that the file name is the identifier for the note and that there is only one '.' file extension
output_json_annotations = 'path_to_output_json_annotations'   # the json output format might not be a perfect fit for what you need, but that's an pretty simple fix


sentences_d = {}

for path,directory,files in os.walk(gold_sentences_directory):
    for f in files:
        for lines in open(path +  f,'r').readlines():     
            status = labels[lines[0].upper()]           
            sentence = lines[2:].strip()
            if sentence in sentences_d and sentences_d[sentence] != status:
                print 'label mismatch:',sentences_d[sentence],'   VS   ',status,'    WITH:',sentence
            else:
                sentences_d[sentence] = status
            sentences_d[sentence]=status
print len(sentences_d)  ,'annotated sentences'


# output annotations_d will be a dictionary of unique document identifiers that map
# a list of annotations (text span) dictionaries
# each dictionary will have charoffsets (start and stop position in the document
# and a TobaccoStatus (closed class of labels) 
annotations_d = {}   
import re
for path, directory, files in os.walk('H:/Internships/Florian/smoking_status/SmokingStatusAnnotator/resources/gold/sentences/'):
    for f in files:
        text = open(path + f,'r').read()
        ## this doc id is assuming that there is only one file extension in the file name
        document_id = f.split('.')[0]
        annotations_d[document_id] = []
        for sentence in sentences_d:
            regex_sentence = sentence.replace('+','[+]').replace('(','[(]').replace(')','[)]')
            m = re.match(r'.*(' + regex_sentence + ').*', text)
            if m:
                annotations_d[document_id].append({'TobaccoStatus':sentences_d[sentence],
                                      'StartPosition':m.start(1),
                                      'StopPosition':m.end(1)})

import json
with open(output_json_annotations,'w') as out:
    json.dump(annotations_d, out)          
            
            

           
            
            