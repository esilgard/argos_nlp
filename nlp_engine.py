#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
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


'''initial script of the Argos/NLP engine do deal with command line parsing and module outputs '''
'''author@esilgard'''
'''last updated October 2014'''
__version__='nlp_engine1.0'

import sys,os
import json
from datetime import datetime

cwd= os.getcwd()+'/'
path= os.path.dirname(os.path.realpath(__file__))+'/'

## path to file containing flags and descriptions ##
## in the format -char<tab>description<tab>verbose_description(for help and error messages) ##
try:
    command_line_flag_file=path+'command_line_flags.txt'
except:
    output_results(Exception,'\nFATAL ERROR: command line flag file not found.  program aborted.')


## set of required flags for program to run successfully ##
required_flags=set([])

## dictionary of actual flags:argument values ##
arguments={}


## dictionary of flag:tuple(flag description,verbose flag description) ##
command_line_flags={}
for line in open(command_line_flag_file,'r').readlines():
    line=line.strip().split('\t')
    if line[1]=='required': required_flags.add(line[0])
    command_line_flags[line[0]]=(line[2],line[3])

args=sys.argv[1:]

######################################################################################################
def return_exec_code(x):
    '''
        helper method to retrieve the returned field value from each module
    '''
    return x


## output results to file ##
## mostly empty template for results for now ##        
def output_results(output):
    try:        
        of=open(cwd+arguments.get('-o'),'w')
        
    except:
        sys.stderr.write('FATAL ERROR: path to output file '+cwd+arguments.get('-o')+' not found');sys.exit(1)
    try:
        with of as output_file:           
            #with open('json_error.txt','w')as o:
            #    for k,v in output.items():
            #        o.write(k+'\t'+str(v)+'\n\n')
            pretty_dump = json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))           
            output_file.write(pretty_dump)        
    except:
        sys.stderr.write('FATAL ERROR: problem with output filestream/json dump to file object "'+cwd+arguments.get('-o')+'" --- sys.exec_info = '+str(sys.exc_info()));sys.exit(1)
        

##########################################################################################################################
## build the dictionary for the json output ##
output_dictionary={}
output_dictionary["controlInfo"]={}
output_dictionary["controlInfo"]["engineVersion"]= __version__
output_dictionary["controlInfo"]["referenceId"]="123"
output_dictionary["controlInfo"]["docVersion"]="document version"
output_dictionary["controlInfo"]["source"]="document source"
output_dictionary["controlInfo"]["docDate"]="doc date"
output_dictionary["controlInfo"]["processDate"]=str(datetime.today())

output_dictionary["errors"]=[]
output_dictionary["reports"]=[]

## parse the arguments from arg1 on into a dictionary - notify user of unrecognized flags ##
## NOTE - this does assume that flags start in the first position and every other argument is a flag ##
for index in range(0,len(args)-1,2):    
    if args[index] in command_line_flags:
        arguments[args[index]]=args[index+1]
    else:
        output_dictionary["errors"].append({'errorType':'Warning','errorString':'nonfatal error:  unrecognized flag: '+args[index]+' this flag will be excluded from the arguments\
        refer to '+command_line_flag_file+' for a complete list and description of command line flags'})

## add in flag info to the json output dictionary
output_dictionary["controlInfo"]["docName"]=arguments.get('-f')
output_dictionary["controlInfo"]["docType"]=arguments.get('-t')
output_dictionary["controlInfo"]["diseaseGroup"]=arguments.get('-g')

## ERR out for missing flags that are required ##    
missing_flags=required_flags-set(arguments.keys())
if len(missing_flags)>0:
    error_string=''
    for each_flag in missing_flags:
        output_dictionary["errors"].append({'errorType':'Exception','errorString':'FATAL ERROR: missing required flag: '+each_flag+' '+command_line_flags[each_flag][1]})
    output_results(output_dictionary)
else:
    

    ## import and call appropriate module ##
    exec 'from fhcrc_'+arguments.get('-t')+' import process_'+arguments.get('-t')
    exec ('output,errors,return_type=return_exec_code(process_'+arguments.get('-t')+'.main(arguments,path))')
    
    if return_type==list:
        output_dictionary["reports"].append(output)
        output_dictionary["errors"].append(errors)
    else:
        output_dictionary["errors"].append(output)
    
    output_results(output_dictionary)
