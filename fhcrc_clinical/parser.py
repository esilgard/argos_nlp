''' author @ esilgard '''
#
# Copyright (c) 2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__version__ = 'clinical_parser1.0'
import re, sys, os, csv
import global_strings as gb


def process_text_lines(note_d, note_text):
    
    section = 'NULL'
    section_order = 0
    chars_onset = 0
    for text_line in re.split('[\r\n]',note_text):  # process line by line exactly as is done in the original parser
    
        # match general section header patterns
        ## TODO - this pattern was made for pathology reports
        ## we'll have to come up with something a little more sophisticated for clinic notes
        ## also probably need to deal with sentence splitting here
        section_header = re.match(r'^[\*\"\<\( ]*([A-Z \/\\\-\(\)&]{4,100})[\*:#\>\)]+$', text_line)

        # reassign the section variable if you find a section pattern match
        # reset specimen and increment section order
        if section_header:
            section = section_header.group(1).strip()
            section_order += 1
        note_d[(section_order, section, chars_onset)] = \
            note_d.get((section_order, section, chars_onset), {})
        note_d[(section_order, section, chars_onset)] = text_line
        note_d[(-1, 'FullText', 0)] = \
            note_d.get((-1, 'FullText', 0), '') + text_line + '\n'
        chars_onset += len(text_line) + 1
    return note_d


def csv_parse(input_file_path):
    clinical_d = {}
    required_header_set = set([gb.EVENT_DATE, gb.OBSERVATION_VALUE, gb.FILLER_ORDER_NO, gb.MRN_CAPS])
    headers = {}
    try:
        line_number = 0
        with open(input_file_path, "rb") as csv_file:
            note_reader = csv.reader(csv_file) 
            for row in note_reader:  # each row is a document and its metadata
                if line_number == 0:
                    headers = dict((k, v) for v, k in enumerate(row))
                    if not set(headers.keys()).issuperset(required_header_set):                        
                        return ({gb.ERR_TYPE: 'Exception', gb.ERR_STR: "FATAL ERROR: " + \
                        str(sys.exc_info()[0]) + "," + str(sys.exc_info()[1]) + \
                        "Missing required header set in initial line of input file"}, Exception)                    
                else:
                    note_text = row[headers.get(gb.OBSERVATION_VALUE)]
                    mrn = row[headers.get(gb.MRN_CAPS)]
                    acc = row[headers.get(gb.FILLER_ORDER_NO)]
                    date = row[headers.get(gb.EVENT_DATE)]              

                    clinical_d[mrn] = clinical_d.get(mrn, {})
                    clinical_d[mrn][acc] = {}
                    #clinical_d[mrn][acc][(-1, 'FullText', 0)] = note_text
                    clinical_d[mrn][acc][(-2, gb.EVENT_DATE, 0)] = date   
                    clinical_d[mrn][acc] = process_text_lines(clinical_d[mrn][acc], note_text)
                line_number += 1
            return clinical_d, dict

    except RuntimeError:
        return ({gb.ERR_TYPE: 'Exception', gb.ERR_STR: "FATAL ERROR: " + \
                str(sys.exc_info()[0]) + "," + str(sys.exc_info()[1]) + \
                " trouble finding input file path or parsing file " + str(
            input_file_path) + " -- program aborted"}, Exception)
    pass

def parse(input_file_path):
    '''
    starter for a basic parser and sectioner/sentence splitter for  Amalga clinic notes
    input = "input_file_path" = directory housing txt files (notes)
    output = "clinical_d" = a dictionary of {unique mrns:{unique acc_nums:
	** lots of TBD here - may want to organize by sentences as well as sections 
	** will require some splitting/sectioning work
        {(section order?, section heading?, character onset of section?):{texts}}}}
    --returns a tuple of output, return_type
    '''
    
    # If the input is a .csv, the parsing is different
    #if ".csv" in input_file_path:
    return csv_parse(input_file_path)

    # If the input file is not a csv, go home. Support for directory processing N/A
    #else:
    #    raise IOError("Error: Input file not a .csv")

