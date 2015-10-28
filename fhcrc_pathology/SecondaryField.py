# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

__author__="esilgard"

import re
import os
import global_strings
path= os.path.dirname(os.path.realpath(__file__))+'\\'

class SecondaryField(object):
    '''
        extract the value of a field which is dependant on another value        
    ''' 
    __version__='SecondaryField1.0'
  
    def __init__(self):
        self.field_name ='Default'
        standardization_dictionary = {}
        self.return_dictionary={}
        ## variable window sizes based on primary field string matches ##
        self.pre_window =0
        self.post_window = 0

        self.strings1=r''
        self.strings2=r''
        self.patterns =[]
        
    def get_version(self):
        return self.__version__

    def get(self,primary_field_dictionary,text):
       
        ## general sets to track and aggregate overall findings for the text
        finding_set=set([])
        start_stops_set=set([])
        ## a dictionary of offsets for each string match in primary field dictionary
        primary_offsets=primary_field_dictionary[global_strings.STARTSTOPS]
       
        ## loop through primary field matches
        for offsets in primary_offsets:           
            ## loop through secondary patterns
            #print text[offsets[global_strings.START]-self.pre_window:offsets[global_strings.STOP]+self.post_window].lower()
            for pattern in self.patterns:                
                ## find first match in each secondary pattern in restricted window around primary pattern             
                p = re.match(pattern[0],text[offsets[global_strings.START]-self.pre_window:offsets[global_strings.STOP]+self.post_window].lower(),re.DOTALL)
                if p:
                   
                    finding_set.add(p.group(pattern[1]))
                    start_stops_set.add((p.start(pattern[1])+(offsets[global_strings.START]-30),p.end(pattern[1])+(offsets[global_strings.START]-30)))

                    
        if finding_set:            
            self.return_dictionary={global_strings.NAME:self.field_name,global_strings.KEY:primary_field_dictionary[global_strings.KEY],
                                    global_strings.TABLE:primary_field_dictionary[global_strings.TABLE],global_strings.VERSION:self.get_version(),
                                    global_strings.VALUE:';'.join(finding_set),global_strings.CONFIDENCE:(primary_field_dictionary[global_strings.CONFIDENCE]),
                                    global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in start_stops_set]}
      
       
        return self.return_dictionary      
                    
            
