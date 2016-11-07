'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

import re
import os
import global_strings as gb
import make_datetime
PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class OneFieldPerReport(object):
    '''
    extract the value of a field which has one unambiguous value
    per report from the pathology report
    '''
    __version__ = 'OneFieldPerReport1.0'
    file_name_string = ''
    def __init__(self):
        self.field_name = 'Default'
        self.regex = ''
        self.return_d = {}
        self.confidence = 0.0
        self.match_style = 'Default'
        self.table = 'Default'
        self.value_type = 'Default'
        
    def get_dictionaries(self, reference_file_name_string):
        '''
        get data element relevant resource files
        '''
        string_list = []
        standardizations = {}
        for line in open(PATH + reference_file_name_string + '.txt', 'r').readlines():
            strings = line.split(';')
            for each in strings:
                each = each.strip().lower()
                standardizations[each] = strings[0].strip()
                string_list.append(each)
        string_list = sorted(string_list, key=lambda x: len(x), reverse=True)
        return string_list, standardizations
    
    def get_version(self):
        ''' return algorithm version'''
        return self.__version__
    
    
    def get(self, disease_group, dictionary):
        ''' find field match based on different match types (greedy, all, first, last) '''
        def get_from_section(dictionary):
            '''
            search for a pattern in a specific section/sections of the document (currently implemented as a match first *not consistent with fullText search version)
            '''
            return_d = {gb.NAME: self.field_name, gb.VALUE: None, gb.CONFIDENCE: ('%.2f' % 0.0), \
                                 gb.KEY: gb.ALL, gb.VERSION: self.get_version(),\
                                 gb.STARTSTOPS: [], gb.TABLE: self.table}
            for section in dictionary:
                if re.search(self.good_section, section[1]):
                    for index, text in dictionary[section].items():
                        m = re.match(self.regex, text, re.DOTALL)
                        if m:
                            return_d[gb.VALUE] = m.group(1)
                            return_d[gb.CONFIDENCE] = ('%.2f' % self.confidence)                       
                            return_d[gb.STARTSTOPS].append({gb.START: m.start(1), gb.STOP:m.end(1)})                    
                            return return_d
            for section in dictionary:
                if re.search(self.less_good_section, section[1]):
                    for index, text in dictionary[section].items():
                        m = re.match(self.regex, text, re.DOTALL)
                        if m:
                            return_d[gb.VALUE] = m.group(1)
                            return_d[gb.CONFIDENCE] = ('%.2f' % self.less_good_confidence)                       
                            return_d[gb.STARTSTOPS].append({gb.START: m.start(1), gb.STOP:m.end(1)})                    
                            return return_d
            return return_d                   
        
        
        
        
        try:
            self.return_d = {gb.NAME: self.field_name, gb.VALUE: None, gb.CONFIDENCE: ('%.2f' % 0.0), \
                                 gb.KEY: gb.ALL, gb.VERSION: self.get_version(),\
                                 gb.STARTSTOPS: [], gb.TABLE: self.table}
            if hasattr(self ,'good_section'):               
                self.return_d = get_from_section(dictionary)

            if not self.return_d.get(gb.VALUE):   
                '''
                backoff to entire text
                '''
                full_text = dictionary[(-1, 'FullText', 0, None)]
                
                ## match type object for equivalence test - this determines whether the value
                ## is based on the pattern match, or is a predetermined value
                sre_match_type = type(re.match("", ""))
                match = None
    
                ## handle different match types: greedy, non greedy, or multiple string match
                if self.match_style == 'first':
                    match = re.match(r'.*?' + self.regex + '.*', full_text, re.DOTALL)
                elif self.match_style == 'last':
                    match = re.match(r'.*' + self.regex + '.*', full_text, re.DOTALL)
                elif self.match_style == 'all':
                    match = re.finditer(self.regex, full_text, re.DOTALL)
                    if self.file_name_string:            
                        ## keyword dictionaries for pattern matching            
                        self.dz_specific_list, self.dz_specific_standardizations = self.get_dictionaries\
                                                (disease_group + os.path.sep + self.file_name_string)
                        match = re.finditer('(' + self.regex + '(' + '|'.join(self.dz_specific_list) + '))', re.sub('[.,;\\\/\-]', ' ', full_text.lower()), re.DOTALL)
                    
                if match:
                    if (self.value_type) != dict:
                        self.return_d[gb.CONFIDENCE] = ('%.2f' % self.confidence)                    
                    ## the field value will be based on the string match itself
                    if isinstance(match, sre_match_type):
                        if 'Date' in self.field_name:
                            year = match.group(3)
                            month = match.group(1)
                            day = match.group(2)
                            date_obj = make_datetime.get((year,month,day),self.date_format_string)
                            self.return_d[gb.VALUE] = date_obj
                            self.return_d[gb.STARTSTOPS].append\
                                        ({gb.START: match.start(1), gb.STOP: match.end(3)})
                        else:
                            if (self.value_type) != dict:
                                ## hacky string normalization for Pathologist
                                self.return_d[gb.VALUE] = match.group(1).replace('  ', ' ')
                            else:
                                self.return_d[gb.VALUE] = self.value_type.get(True)[0]
                                self.return_d[gb.CONFIDENCE] = ('%.2f' % self.value_type.get(True)[1])
                            self.return_d[gb.STARTSTOPS].append\
                                            ({gb.START: match.start(1), gb.STOP:match.end(1)})
                    ## iterate through match iterator for 'all' style fields, which may have multiple matches
                    else:
                        field_set = set([])
                        for each_match in match:                            
                            # get normalized string name from dictionary
                            if self.file_name_string:
                                field_set.add(self.dz_specific_standardizations[each_match.group(3)])
                            ## just put match value in field_set
                            if not isinstance(self.value_type, dict):
                                if not self.file_name_string:
                                    ## hacky string normalization for PathStageSystem (although cellularityPercent also ends up here)
                                    field_set.add(each_match.group(1).replace(',', ''))
                            else:
                                field_set.add(self.value_type.get(True)[0])
                                self.return_d[gb.CONFIDENCE] = ('%.2f' % self.value_type.get(True)[1])
                            self.return_d[gb.STARTSTOPS].append({gb.START:each_match.start(1), gb.STOP: each_match.end(1)})
                        self.return_d[gb.VALUE] = ';'.join(sorted(field_set))
                ## no match && value_type && dictionary -> value is based on lack of evidence (reviews)
                if isinstance(self.value_type, dict) and self.return_d[gb.VALUE] is None:
                    self.return_d[gb.VALUE] = self.value_type.get(False)[0]
                    self.return_d[gb.CONFIDENCE] = ('%.2f' % self.value_type.get(False)[1])
            return ([self.return_d], list)
        except RuntimeError:
            return ([{gb.ERR_TYPE: 'Warning', gb.ERR_STR: 'ERROR in %s module.' \
                      % self.field_name}], Exception)
