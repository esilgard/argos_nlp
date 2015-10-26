#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

__author__='esilgard'

import re, sys
import global_strings
from datetime import datetime

class OneFieldPerReport(object):
    '''
        extract the value of a field which has one unambiguous value per report from normal cased text of the pathology report        
    ''' 
    __version__='OneFieldPerReport1.0'
    
    def __init__(self):
        self.field_name='Default'
        self.regex=''  
        self.return_dictionary = {}
        self.confidence=0.0
        self.match_style='Default'
        self.table='Default'
        self.value_type='Default'

    def get_version(self):
        return self.__version__
    
    def get(self, disease_group,dictionary):
        try:                
                      
            full_text=dictionary[(-1,'FullText',0,None)]           
            self.return_dictionary={global_strings.NAME:self.field_name,global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.KEY:global_strings.ALL,
                                    global_strings.VERSION:self.get_version(), global_strings.STARTSTOPS:[],global_strings.TABLE:self.table}
            ## match type object for equivilance test - this determines whether the value is based on the pattern match, or is a predetermined value
            SRE_MATCH_TYPE = type(re.match("", "")) 

            match=None
            ## handle different match types: greedy, non greedy, or multiple string match
            if self.match_style=='first':               
                match=re.match(r'.*?'+self.regex+'.*', full_text, re.DOTALL)
            elif self.match_style=='last':
                match=re.match(r'.*'+self.regex+'.*', full_text, re.DOTALL)
            elif self.match_style=='all':
                match=re.finditer(self.regex, full_text, re.DOTALL)
           
            if match:                
                if type(self.value_type)!=dict:                    
                    self.return_dictionary[global_strings.CONFIDENCE]=('%.2f' % self.confidence)               

                ## the field value will be based on the string match itself
                if type(match) is SRE_MATCH_TYPE:
                    ## making the value into a datetime -- TODO this should be moved into a separate class which handles multiple date formats
                    if self.field_name=='PathDate':                    
                        year=match.group(3)
                        month=match.group(1)
                        day=match.group(2)                    
                        if len(match.group(2))==1:               
                            day='0'+match.group(2)                    
                        self.return_dictionary[global_strings.VALUE]=str(datetime.strptime(year+','+month+','+day,'%Y,%m,%d').isoformat())
                        self.return_dictionary[global_strings.STARTSTOPS].append({global_strings.START:match.start(1),global_strings.STOP:match.end(3)})
                    
                    else:
                        if type(self.value_type)!=dict:                        
                            self.return_dictionary[global_strings.VALUE]=match.group(1).replace('  ',' ')## hacky string normalization for Pathologist
                        else:
                            self.return_dictionary[global_strings.VALUE]=self.value_type.get(True)[0]                        
                            self.return_dictionary[global_strings.CONFIDENCE]=('%.2f' % self.value_type.get(True)[1])
                    
                        self.return_dictionary[global_strings.STARTSTOPS].append({global_strings.START:match.start(1),global_strings.STOP:match.end(1)})        

                ## iterate through match iterator for 'all' style fields, which may have multiple
                else:                     
                    for m in match:                        
                        if type(self.value_type)!=dict:
                            self.return_dictionary[global_strings.VALUE]=m.group(1).replace(',','')  ## hacky string normalization for PathStageSystem
                        else:
                            self.return_dictionary[global_strings.VALUE]=self.value_type.get(True)[0]
                            self.return_dictionary[global_strings.CONFIDENCE]=('%.2f' % self.value_type.get(True)[1])
                        self.return_dictionary[global_strings.STARTSTOPS].append({global_strings.START:m.start(1),global_strings.STOP:m.end(1)})

            ## no match && value_type is a dictionary->the value is predetermined based on the lack of evidence
            if type(self.value_type) == dict and self.return_dictionary[global_strings.VALUE] is None:               
                self.return_dictionary[global_strings.VALUE]=self.value_type.get(False)[0]
                self.return_dictionary[global_strings.CONFIDENCE]=('%.2f' % self.value_type.get(False)[1])
            return ([self.return_dictionary],list)
        except:
            return ([{global_strings.ERR_TYPE:'Warning',global_strings.ERR_STR:'ERROR in %s module.' % self.field_name}],Exception)   
       
