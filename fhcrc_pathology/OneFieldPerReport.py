#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

__author__='esilgard'

import re, sys
import global_strings as dict_keys
from datetime import datetime

class OneFieldPerReport(object):
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
            '''
            extract the value of a field which has one unambiguous value per report from normal cased text of the pathology report        
            '''
           
            full_text=dictionary[(-1,'FullText',0,None)]           
            self.return_dictionary={dict_keys.NAME:self.field_name,dict_keys.VALUE:None,dict_keys.CONFIDENCE:0.0,dict_keys.VERSION:self.get_version(),
                 dict_keys.STARTSTOPS:[],dict_keys.TABLE:self.table}       
            SRE_MATCH_TYPE = type(re.match("", ""))
            match=None            
            if self.match_style=='first':               
                match=re.match(r'.*?'+self.regex+'.*', full_text, re.DOTALL)
            elif self.match_style=='last':
                match=re.match(r'.*'+self.regex+'.*', full_text, re.DOTALL)
            elif self.match_style=='all':
                match=re.finditer(self.regex, full_text, re.DOTALL)
           
            if match:                
                if type(self.value_type)!=dict:                    
                    self.return_dictionary[dict_keys.CONFIDENCE]=('%.2f' % self.confidence)
                self.return_dictionary[dict_keys.KEY]=dict_keys.ALL
                
                if type(match) is SRE_MATCH_TYPE:
                    ## hacky workaround for making the value into a datetime
                    if self.field_name=='PathDate':                    
                        year=match.group(3)
                        month=match.group(1)
                        day=match.group(2)                    
                        if len(match.group(2))==1:               
                            day='0'+match.group(2)                    
                        self.return_dictionary[dict_keys.VALUE]=str(datetime.strptime(year+','+month+','+day,'%Y,%m,%d').isoformat())
                        self.return_dictionary[dict_keys.STARTSTOPS].append({dict_keys.START:match.start(1),dict_keys.STOP:match.end(3)})
                    elif type(self.value_type)!=dict:                        
                        self.return_dictionary[dict_keys.VALUE]=match.group(1)
                    else:
                        self.return_dictionary[dict_keys.VALUE]=self.value_type.get(True)[0]
                        self.return_dictionary[dict_keys.CONFIDENCE]=('%.2f' % self.value_type.get(True)[1])
                    self.return_dictionary[dict_keys.STARTSTOPS].append({dict_keys.START:match.start(1),dict_keys.STOP:match.end(1)})        
                else:  ## iterate through match iterator                   
                    for m in match:                        
                        if type(self.value_type)!=dict:
                            self.return_dictionary[dict_keys.VALUE]=m.group(1).replace(',','')  ## hacky string normalization for PathStageSystem
                        else:
                            self.return_dictionary[dict_keys.VALUE]=self.value_type.get(True)[0]
                            self.return_dictionary[dict_keys.CONFIDENCE]=('%.2f' % self.value_type.get(True)[1])
                        self.return_dictionary[dict_keys.STARTSTOPS].append({dict_keys.START:m.start(1),dict_keys.STOP:m.end(1)})
                
            if type(self.value_type) == dict and self.return_dictionary[dict_keys.VALUE] is None:               
                self.return_dictionary[dict_keys.VALUE]=self.value_type.get(False)[0]
                self.return_dictionary[dict_keys.CONFIDENCE]=('%.2f' % self.value_type.get(False)[1])
            return ([self.return_dictionary],list)
        except:
            return ([{dict_keys.ERR_TYPE:'Warning',dict_keys.ERR_STR:'ERROR in %s module.' % self.field_name}],Exception)   
       
