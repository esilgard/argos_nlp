#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

import re
import global_strings as dict_keys


class PathStage(object):    
    __version__='PathStage1.0'

    def __init__(self):    
        self.stage_name='Default'  
        self.regex=''  
        self.return_dictionary = {}
        self.confidence=0.0


    def get_version(self):
        return self.__version__
    
    def get(self, disease_group,dictionary):       
        try:           
            '''
            extract the PathStage from normal cased text of the pathology report        
            '''
            full_text=dictionary[(-1,'FullText',0,None)]
           
            self.return_dictionary={dict_keys.NAME:self.stage_name,dict_keys.VALUE:None,dict_keys.CONFIDENCE:0.0,dict_keys.VERSION:self.get_version(),
                           dict_keys.STARTSTOPS:[],dict_keys.TABLE:dict_keys.STAGE_GRADE_TABLE}        
        
            stage=re.match(self.regex, full_text, re.DOTALL)
            if stage:
                self.return_dictionary[dict_keys.KEY]='ALL'
                self.return_dictionary[dict_keys.CONFIDENCE]=self.confidence
                self.return_dictionary[dict_keys.VALUE]=stage.group(1)
                self.return_dictionary[dict_keys.STARTSTOPS].append({dict_keys.START:stage.start(1),dict_keys.STOP:stage.end(1)})
            return ([self.return_dictionary],list)
           
        except:
            return ([{dict_keys.ERR_TYPE:'Warning',dict_keys.ERR_STR:'ERROR in %s module.' % self.stage_name}],Exception)
