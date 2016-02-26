'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

__version__ = 'output_text1.0'

import os, shutil, sys
import global_strings as gb

def main(input_file):
    '''
        output text files (reports) to a new directory
    '''
    if '.nlp' in input_file:
        output_directory = input_file[:input_file.find('.nlp')]
        if os.path.isdir(output_directory):
            try:
                os.rmdir(output_directory)
                os.mkdir(output_directory)
                return  (dict, {gb.ERR_TYPE: 'Warning', gb.ERR_STR: 'Output directory already existed at program runtime. It was empty and was deleted'})
            except EnvironmentError:
                try:
                    shutil.rmtree(output_directory)
                    os.mkdir(output_directory)
                    return (dict, {gb.ERR_TYPE: 'Warning', gb.ERR_STR: 'Output directory already existed at program runtime. It was not empty and was deleted'})
                except EnvironmentError:
                    return (Exception, 'FATAL ERROR: Output directory already existed at program runtime: ' + output_directory + '. \
                                        It could not be deleted' + str(sys.exc_info()[1]))
        else:
            try:
                os.mkdir(output_directory)
                return None, None
            except EnvironmentError:
                return (Exception, 'FATAL ERROR: failed to create directory: ' + output_directory + ' based on input filename ' + input_file)
    else:
        return (Exception, 'FATAL ERROR: bad input file name: ' + input_file + ' program aborted; expects in file name to end with ".nlp.tsv" in order to appropriately\
                            label text file directory')
