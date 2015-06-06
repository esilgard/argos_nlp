#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
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
    output warnings and results in json format to CWD in the file provided in cmd line arguments
    author@esilgard
'''
 
import sys,os,json
import output_results,make_text_output_directory,codecs
from datetime import datetime
import subprocess

## declare output dictionary for values, warnings, and metadata
output_dictionary={}

## path to the nlp_engine.py script ##
nlp_engine_path= os.path.dirname(os.path.realpath(__file__))+'/'
original_wd=os.getcwd()

## timeit variable for performance testing ##
begin=datetime.today()

## grab version number from txt file which updates with git post-commit hook scipt (assume utf-8, but back up to utf-16) ## 
try: 
    __version__=codecs.open(nlp_engine_path+'version','rb', encoding='utf-8').readlines()[0].strip() 
except: 
    try: 
         __version__=codecs.open(nlp_engine_path+'version','rb', encoding='utf-16').readlines()[0].strip() 
    except: 
        sys.stderr.write('FATAL ERROR: could not locate or parse version file.') 
        sys.exit(1) 

## path to file containing command line flags and descriptions ##
## in the format -char<tab>description<tab>verbose_description(for help and error messages) ##
try:
    command_line_flag_file=open(nlp_engine_path+'command_line_flags.txt','r')
    try:
        ## set of required flags for program to run successfully ##
        required_flags=set([])
        ## dictionary of actual flags:argument values ##
        arguments={}
        ## dictionary of flag:tuple(flag description,verbose flag description) ##
        command_line_flags={}
        for line in command_line_flag_file.readlines():
            line=line.strip().split('\t')
            if line[1]=='required': required_flags.add(line[0])
            command_line_flags[line[0]]=(line[2],line[3])
        command_line_flag_file.close()
        args=sys.argv[1:]
    except:
        sys.stderr.write('FATAL ERROR: command line flag dictionary could not be established from file, potential formatting error.  program aborted.')
        sys.exit(1)    
except:
    sys.stderr.write('FATAL ERROR: command line flag file not found.  program aborted.')
    sys.exit(1)

## path to file containing the metadata dictionary (in json format) ##
try:
    meta_data_file=open(nlp_engine_path+'metadata.json','r')
    try:
        metadata_d=json.load(meta_data_file)
    except:
        sys.stderr.write('FATAL ERROR: json could not load metadata dictionary file, potential formatting error.  program aborted.')
        sys.exit(1)
except:
    sys.stderr.write('FATAL ERROR: metadata dictionary not found.  program aborted.')
    sys.exit(1)

## parse the arguments from arg1 on into a dictionary - notify user of unrecognized flags ##
## NOTE - this does assume that flags start in the first position and every other argument is a flag ##
for index in range(0,len(args)-1,2):    
    if args[index] in command_line_flags:
        arguments[args[index]]=args[index+1]
    else:
        output_dictionary["errors"].append({'errorType':'Warning','errorString':'nonfatal error:  unrecognized flag: '+args[index]+' this flag will be excluded from the arguments\
        refer to '+command_line_flag_file+' for a complete list and description of command line flags'})


######################################################################################################
def return_exec_code(x):
    '''
        helper method to retrieve the returned field value from each module
    '''
    return x
   

######################################################################################################
## build the dictionary for the json output ##

output_dictionary["controlInfo"]={}
output_dictionary["controlInfo"]["engineVersion"]= __version__
output_dictionary["controlInfo"]["referenceId"]="12345"
output_dictionary["controlInfo"]["docVersion"]="document version"
output_dictionary["controlInfo"]["source"]="document source"
output_dictionary["controlInfo"]["docDate"]="doc date"
output_dictionary["controlInfo"]["processDate"]=str(datetime.today().isoformat())
output_dictionary["controlInfo"]["metadata"]=dict((table,[field for field in metadata_d.get(arguments.get('-t')).get(table) if arguments.get('-g') in field.get('diseaseGroup')]) \
                                                  for table in metadata_d.get(arguments.get('-t')))
output_dictionary["errors"]=[]
output_dictionary["reports"]=[]
meta_data_file.close()

## add in flag info to the json output dictionary
output_dictionary["controlInfo"]["docName"]=arguments.get('-f')
output_dictionary["controlInfo"]["docType"]=arguments.get('-t')
output_dictionary["controlInfo"]["diseaseGroup"]=arguments.get('-g')

## ERR out for missing flags that are required ##    
missing_flags=required_flags-set(arguments.keys())
if len(missing_flags)>0:    
    for each_flag in missing_flags:
        sys.stderr.write('FATAL ERROR: missing required flag: '+each_flag+' '+command_line_flags[each_flag][1])    
    sys.exit(1)
else:   

    ## import and call appropriate module ##
    try:        
        exec 'from fhcrc_'+arguments.get('-t')+' import process_'+arguments.get('-t')        
    except:
        sys.stderr.write('FATAL ERROR:  could not import module process_'+arguments.get('-t'));sys.exit(1)
    mkdir_errors=make_text_output_directory.main(arguments.get('-f'))
    if mkdir_errors[0]==Exception:
        sys.stderr.write(mkdir_errors[1])

        sys.exit(1)        
    exec ('output,errors,return_type=return_exec_code(process_'+arguments.get('-t')+'.main(arguments,nlp_engine_path ))')
    
    if return_type==Exception:        
        sys.stderr.write(errors['errorString'])
        sys.exit(1)
    else:
        output_dictionary["reports"]=output
        output_dictionary["errors"]=errors
    
    if mkdir_errors[0]==dict:        
        output_dictionary["errors"].append(mkdir_errors[1])         

    ## iterate through errors - crash for Exceptions and output Warnings
    if output_dictionary["errors"]:        
        crash=False        
        for error_dictionary in output_dictionary["errors"]:            
            if error_dictionary and error_dictionary['errorType']=='Exception':
                crash=True
                sys.stderr.write(error_dictionary['errorString'])
        if crash==True:sys.exit(1)
    ## output results to file ##
    output_return = output_results.main(arguments.get('-o'),output_dictionary)
    if output_return:
        sys.exit(1)


## timeit - print out the amount of time it took to process all the reports ##
#print (datetime.today()-begin).days * 86400 + (datetime.today()-begin).seconds,'seconds to process '+str(len(output_dictionary["reports"]))+' reports'

    
        
