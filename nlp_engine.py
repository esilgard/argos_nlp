''' author@esilgard '''
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
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

import sys, os, codecs
import output_results, make_text_output_directory, metadata
from datetime import datetime
import global_strings as gb

'''
initial script of the Argos/NLP engine do deal with command line parsing and module outputs
should exit with a non-zero status for any fatal errors and
output warnings and results in json format to CWD in the file provided in cmd line args
'''

## declare output dictionary for values, warnings, and metadata
OUTPUT_DICTIONARY = {}
OUTPUT_DICTIONARY[gb.ERRS] = []

## path to the nlp_engine.py script ##
NLP_ENGINE_PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
ORIGINAL_WD = os.getcwd()

## timeit variable for performance testing ##
BEGIN = datetime.today()

try:
    ## grab version number from txt file which updates with git post-commit hook script
    ##(assume utf-8, but back up to utf-16)
    __version__ = codecs.open(NLP_ENGINE_PATH + 'version', 'rb', encoding='utf-8')\
                  .readlines()[0].strip()
except UnicodeError:
    try:
        __version__ = codecs.open(NLP_ENGINE_PATH + 'version', 'rb', encoding='utf-16')\
                      .readlines()[0].strip()
    except IOError:
        sys.stderr.write('FATAL ERROR: could not locate or parse version file.')
        sys.exit(1)

## path to file containing command line flags and descriptions ##
## in the format -char<tab>description<tab>verbose_description(for help and error messages) ##
try:
    COMMAND_LINE_FLAG_FILE = open(NLP_ENGINE_PATH + 'command_line_flags.txt', 'r')
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
    except IOError:
        sys.stderr.write('FATAL ERROR: command line flag dictionary could not be established \
                        from file, potential formatting error.  program aborted.')
        sys.exit(1)
except EnvironmentError:
    sys.stderr.write('FATAL ERROR: command line flag file not found.  program aborted.')
    sys.exit(1)

## parse the ARGUMENTS from arg1 on into a dictionary - notify user of unrecognized flags
## NOTE - this does assume that flags start in the first position
## and every other argument is a flag
for index in range(0, len(ARGS)-1, 2):
    if ARGS[index] in COMMAND_LINE_FLAGS:
        ARGUMENTS[ARGS[index]] = ARGS[index+1]
    else:
        OUTPUT_DICTIONARY[gb.ERRS].append({gb.ERR_TYPE: 'Warning', gb.ERR_STR: 'nonfatal error: \
        unrecognized flag: ' + ARGS[index] + ', this flag will not be excluded. Refer to ' + \
        NLP_ENGINE_PATH + 'COMMAND_LINE_FLAGS.txt for a complete list and description of command line flags'})

## build the dictionary for the json output ##
OUTPUT_DICTIONARY[gb.CNTL] = {}
OUTPUT_DICTIONARY[gb.CNTL]["engineVersion"] = __version__
OUTPUT_DICTIONARY[gb.CNTL]["referenceId"] = "12345"
OUTPUT_DICTIONARY[gb.CNTL]["docVersion"] = "document version"
OUTPUT_DICTIONARY[gb.CNTL]["source"] = "document source"
OUTPUT_DICTIONARY[gb.CNTL]["docDate"] = "doc date"
OUTPUT_DICTIONARY[gb.CNTL]["processDate"] = str(datetime.today().isoformat())
metadata = metadata.get(NLP_ENGINE_PATH, ARGUMENTS)
OUTPUT_DICTIONARY[gb.CNTL]["metadata"] = metadata
OUTPUT_DICTIONARY[gb.REPORTS] = []
## add in flag info to the json output dictionary
OUTPUT_DICTIONARY[gb.CNTL]["docName"] = ARGUMENTS.get('-f')
OUTPUT_DICTIONARY[gb.CNTL]["docType"] = ARGUMENTS.get('-t')
OUTPUT_DICTIONARY[gb.CNTL]["diseaseGroup"] = ARGUMENTS.get('-g')

## ERR out for missing flags that are required ##
MISSING_FLAGS = REQUIRED_FLAGS-set(ARGUMENTS.keys())
if len(MISSING_FLAGS) > 0:
    for each_flag in MISSING_FLAGS:
        sys.stderr.write('FATAL ERROR: missing required flag: ' + each_flag + ' ' + COMMAND_LINE_FLAGS[each_flag][1])
    sys.exit(1)
else:

    ## import and call appropriate module ##
    try:
        DOCUMENT_PROCESSER = __import__('fhcrc_'+ARGUMENTS.get('-t'), globals(), locals(), ['process'])
    except ImportError:
        sys.stderr.write('FATAL ERROR: could not import module ' + ARGUMENTS.get('-t'))
        sys.exit(1)
    MKDIR_ERRORS = make_text_output_directory.main(ARGUMENTS.get('-f'))
    if MKDIR_ERRORS[0] == Exception:
        sys.stderr.write(MKDIR_ERRORS[1])
        sys.exit(1)
    OUTPUT, ERRORS, RETURN_TYPE = DOCUMENT_PROCESSER.process.main(ARGUMENTS)

    if RETURN_TYPE == Exception:
        print ERRORS
        sys.stderr.write('\n'.join([err[gb.ERR_STR] for err in ERRORS]))
        sys.exit(1)
    else:
        OUTPUT_DICTIONARY[gb.REPORTS] = OUTPUT
        OUTPUT_DICTIONARY[gb.ERRS] = ERRORS

    if MKDIR_ERRORS[0] == dict:        
        OUTPUT_DICTIONARY[gb.ERRS].append(MKDIR_ERRORS[1])
    ## iterate through errors - CRASH for Exceptions and output Warnings
    if OUTPUT_DICTIONARY[gb.ERRS]:
        CRASH = False
        for error_dictionary in OUTPUT_DICTIONARY[gb.ERRS]:
            if error_dictionary and error_dictionary[gb.ERR_TYPE] == 'Exception':
                CRASH = True
                sys.stderr.write(error_dictionary[gb.ERR_STR])
        if CRASH == True:
            sys.exit(1)
    ## output results to file ##
    OUTPUT_RETURN = output_results.main(ARGUMENTS.get('-o'), OUTPUT_DICTIONARY)
    if OUTPUT_RETURN:
        sys.exit(1)

## timeit - print out the amount of time it took to process all the reports ##
## print (datetime.today()-BEGIN).days * 86400 + (datetime.today()-BEGIN).seconds, \
##'seconds to process '+str(len(OUTPUT_DICTIONARY["reports"]))+' reports'
