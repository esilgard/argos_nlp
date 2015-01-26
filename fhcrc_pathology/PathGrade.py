#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''
    written October 2014, updates:
    December 2014 - added table_name to return dictionary
'''
__version__='PathGrade1.0'

import re
import global_strings
## mapping of grade numbers to words ##

grades={'high':'high','low':'low','intermediate':'intermediate',
        ' 3 ':'high',' 1 ':'low',' 2 ':'intermediate',' iii ':'high',
        ' i ':'low',' ii ':'intermediate'}
histos=['carcinoma','cancer','sclc']


def get(disease_group,dictionary):
    '''
    extract the histology from the lower cased text of the pathology report       
    '''
    return_dictionary={global_strings.NAME:"PathGrade",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,
                       global_strings.STARTSTOPS:[],return_dictionary[global_strings.TABLE]:global_strings.STAGE_GRADE_TABLE}
    
    grade=[]
    text='\n'.join([y.lower() for x in dictionary.keys() if 'COMMENT' in x or 'FINAL' in x or 'IMPRESSION' in x for x,y in sorted(dictionary[x].items())])
    ## ** need to deal with character offsets and mulitple grades ... start with list append candidates? ##
    index=text.find('grade')
    window=text[max(0,index-45):min(index+45,len(text))]
    
    for g,n in grades.items():
        if re.match('.{,7}'+g+'.{,3}grade.{,7}',window): return n
        if re.search('[\W]'+g+'[\W]',window):
            if 'grade:' in window:
                return_dictionary[global_strings.VALUE]=n
                return (return_dictionary,dict)
            for h in histos:
                if h in window:
                    return_dictionary[global_strings.VALUE]=n
                    return (return_dictionary,dict)
            
      
    m=re.match('.*([123])[/of ]{1,6}3.{,20}fn[c]?l[c]?c.*',text)
    
    if m: return_dictionary[global_strings.VALUE]=grades[' '+m.group(1)+' ']
    else: m=re.match('.*fn[c]?l[c]?c .{,20}([123])[/of ]{1,6}3.*',text)
    if m: return_dictionary[global_strings.VALUE]=grades[' '+m.group(1)+' ']
    else: m=re.match('.*fn[c]?l[c]?c .{,20}grade.{,5}([123]).*',text)
    if m:
        return_dictionary[global_strings.VALUE]=grades[' '+m.group(1)+' ']

    return ([return_dictionary],list) 
