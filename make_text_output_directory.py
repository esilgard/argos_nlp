#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''
    text files (reports) to a new directory 
    author@esilgard
    December 2014
'''
__version__='output_text1.0'

import os,shutil,sys

def main(input_file):
<<<<<<< HEAD
    try:
=======
    if '.nlp' in input_file:
>>>>>>> origin/labkey_dev
        output_directory=input_file[:input_file.find('.nlp')]
        if(os.path.isdir(output_directory)):        
            try:
                os.rmdir(output_directory)
                os.mkdir(output_directory)
                return  (dict,{'errorType':'Warning','errorString':'Output directory already existed at program runtime. It was empty and was deleted'})
            except:
                try:
                    shutil.rmtree(output_directory)
                    os.mkdir(output_directory)
                    return (dict,{'errorType':'Warning','errorString':'Output directory already existed at program runtime. It was not empty and was deleted'})
                except:
                    return(Exception,'FATAL ERROR: Output directory already existed at program runtime: '+output_directory+'. It could not be deleted'+str(sys.exc_info()[1]))
                
        else:
            try:        
                os.mkdir(output_directory)
                return None, None
            except:            
                return(Exception,'FATAL ERROR: failed to create directory: '+output_directory+' based on input filename '+input_file)

<<<<<<< HEAD
    except:
=======
    else:
>>>>>>> origin/labkey_dev
        return(Exception,'FATAL ERROR: bad input file name: '+input_file+' program aborted')
        
