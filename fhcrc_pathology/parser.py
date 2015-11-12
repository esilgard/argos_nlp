''' author @ esilgard '''
#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
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

__version__ = 'parser1.0'
import re, sys
import global_strings as gb

## header names exptected to be coming from the Amalga Import ##
REQUIRED_HEADER_SET = set([gb.SET_ID, gb.OBSERVATION_VALUE, gb.FILLER_ORDER_NO, gb.MRN_CAPS])

def parse(obx_file):
    '''
    this is a basic parser and sectioner for  Amalga pathology reports
    input = "obx_file" = a tab delimited text version of an Amalga obx table
    output = "path_d" = a dictionary of {unique mrns:{unique acc_nums:
        {(section order, section heading, character onset of section):{row num/index:texts}}}}
    **to work correctly first line must contain the expected headers**
    --returns a tuple of output, return_type
    '''

    path_d = {}
    section = 'NULL'
    section_order = 0
    specimen = None
    try:
        obx = open(obx_file, 'rU').readlines()
        obx = [re.sub(r'[\r\n]', '', a).split('\t') for a in obx]
        header_set = set(obx[0])
        if set(header_set) >= REQUIRED_HEADER_SET:
            headers = dict((k, v) for v, k in enumerate(obx[0]))
            try:
                # sort by mrn, acc, and then setid, ignore null mrns,acc nums,setids
                obx = sorted([y for y in obx[1:] if (y[headers.get(gb.MRN_CAPS)] != 'NULL' \
                            and y[headers.get(gb.FILLER_ORDER_NO)] != 'NULL' and \
                            y[headers.get(gb.SET_ID)] != 'NULL')], key=lambda x: \
                            (x[headers.get(gb.MRN_CAPS)], x[headers.get(gb.FILLER_ORDER_NO)], \
                             int(x[headers.get(gb.SET_ID)])))

                chars_onset = 0
                for line in obx:
                    mrn = line[headers.get(gb.MRN_CAPS)]
                    acc = line[headers.get(gb.FILLER_ORDER_NO)]
                    index = line[headers.get(gb.SET_ID)]
                    if index == '1':
                        section_order = 0
                        chars_onset = 0
                    text = line[headers.get(gb.OBSERVATION_VALUE)]

                    if gb.FILLER_ORDER_NO in line:
                        pass  # ignore duplicate header lines
                    elif  text == 'NULL':
                        # maintain readability of text by keeping 'NULL' lines
                        path_d[mrn] = path_d.get(mrn, {})
                        path_d[mrn][acc] = path_d[mrn].get(acc, {})
                        path_d[mrn][acc][(-1, 'FullText', 0, None)] = path_d[mrn][acc].get\
                            ((-1, 'FullText', 0 , None), '') +'\n'
                        # maintain readability of fully constituted text by keeping 'NULL' lines
                        chars_onset += 1
                    else:
                        ## grab acc dictionary
                        path_d[mrn] = path_d.get(mrn, {})
                        path_d[mrn][acc] = path_d[mrn].get(acc, {})
                        if index == '1':
                            chars_onset = 0
                            # create a specimen source dictionary for each labeled specimen
                            # (in the same format as the regular pathology section dictionary
                            ## catch NULL or empty string specimenSources
                            if not headers.get(gb.SPECIMEN_SOURCE) or \
                               line[headers.get(gb.SPECIMEN_SOURCE)] == 'NULL':
                                specimen_dictionary = {}
                            else:
                                specimen_dictionary = dict((x.split(')')[0], x.split(')')[1].\
                                                    replace('(', ' ')) for x in  line[headers.get\
                                                    (gb.SPECIMEN_SOURCE)].strip('"').split('~'))
                            path_d[mrn][acc][(0, gb.SPECIMEN_SOURCE, 0, None)] = {}
                            path_d[mrn][acc][(0, gb.SPECIMEN_SOURCE, 0, None)][0] = specimen_dictionary
                        # match general section header patterns
                        section_header = re.match(r'^[\*\"\<\( ]*([A-Z \\\-\(\)]{4,})[\*:#\>\) ]*$', text)

                        # reassign the section variable if you find a section pattern match
                        # reset specimen and increment section order
                        if section_header:
                            section = section_header.group(1).strip()
                            section_order += 1
                            specimen = ''
                        specimen_header = re.match(r'[\s\"]{,4}([,A-Z\- and&]+?)[\s]*(FS)?((-[A-Z])[\s]*FS)?[\s]*[)].*', text)
                        if specimen_header:
                            specimen = '' ## reset specimen if there is a new specimen header match
                            specimen_match = specimen_header.group(1).replace(' ', '')
                            ## catch specimens listed in interop consults eg 'AFS-EFS: negative..'
                            if specimen_header.group(4) and '-' in specimen_header.group(4):
                                specimen_match = specimen_match + specimen_header.group(4)
                            for each in  specimen_dictionary.keys():
                                if each and re.search('[' + specimen_match + ']', each):
                                    specimen += each

                        path_d[mrn][acc][(section_order, section, chars_onset, specimen)] = \
                            path_d[mrn][acc].get((section_order, section, chars_onset, specimen), {})
                        path_d[mrn][acc][(section_order, section, chars_onset, specimen)][index] = text
                        path_d[mrn][acc][(-1, 'FullText', 0, None)] = \
                            path_d[mrn][acc].get((-1, 'FullText', 0, None), '') \
                            + text + '\n'
                        chars_onset += len(text) + 1

                return path_d, dict
            except RuntimeError:
                return ({gb.ERR_TYPE: 'Exception', gb.ERR_STR: "FATAL ERROR: " + \
                         str(sys.exc_info()[0]) + "," + str(sys.exc_info()[1]) + \
                         " trouble parsing " + str(obx_file) + " -- program aborted"}, Exception)
        else:
            return ({gb.ERR_TYPE: 'Exception', gb.ERR_STR: "FATAL ERROR: " + str(sys.exc_info()[0]) \
                     + "," + str(sys.exc_info()[1]) + " required headers not found in inital \
                    line of " + str(obx_file) + " -- must include " + ','.join\
                    (REQUIRED_HEADER_SET - header_set) + " -- program aborted"}, Exception)
    except EnvironmentError:
        return ({gb.ERR_TYPE: 'Exception', gb.ERR_STR: "FATAL ERROR: " + str(sys.exc_info()[0]) + \
                 "," + str(sys.exc_info()[1]) + " -- could not find input file " + str(obx_file) + \
                 " -- program aborted"}, Exception)
