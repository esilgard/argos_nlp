#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

import re
import global_strings as dict_keys


class OncoplexTesting(object):    
    __version__='OncoplexTesting1.0'
    print 'oncoplexTesting class'
    def __init__(self):    
        self.test_name='Default'  
        self.regex=''  
        self.return_dictionary = {}
        self.return_dictionary_list=[]

    def get_version(self):
        return self.__version__
    
    def get(self, disease_group,dictionary):       
        try:
            print 'in try'            
            '''
            extract the Oncoplex Testing Results from normal cased text of the pathology report
            currently pulling the first line of oncoplex testing results
            '''
            full_text=dictionary[(-1,'FullText',0,None)]
            print 'in try',1
            print type(full_text)
            onco_text=re.findall(r'[\.\r\n]*^OPX Results:[ ]*(.+)[\.\r\n]*',full_text,re.MULTILINE)
            print 'in try',3
            for o in onco_text:                   
                print o
                test=re.match(self.regex, o)
                if test:
                    ##***split by POSITIVE for or NEGATIVE for ##
                    self.return_dictionary={dict_keys.NAME:self.test_name,dict_keys.VALUE:None,dict_keys.CONFIDENCE:0.0,dict_keys.VERSION:self.get_version(),
                    dict_keys.STARTSTOPS:[],dict_keys.TABLE:dict_keys.TEST_TABLE}
                    print test.group(1)
                    self.return_dictionary[dict_keys.CONFIDENCE]=0.90
                    self.return_dictionary[dict_keys.VALUE]=test.group(1)
                    ## this is not foolproof - right now if there are duplicate strings, it will return duplicate offsets for the first string
                    self.return_dictionary[dict_keys.STARTSTOPS].append({dict_keys.START:full_text.find(o)+test.start(1),dict_keys.STOP:full_text.find(o)+test.end(1)})
                    return_dictionary_list.append(self.return_dictionary)
            print self.return_dictionary_list           
            return (self.return_dictionary_list,list)
            
        except:
            return ({dict_keys.ERR_TYPE:'Exception',dict_keys.ERR_STR:'ERROR in %s module.' % self.test_name},Exception)
