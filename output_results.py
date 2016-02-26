'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

__version__ = 'output_results1.0'
import json, sys

def main(output_file_name, output):
    '''
    output warnings and results in json format to CWD in the file provided
    '''
    try:
        file_object = open(output_file_name, 'wb')
    except IOError:
        sys.stderr.write('FATAL ERROR: path to output file ' + output_file_name + ' not found')
        return 'FATAL ERROR: path to output file ' + output_file_name + ' not found'
    try:
        with file_object as output_file:
            pretty_dump = json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))
            output_file.write(pretty_dump)
    except SyntaxError:
        sys.stderr.write('FATAL ERROR: problem with output filestream to file object "'\
                        + output_file_name + '" --- sys.exec_info = '+ str(sys.exc_info()))
        return 'FATAL ERROR: path to output file ' + output_file_name + ' not found'
