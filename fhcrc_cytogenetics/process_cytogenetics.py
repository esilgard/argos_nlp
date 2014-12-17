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

import sys,cyto_parser,iscn_parser
import os,re
path2= os.path.dirname(os.path.realpath(__file__))+'/'

'''author@esilgard'''
'''December 2014'''
__version__='process_cytogenetics1.0'

training_set=[a.strip().split('\t') for a in open('K:/CRI/STTR/AML/Cytogenetics/train_set.txt','r').readlines()]
acc_set=set([a[2] for a in training_set])
### MAIN CLASS ###


def main(arguments,path):
    
    '''
    current minimum required flags for the pathology parsing in the "arguments" dictionary are:
        -f input cytogenetics file
        -g disease group
    '''
    try:
        cytogenetics_dictionary,return_type=cyto_parser.parse(arguments.get('-f'))        
        if return_type!=dict: return (cytogenetics_dictionary,return_type,Exception)
    except:
        
        return({},{'errorType':'Exception','errorString':'FATAL ERROR: could not parse input cytogenetics file '\
                   +arguments.get('-f')+' --- program aborted'},Exception)
    disease_group=arguments.get('-g')
   
    
    field_value_output=[]
    error_output=[]
    i=0
    ## create a list of output field dictionaries ##
    for mrn in cytogenetics_dictionary:
        
        for accession in cytogenetics_dictionary[mrn]:
            if accession in acc_set:
                for sections,text in cytogenetics_dictionary[mrn][accession].items():                    
                    karyotype= re.match('.*ISCN Diagnosis:[ ]+(.*)[ ]*',cytogenetics_dictionary[mrn][accession][sections])
                    if karyotype and sections!=0:
                        print mrn,accession,karyotype.group(1)
                        field_value_dictionary={}
                        field_value_dictionary["report"]=accession
                        field_value_dictionary["mrn"]=mrn                               
                        return_fields,return_errors,return_type=iscn_parser.get(karyotype.group(1))
                        
                        for r in return_fields:
                            print 'CELL'
                            for k,v in r.items():
                                print k,':',v
                        print '\n\n'
                        if return_type!=Exception:                
                            field_value_dictionary['fields']=return_fields
                            field_value_output.append(field_value_dictionary)
                        else:
                            return (field_value_output,{'errorType':'Exception','errorString':'ERROR in process_cytogenetics.get() - unknown number of reports completed'},list)           
              
    return (field_value_output,return_errors,list)
main({'-g':'aml','-f':'K:/CRI/STTR/AML/Cytogenetics/AML_CytogeneticsPathReports.txt'},'H:/NLP')
