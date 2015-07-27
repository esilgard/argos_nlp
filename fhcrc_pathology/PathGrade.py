#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='PathGrade1.0'

import re
import global_strings
## mapping of grade numbers to words ##

grades={'high':'high','low':'low','intermediate':'intermediate',
        ' 3 ':'high',' 1 ':'low',' 2 ':'intermediate',' iii ':'high',
        ' i ':'low',' ii ':'intermediate'}
histos=['carcinoma','cancer','sclc']

descriptions=['moderate','poor','well']
## helper method to extract grade from text for each specimen ##
def get_grade(text,line_onset):     
    grade_set=set([])
    start_stops_list=[] 

    ## number grades paired with the word "grade" ##
    for g,n in grades.items():
        m=re.match('.*('+g+'.{,15}grade).*',text)
        if m:
            grade_set.add(n)
            start_stops_list.append({global_strings.START:m.start(1)+line_onset,global_strings.STOP:m.end(1)+line_onset})
        m=re.match('.*(grade.{,15'+g+').*',text)
        if m:
            grade_set.add(n)
            start_stops_list.append({global_strings.START:m.start(1)+line_onset,global_strings.STOP:m.end(1)+line_onset})
          
    ## descriptions of cell differentiation ##
    for each_desc in descriptions:
        m= re.match('.*('+each_desc+'.{1,15}differentiated).*',text)
        if m:
            grade_set.add(m.group(1))        
            start_stops_list.append({global_strings.START:m.start(1)+line_onset,global_strings.STOP:m.end(1)+line_onset})
                
    ## specific grading system (FNCLCC)
    m=re.match('.*(([123])[/of ]{1,6}3.{,20}fn[c]?l[c]?c).*',text)    
    if m:
        grade_set.add(grades[' '+m.group(1)+' '])
        start_stops_list.append({global_strings.START:m.start(1)+line_onset,global_strings.STOP:m.end(1)+line_onset})
    else: m=re.match('.*(fn[c]?l[c]?c .{,20}([123])[/of ]{1,6}3).*',text)
    if m:
        grade_set.add(grades[' '+m.group(1)+' '])
        start_stops_list.append({global_strings.START:m.start(1)+line_onset,global_strings.STOP:m.end(1)+line_onset})
    else: m=re.match('.*(fn[c]?l[c]?c .{,20}grade.{,5}([123])).*',text)
    if m:
        grade_set.add(grades[' '+m.group(1)+' '])
        start_stops_list.append({global_strings.START:m.start(1)+line_onset,global_strings.STOP:m.end(1)+line_onset})

    ## discard substrings ##
    grade_list=sorted(grade_set,key=lambda x: len(x))    
    for i in range (len(grade_list)-1):
        if grade_list[i] in grade_list[i+1]:
            grade_set.remove(grade_list[i])
    
    return grade_set,start_stops_list

## main method ##        
def get(disease_group,dictionary):
   
    '''
    extract the grade from the lower cased text of the pathology report       
    '''
    return_dictionary_list=[]    
    whole_start_stops_set=[]
    whole_grade_set=set([])
    return_dictionary_list=[]   
    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():        
        for specimen,description in specimen_dictionary.items():            
            grade_set=set([])
            start_stops_set=set([])
            for section in dictionary:               
                section_specimen=section[3]
                line_onset=section[2]
                header=section[1]
                if section_specimen is not None and specimen in section_specimen and ('COMMENT' in header \
                   or 'FINAL' in header or 'IMPRESSION' in header or 'SUMMARY' in header):                               
                    text= dictionary[section].values()[0]                    
                    ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                    ## these can contain confusing general statements about the cancer and/or patients in general ##
                    if re.search('[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',text):pass               
                    else:                        
                        text=text.lower()
                        text=re.sub('[,:;\\\/\-]',' ',text); text=re.sub('[.] ', '  ',text)      ## this should keep decimal places and throw out periods                        
                        specimen_grade,offsets=get_grade(text,line_onset)                        
                        if specimen_grade:
                            grade_set=grade_set.union(specimen_grade)                            
                            start_stops_set.add(offsets) 
                            
            if grade_set:                
                return_dictionary_list.append({global_strings.NAME:"PathFindGrade",global_strings.KEY:specimen,global_strings.TABLE:global_strings.FINDING_TABLE,global_strings.VALUE:';'.join(grade_set),
                    global_strings.CONFIDENCE:("%.2f" % .85), global_strings.VERSION:__version__,global_strings.STARTSTOPS:list(start_stops_set)} )                
                whole_grade_set=whole_grade_set.union(grade_set)
                whole_start_stops_set.union(start_stops_set)
                
    if whole_grade_set:
        return_dictionary_list.append({global_strings.NAME:"PathGrade",global_strings.TABLE:global_strings.STAGE_GRADE_TABLE,global_strings.VALUE:';'.join(whole_grade_set),
                                   global_strings.CONFIDENCE:0.75,global_strings.VERSION:__version__,global_strings.STARTSTOPS:list(whole_start_stops_list)})
    
    ## if there were no specimens, or no specimen headers in the text - look at the text overall ##
    else:        
        for section in dictionary:               
            section_specimen=section[3]
            line_onset=section[2]
            header=section[1]
            if section_specimen is not None and specimen in section_specimen and ('COMMENT' in header \
                or 'FINAL' in header or 'IMPRESSION' in header or 'SUMMARY' in header):                               
                text= dictionary[section].values()[0]                    
                ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                ## these can contain confusing general statements about the cancer and/or patients in general ##
                if re.search('[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',text):pass               
                else:                        
                    text=text.lower()
                    text=re.sub('[,:;\\\/\-]',' ',text); text=re.sub('[.] ', '  ',text)      ## this should keep decimal places and throw out periods                        
                    specimen_grade,offsets=get_grade(text,line_onset)                        
                    if specimen_grade:
                        whole_grade_set=whole_grade_set.union(specimen_grade)                            
                        whole_start_stops_set.add(offsets) 
                            
        if whole_grade_set:
            return_dictionary_list.append({global_strings.NAME:"PathGrade",global_strings.TABLE:global_strings.STAGE_GRADE_TABLE,global_strings.VALUE:';'.join(whole_grade_set),
                global_strings.CONFIDENCE:0.65,global_strings.VERSION:__version__,global_strings.STARTSTOPS:list(whole_start_stops_set)})          
    return (return_dictionary_list,list)
