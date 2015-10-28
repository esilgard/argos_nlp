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

class OneFieldPerSpecimen(object):
    '''
        extract the value of a field which has one or more values per specimen from lower cased text of the pathology report        
    ''' 
    __version__='OneFieldPerSpecimen1.0'
    pre_negation=r'( not | no |negative |free of |without|against |(hx|history) of | to rule out|preclud| insufficient|suboptimal).{,75}'
    post_negation=r'.{,50}( unlikely| not (likely|identif)| negative)'
    ## default False flag; true means the slgorithm will infer some other value based on given input
    inference_flag=False
    ## default False secondary element; true means there's another data element that should
    ## be searched for based on either position or value of the first
    has_secondary_data_element = False
    secondary_data_elements = None
    def __init__(self):
        self.specimen_field_name ='Default'
        self.overall_field_name='Default'
        self.specimen_table = 'Default'
        self.overall_table = 'Default'
        self.specimen_confidence = 0.0
        self.unlabled_specimen_confidence = 0.0          
        self.return_dictionary_list = []    
        
        ## reference lists & dictionaries ##
        self.file_name_string = 'Default'
        self.dz_specific_list = []
        self.dz_specific_standardizations = {}
        self.general_list = []
        self.general_standardizations = {}

        ## relevant sections and negations of the report ##
        self.good_section = 'Default'
        self.bad_section = 'Default'
        
    
    def get_version(self):
        return self.__version__

    def get_dictionaries(self,reference_file_name_string):     
        string_list=[]
        standardizations={}
        for line in open(path+reference_file_name_string+'.txt','r').readlines():
            strings=line.split(';')
            for each in strings:
                each=each.strip().lower()
                standardizations[each]=strings[0].strip()
                string_list.append(each)
        string_list=sorted(string_list,key=lambda x: len(x),reverse=True)
        return string_list,standardizations

    ## loop through relevant sections findings PER SPECIMEN
    def get_specimen_finding(self,specimen,string_list,standardizations,dictionary):
       
        specimen_finding_set=set([])
        specimen_start_stops_set=set([])
        def find_string_match(text):            
            text=text.lower()
            text=re.sub(r'[.,:;\\\/\-]',' ',text)       
            for finding in string_list:             
                if re.search(r'([\W]|^)'+finding+r'([\W]|$)',text) and \
                   not re.search(self.pre_negation+finding+r'([\W]|$)',text) and \
                   not re.search(r'([\W]|^)'+finding+self.post_negation,text):                 
                    ## only return character offsets for the regular pathology text (not the SpecimenSource field)
                    if line_onset:                        
                        start=text.find(finding)+line_onset
                        stop=start+len(finding)                    
                        ## only add char off sets if there is not a longer (overlapping) string
                        ## this works because the finding list is sorted by length                
                        substring=False                    
                        for offsets in specimen_start_stops_set:
                            if start >= offsets[0] and start <= offsets[1]:
                                substring=True                   
                        if substring==False:
                            specimen_finding_set.add(standardizations[finding])
                            specimen_start_stops_set.add((start,stop))
                    else:                       
                        specimen_finding_set.add(standardizations[finding])
                        
        for section in sorted(dictionary):        
            section_specimen=section[3]                
            line_onset=section[2]
            header=section[1]
            
            if re.search(self.good_section,header) and not re.search(self.bad_section,header):                
                for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):                   
                    ## this is a special case for getting info from the SpecimenSource data field (not the regular path report)
                    if section==(0,'SpecimenSource',0,None):                      
                        if dictionary[section][0].get(specimen): 
                            find_string_match(dictionary[section][0].get(specimen)) 
                    ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                    ## these can contain confusing general statements about the cancer and/or patients in general ##
                    elif re.search(r'[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',results):pass                    
                    elif specimen in section_specimen:                     
                        find_string_match(results)                       
                               
        return specimen_finding_set,specimen_start_stops_set


   #helper method to retrieve the returned field value from each module
    def return_exec_code(self,x):        
        return x

    
    ## call secondary data element class where applicable
    def add_secondary_data_elements(self,each_field_dictionary,full_text):        
        for each_secondary_element in self.secondary_data_elements:            
            exec("import "+each_secondary_element)              
            exec("secondaryClass=self.return_exec_code("+each_secondary_element+"."+each_secondary_element+"())")
            return_d =  secondaryClass.get(each_field_dictionary,full_text)
            if return_d:
                self.return_dictionary_list.append(return_d)  
   


    def get(self,disease_group,dictionary):
        self.general_list,self.general_standardizations=self.get_dictionaries(self.file_name_string)
        self.dz_specific_list,self.dz_specific_standardizations=self.get_dictionaries(disease_group+'\\'+self.file_name_string)        
        ## general sets to track and aggregate overall findings for the report
        finding_set=set([])
        start_stops_set=set([])   

        ## loop through explicitly labeled specimens to look for corresponding findings in relevant sections
        for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():     
            for specimen,description in specimen_dictionary.items():
                specimen_finding_set,specimen_start_stops_set=self.get_specimen_finding(specimen,self.dz_specific_list,self.dz_specific_standardizations,dictionary)
        
                ## back off to general (non disease or anatomically specific) info
                if not specimen_finding_set:                
                    specimen_finding_set,specimen_start_stops_set=self.get_specimen_finding(specimen,self.general_list,self.general_standardizations,dictionary)          
                if specimen_finding_set:
                    if self.inference_flag: specimen_finding_set=self.infer(specimen_finding_set)
                    specimen_finding_dictionary = {global_strings.NAME:self.specimen_field_name,global_strings.KEY:specimen,global_strings.TABLE:self.specimen_table,
                                                        global_strings.VALUE:';'.join(specimen_finding_set),global_strings.CONFIDENCE:("%.2f" % self.specimen_confidence),global_strings.VERSION:self.get_version(),
                                                       global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in specimen_start_stops_set]}
                    self.return_dictionary_list.append(specimen_finding_dictionary)
                    finding_set=finding_set.union(specimen_finding_set)             
                    start_stops_set=start_stops_set.union(specimen_start_stops_set)              
                    if self.has_secondary_data_element == True:                        
                        self.add_secondary_data_elements(specimen_finding_dictionary,dictionary[(-1,'FullText',0,None)])
                        
        ## NOTE - this back off model only happens when specimen specific values, which means it will not currently pick up "summary cancer data" if specimen values were found
        ## back off model - to cover the case where there's no explicitly labeled specimen - assign to a general "UNK" specimen
        if not finding_set:            
            specimen_finding_set,specimen_start_stops_set=self.get_specimen_finding('',self.dz_specific_list,self.dz_specific_standardizations,dictionary)
            ## back off to general findings           
            if not specimen_finding_set:                 
                specimen_finding_set,specimen_start_stops_set=self.get_specimen_finding('',self.general_list,self.general_standardizations,dictionary)                
            if specimen_finding_set:         
                finding_set=finding_set.union(specimen_finding_set)
                if self.inference_flag: specimen_finding_set=self.infer(specimen_finding_set)
                start_stops_set=start_stops_set.union(specimen_start_stops_set)
                unk_finding_dictionary = {global_strings.NAME:self.specimen_field_name,global_strings.KEY:global_strings.UNK,global_strings.TABLE:self.specimen_table,global_strings.VERSION:self.get_version(),
                                            global_strings.VALUE:';'.join(specimen_finding_set),global_strings.CONFIDENCE:("%.2f" % self.unlabled_specimen_confidence),
                                            global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in specimen_start_stops_set]}
                self.return_dictionary_list.append(unk_finding_dictionary)         
                if self.has_secondary_data_element == True:                   
                    self.add_secondary_data_elements(unk_finding_dictionary,dictionary[(-1,'FullText',0,None)])                   

                    
        ## aggregate histologies of individual specimens for overall finding
        if finding_set:       
            if self.inference_flag: finding_set=self.infer(finding_set)
            overall_finding_dictionary={global_strings.NAME:self.overall_field_name,global_strings.KEY:global_strings.ALL,global_strings.TABLE:self.overall_table,global_strings.VALUE:';'.join(finding_set),
                                           global_strings.CONFIDENCE:("%.2f" % (sum([float(x.get(global_strings.CONFIDENCE)) for x in self.return_dictionary_list])/len(self.return_dictionary_list))),
                                          global_strings.VERSION:self.get_version(),global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in start_stops_set]}
            self.return_dictionary_list.append(overall_finding_dictionary) 
            if self.has_secondary_data_element == True:               
                self.add_secondary_data_elements(overall_finding_dictionary,dictionary[(-1,'FullText',0,None)])               
            
                    
        return (self.return_dictionary_list,list)        
                    
            
