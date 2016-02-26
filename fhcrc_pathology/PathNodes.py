#
# Copyright (c) 2014-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

import re
import global_strings as dict_keys


class PathNodes(object):    
    __version__='PathNodes1.0'

    def __init__(self):    
        self.node_name='Default'  
        self.regex=''  
        self.confidence=0.0
        self.site_nodes=0
        self.pos_nodes=0
        self.num_nodes=0
        self.return_dictionary_list=[]


    def get_version(self):
        return self.__version__
    
    def get(self, disease_group,dictionary):       
        try:           
            '''
            extract the node finding information from normal cased text of the pathology report        
            '''
            full_text=dictionary[(-1,'FullText',0,None)]           
            recordKey=0
            return_dictionary_list=[]
            for node in re.finditer(self.regex, full_text, re.DOTALL):
                #print recordKey
                #print node.group(1),node.group(2),node.group(3)
                print [{dict_keys.START:node.start(self.site_nodes),dict_keys.STOP:node.end(self.site_nodes)}]
               
                self.return_dictionary_list.append({dict_keys.CONFIDENCE:self.confidence,dict_keys.NAME:'PathFindSite',dict_keys.VALUE:node.group(self.site_nodes),
                                                    dict_keys.STARTSTOPS:[{dict_keys.START:node.start(self.site_nodes),dict_keys.STOP:node.end(self.site_nodes)}],
                                                    dict_keys.KEY:recordKey,global_strings.TABLE:dict_keys.NODE_TABLE})
                #print 'k'
                self.return_dictionary_list.append({dict_keys.CONFIDENCE:self.confidence,dict_keys.NAME:'PathFindNodesPos',dict_keys.VALUE:node.group(self.pos_nodes),
                                                    dict_keys.STARTSTOPS:[{dict_keys.START:node.start(self.pos_nodes),dict_keys.STOP:node.end(self.pos_nodes)}],
                                                    dict_keys.KEY:recordKey,global_strings.TABLE:dict_keys.NODE_TABLE})
                #print 'l'
                self.return_dictionary_list.append({dict_keys.CONFIDENCE:self.confidence,dict_keys.NAME:'PathFindNumNodes',dict_keys.VALUE:node.group(self.num_nodes),
                                                    dict_keys.STARTSTOPS:[{dict_keys.START:node.start(self.num_nodes),dict_keys.STOP:node.end(self.num_nodes)}],
                                                    dict_keys.KEY:recordKey,global_strings.TABLE:dict_keys.NODE_TABLE})

                recordKey+=1
            
            return (self.return_dictionary_list,list)
           
        except:
            #print 'ERROR'
            return ([{dict_keys.ERR_TYPE:'Warning',dict_keys.ERR_STR:'ERROR in %s module.' % self.node_name}],Exception)
