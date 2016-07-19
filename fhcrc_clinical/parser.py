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


def process_text_lines(note_text, mrn, acc, chars_onset, clinical_d, section, section_order):
    for text_line in note_text:  # process line by line exactly as is done in the original parser
        ## for now...make sure line endings are are all simply a single new line char
        ## (replaced later)
        text_line = re.sub(r'[\r\n]', '', text_line)
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
        clinical_d[mrn][acc][(section_order, section, chars_onset)] = \
            clinical_d[mrn][acc].get((section_order, section, chars_onset), {})
        clinical_d[mrn][acc][(section_order, section, chars_onset)] = text_line
        clinical_d[mrn][acc][(-1, 'FullText', 0)] = \
            clinical_d[mrn][acc].get((-1, 'FullText', 0), '') + text_line + '\n'
        chars_onset += len(text_line) + 1
    return clinical_d


def csv_parse(input_file_path, clinical_d, section, section_order):
    try:
        with open(input_file_path, "rb") as csv_file:
            note_reader = csv.reader(csv_file)
            for row in note_reader:  # each row is a document and its metadata
                # print ', '.join(row)
                note_text = row[3].split("\n")
                mrn = row[0]
                acc = row[1]
                date = row[2]
                chars_onset = 0
                clinical_d[mrn] = clinical_d.get(mrn, {})
                clinical_d[mrn][acc] = {}

                clinical_d = process_text_lines(note_text, mrn, acc, chars_onset, clinical_d, section,
                                                section_order)
            return clinical_d, dict
    except RuntimeError:
        return ({gb.ERR_TYPE: 'Exception', gb.ERR_STR: "FATAL ERROR: " + \
                                                       str(sys.exc_info()[0]) + "," + str(sys.exc_info()[1]) + \
                                                       " trouble finding input file path or parsing file " + str(
            input_file_path) + " -- program aborted"}, Exception)
    pass


def directory_parse(input_file_path, clinical_d, section, section_order):
    # Regular input directory parsing
    try:
        for filename in os.listdir(input_file_path):
            note_text = open(input_file_path + os.path.sep + filename, 'rU').readlines()
            ## currently getting identifiers from file name
            mrn = filename.split('_')[0]
            acc = filename.split('.')[0]
            chars_onset = 0
            clinical_d[mrn] = clinical_d.get(mrn, {})
            clinical_d[mrn][acc] = {}

            clinical_d = process_text_lines(note_text, mrn, acc, chars_onset, clinical_d, section,
                                            section_order)
        return clinical_d, dict

    ## if this is actually a problem parsing a specific file in the input directory,
    ## it won't currently return that info
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
    clinical_d = {}
    section = 'NULL'
    section_order = 0

    # If the input is a .csv, the parsing is different
    if ".csv" in input_file_path:
        return csv_parse(input_file_path, clinical_d, section, section_order)

    # If the input file is not a csv, go home. Support for directory processing N/A
    else:
        raise IOError("Error: Input file not a .csv")
        #return directory_parse(input_file_path, clinical_d, section, section_order)
