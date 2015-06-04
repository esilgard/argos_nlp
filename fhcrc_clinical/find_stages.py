#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='find_stages1.0'

## a completely rules based/pattern matching program for finding the prognostic stage of lung cancer patients ##
## *** eventually all lung specific aspects should be paramaterized so that the algorithm is not disease specific *** ##

import re,math,sys,os
from datetime import datetime
threshold=.25
lower_class_confidence_boost=.6


def reduce_confidence(confidence,num_notes):
    '''
    a coarse confidence reduction for scarsity of evidence
    '''
    if num_notes < 2:
        confidence -= .3
    elif num_notes < 6:
        confidence -= .2
    elif num_notes < 11:
        confidence -= .1
    if confidence <=0:confidence=0.0
    return confidence

pre_neg_wordlist=['mother',' mom ','father','dad','brother','sister','sibling',' uncle',' aunt','grandm','grandp','grandf','versus',
                      'cousin',' no ',' not ','negative','free of','against','rule out',' r o ',' if ','whether','unknown','consider'
                      'possibl','family','undetermined','would','potential','rather than','suspicious',' or ','questionable']
post_neg_wordlist=['unlikely','ruled out','free',' not ','consider',' or ','less likely','differential']
lung_words=[' lung','pulmonary','sclc',' lobe']
word_d={'IV':['stage( i.{,4} )?[ ]*iv','stage[ ]*4[ab ]','metastatic','m1 ','distant metasta'],
        'III':['stage( i.{,4} )?[ ]*iii[ab]?','stage[ ]*3[ab ]','t4[ ]*n[01]?[ ]*.[^1]','t[1234][ ]*n3[ ]*.[^1]','t3[ ]*n[123][ ]*.[^1]','t[12][ab]?[ ]*n2[ ]*.[^1]','locally advanced','regional metasta','metastatic lymph'],
        'II':['stage( i.{,4} )?[ ]*ii[ab ]','stage[ ]*2[ab ]','t[12][ab]?[ ]*n1[ ]*.[^1]','t2[b]?[ ]*n0[ ]*.[^1]','t3[ ]*n0[ ]*.[^1]'],
        'I':['stage( i.{,4} )?[ ]*i[ab ]','stage[ ]*1[ab ]','t1[ab][ ]*(n0|n[^1])[ ]*[m]?[^1]','t2a[ ]*n0[ ]*[m]?[^1]']}

other_wordlist=['thyroid','breast','sarcoma ','uterine','brain','prostate','renal','colon','gastrointestin','rectum','pharyn','ulcer','decub','hiv','oral','head',
                'esophag',' ovar','endometri','hepatic','liver','neuro','kidney','copd','ckd','ulcer','rectal',' bone','hepat','anal','bladder','hcc','gfr']
                                  
def get(note_list):
    '''
    note_list is of notes for one patient in the form of tuples of ((mrn,service_datetime,update_datetime),clinic_note_text)
    '''
    ## min and max clinic note service dates ##    
    min_max=(min([c[0][1] for c in note_list]),max([d[0][2] for d in note_list]))    
    #all_notes_case_insensitive='    '.join([x[1] for x in note_list]).lower()
    
    system_d=dict.fromkeys(['I','II','III','IV'],0)
    max_date=min_max[1]   
    total_days=(max_date-min_max[0]).days+1
    
    def add_weights(full_match,stage_keyword):     
        if not re.search('('+'|'.join(other_wordlist)+')',text[matches.start()-70:matches.end()+70]) and \
           not re.search('('+'|'.join(pre_neg_wordlist)+').{,50}'+stage_keyword,text[matches.start()-70:matches.end()]) and \
           not re.search(stage_keyword+'.{,50}('+'|'.join(post_neg_wordlist)+')',text[matches.start():matches.end()+70]):
                            
            system_d[stages]+=1
            if re.search('c(linical)?[ ]*'+stage_keyword,text) or re.search(stage_keyword+'[ ]*clinical',text):                    
                system_d[stages]-=.5            
        else:
            ## take off a tenth a point for evidence of another metastasis
            system_d[stages]-=.1
        
    for date_note in note_list:
        date=date_note[0][1]        
        day_diff=(max_date-date).days+1        
        text=re.sub('[.,():;\'\"\-\\\/?!+*\{\[\}\]]',' ',date_note[1].lower())       
        
        for stages,wordlist in word_d.items():                
            for matches in re.finditer('('+'|'.join(wordlist)+').{,250}?('+'|'.join(lung_words)+')',text):                
                full_match=matches.group(0)
                stage_keyword=matches.group(1)
                add_weights(full_match,stage_keyword)
               
            for matches in re.finditer('('+'|'.join(lung_words)+').{,250}?('+'|'.join(wordlist)+')',text):                
                full_match=matches.group(0)
                stage_keyword=matches.group(2)
                add_weights(full_match,stage_keyword)
            if 'lung' in text and ('disease stage' in text or 'clinical stage' in text):
                for matches in re.finditer('(disease|clinical) .{1,30} '+'('+'|'.join(wordlist)+')',text):
                    system_d[stages]+=.5
    
    system_answers= sorted([(x,max(0,system_d[x])) for x in system_d],key=lambda x: x[1],reverse=True)   
        
    if max(x[1] for x in system_answers)<=0:
        return_dictionary=('UNKNOWN',0.0)       
    else:
       
        system_answers=[(z[0],float(z[1])/sum([y[1] for y in system_answers])) for z in system_answers]
        original_answer=system_answers[0]
        candidate_list=[(x[0],x[1]) for x in system_answers if abs(system_answers[0][1]-x[1])<threshold and x[1]>0.0]
        candidate_list=sorted(candidate_list)            
        answer= candidate_list[0][0]            
        confidence=candidate_list[0][1]
        confidence=reduce_confidence(confidence,len(note_list))                        
        return_dictionary=(answer,confidence)
    return return_dictionary
