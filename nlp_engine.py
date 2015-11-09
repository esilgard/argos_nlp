''' author@esilgard '''
#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
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


'''
initial script of the Argos/NLP engine do deal with command line parsing and module outputs
should exit with a non-zero status for any fatal errors and
output warnings and results in json format to CWD in the file provided in cmd line ARGUMENTS
'''

import sys, os, codecs
import output_results, make_text_output_directory, metadata
from datetime import datetime

## declare output dictionary for values, warnings, and metadata
OUTPUT_DICTIONARY = {}

## path to the nlp_engine.py script ##
NLP_ENGINE_PATH = os.path.dirname(os.path.realpath(__file__))+'/'
ORIGINAL_WD = os.getcwd()

## timeit variable for performance testing ##
BEGIN = datetime.today()

## grab version number from txt file which updates with git post-commit hook script
##(assume utf-8, but back up to utf-16)
try:
    __version__ = codecs.open(NLP_ENGINE_PATH + 'version', 'rb', encoding='utf-8')\
                  .readlines()[0].strip()
except Exception:
    try:
        __version__ = codecs.open(NLP_ENGINE_PATH + 'version', 'rb', encoding='utf-16')\
                      .readlines()[0].strip()
    except Exception:
        sys.stderr.write('FATAL ERROR: could not locate or parse version file.')
        sys.exit(1)

## path to file containing command line flags and descriptions ##
## in the format -char<tab>description<tab>verbose_description(for help and error messages) ##
try:
    COMMAND_LINE_FLAG_FILE = open(NLP_ENGINE_PATH + 'COMMAND_LINE_FLAGS.txt', 'r')
    try:
        ## set of required flags for program to run successfully ##
        REQUIRED_FLAGS = set([])
        ## dictionary of actual flags:argument values ##
        ARGUMENTS = {}
        ## dictionary of flag:tuple(flag description,verbose flag description) ##
        COMMAND_LINE_FLAGS = {}
        for line in COMMAND_LINE_FLAG_FILE.readlines():
            line = line.strip().split('\t')
            if line[1] == 'required':
                REQUIRED_FLAGS.add(line[0])
            COMMAND_LINE_FLAGS[line[0]] = (line[2], line[3])
        COMMAND_LINE_FLAG_FILE.close()
        ARGS = sys.argv[1:]
    except Exception:
        sys.stderr.write('FATAL ERROR: command line flag dictionary could not be established \
                        from file, potential formatting error.  program aborted.')
        sys.exit(1)
except Exception:
    sys.stderr.write('FATAL ERROR: command line flag file not found.  program aborted.')
    sys.exit(1)


## parse the ARGUMENTS from arg1 on into a dictionary - notify user of unrecognized flags
## NOTE - this does assume that flags start in the first position
## and every other argument is a flag
for index in range(0, len(ARGS)-1, 2):
    if ARGS[index] in COMMAND_LINE_FLAGS:
        ARGUMENTS[ARGS[index]] = ARGS[index+1]
    else:
        OUTPUT_DICTIONARY["errors"].append({'errorType': 'Warning', \
        'errorString': 'nonfatal error:  unrecognized flag: ' + ARGS[index] + \
        ' this flag will be excluded from the ARGUMENTS refer to ' + \
        COMMAND_LINE_FLAG_FILE + ' for a complete list and description of command line flags'})


############################################################################################
def return_exec_code(string_to_execute):
    '''
        helper method to retrieve the returned field value from each module
    '''
    return string_to_execute

############################################################################
## build the dictionary for the json output ##

OUTPUT_DICTIONARY["controlInfo"] = {}
OUTPUT_DICTIONARY["controlInfo"]["engineVersion"] = __version__
OUTPUT_DICTIONARY["controlInfo"]["referenceId"] = "12345"
OUTPUT_DICTIONARY["controlInfo"]["docVersion"] = "document version"
OUTPUT_DICTIONARY["controlInfo"]["source"] = "document source"
OUTPUT_DICTIONARY["controlInfo"]["docDate"] = "doc date"
OUTPUT_DICTIONARY["controlInfo"]["processDate"] = str(datetime.today().isoformat())
OUTPUT_DICTIONARY["controlInfo"]["metadata"] = metadata.get(NLP_ENGINE_PATH, ARGUMENTS)
OUTPUT_DICTIONARY["errors"] = []
OUTPUT_DICTIONARY["reports"] = []

## add in flag info to the json output dictionary
OUTPUT_DICTIONARY["controlInfo"]["docName"] = ARGUMENTS.get('-f')
OUTPUT_DICTIONARY["controlInfo"]["docType"] = ARGUMENTS.get('-t')
OUTPUT_DICTIONARY["controlInfo"]["diseaseGroup"] = ARGUMENTS.get('-g')

## ERR out for missing flags that are required ##
MISSING_FLAGS = REQUIRED_FLAGS-set(ARGUMENTS.keys())
if len(MISSING_FLAGS) > 0:
    for each_flag in MISSING_FLAGS:
        sys.stderr.write('FATAL ERROR: missing required flag: ' + each_flag + ' ' + \
        COMMAND_LINE_FLAGS[each_flag][1])
    sys.exit(1)
else:

    ## import and call appropriate module ##
    try:
        exec 'from fhcrc_' + ARGUMENTS.get('-t') + ' import process_' + ARGUMENTS.get('-t')
    except Exception:
        sys.stderr.write('FATAL ERROR:  could not import module process_' + \
        ARGUMENTS.get('-t'))
        sys.exit(1)
    MKDIR_ERRORS = make_text_output_directory.main(ARGUMENTS.get('-f'))
    if MKDIR_ERRORS[0] == Exception:
        sys.stderr.write(MKDIR_ERRORS[1])
        sys.exit(1)
    exec ('output, errors, return_type = return_exec_code(process_' + ARGUMENTS.get('-t') + \
          '.main(ARGUMENTS, NLP_ENGINE_PATH ))')

    if return_type == Exception:
        sys.stderr.write(errors['errorString'])
        sys.exit(1)
    else:
        OUTPUT_DICTIONARY["reports"] = output
        OUTPUT_DICTIONARY["errors"] = errors

    if MKDIR_ERRORS[0] == dict:
        OUTPUT_DICTIONARY["errors"].append(MKDIR_ERRORS[1])

    ## iterate through errors - CRASH for Exceptions and output Warnings
    if OUTPUT_DICTIONARY["errors"]:
        CRASH = False
        for error_dictionary in OUTPUT_DICTIONARY["errors"]:
            if error_dictionary and error_dictionary['errorType'] == 'Exception':
                CRASH = True
                sys.stderr.write(error_dictionary['errorString'])
        if CRASH == True:
            sys.exit(1)
    ## output results to file ##
    OUTPUT_RETURN = output_results.main(ARGUMENTS.get('-o'), OUTPUT_DICTIONARY)
    if OUTPUT_RETURN:
        sys.exit(1)

## timeit - print out the amount of time it took to process all the reports ##
## print (datetime.today()-BEGIN).days * 86400 + (datetime.today()-BEGIN).seconds, \
##'seconds to process '+str(len(OUTPUT_DICTIONARY["reports"]))+' reports'
