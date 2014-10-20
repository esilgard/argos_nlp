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


import sys
import json

## path to file containing flags and descriptions ##
## in the format -char<tab>description<tab>verbose_description(for help and error messages) ##
try:
    command_line_flag_file='command_line_flags.txt'
except:
    print '\nFATAL ERROR: command line flag file not found.  program aborted.';sys.exit()


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

def return_exec_code(x):
    '''
        helper method to retrieve the returned field value from each module
    '''
    return x


## parse the arguments from arg1 on into a dictionary - notify user of unrecognized flags ##
## NOTE - this does assume that flags start in the first position and every other argument is a flag ##
for index in range(0,len(args)-1,2):    
    if args[index] in command_line_flags:
        arguments[args[index]]=args[index+1]
    else:
        print 'nonfatal error:  unrecognized flag: '+args[index]+' this flag will be excluded from the arguments\n\
        refer to '+command_line_flag_file+' for a complete list and description of command line flags\n'

## ERR out for missing flags that are required ##    
missing_flags=required_flags-set(arguments.keys())
if len(missing_flags)>0:
    for each_flag in missing_flags:
        print 'ERROR: missing required flag: "'+each_flag+'" '+command_line_flags[each_flag][1]
    print '\nFATAL ERROR: cannot proceed without all required flags. program aborted.';sys.exit()
else:
    ## import and call appropriate module ##
    exec 'from fhcrc_'+arguments.get('-t')+' import process_'+arguments.get('-t')
    exec ('output=return_exec_code(process_'+arguments.get('-t')+'.main(arguments))')
    

          
## output results to file ##
## this is just a template for now - will have to deal with appropriate data structure, etc - probably with a seperate "output" module ##        
with open(arguments.get('-o'),'w') as output_file:
    for accession in output:
        output[accession]['PathNum']=accession        
        output_file.write(json.dumps(output[accession])+'\n')
print 'program run complete '+str(len(output))+' accessions processed successfully'
