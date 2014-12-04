#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''August 2014'''
__version__='make_lung_stage_vectors1.0'

## create vectors for a naive bayes classification ##
import re,math,sys
from datetime import datetime

pre_neg_wordlist=[' mother',' mom ',' father',' dad',' brother',' sister',' sibling',' uncle',' aunt',' grandm',' grandp',' grandf','versus',
                  ' cousin',' no ',' not ','negative','free of','against','rule out',' r o ',' if ','whether','unknown','consider',
                  'possibl','family','undetermined','would','potential','rather than','suspicious',' or ','questionable']
post_neg_wordlist=['unlikely','ruled out','free',' not ','consider',' or ','less likely','differential']
lung_words=[' lung','pulmonary','sclc',' lobe']
word_d={'IV':['stage( i.{,4} )?[ ]*iv','stage[ ]*4[ab ]','metastatic','m1 ','distant metasta'],
        'III':['stage( i.{,4} )?[ ]*iii[ab]?','stage[ ]*3[ab ]','t4[ ]*n[01]?[ ]*.[^1]','t[1234][ ]*n3[ ]*.[^1]','t3[ ]*n[123][ ]*.[^1]','t[12][ab]?[ ]*n2[ ]*.[^1]','locally advanced','regional metasta','metastatic lymph'],
        'II':['stage( i.{,4} )?[ ]*ii[ab ]','stage[ ]*2[ab ]','t[12][ab]?[ ]*n1[ ]*.[^1]','t2[b]?[ ]*n0[ ]*.[^1]','t3[ ]*n0[ ]*.[^1]'],
        'I':['stage( i.{,4} )?[ ]*i[ab ]','stage[ ]*1[ab ]','t1[ab][ ]*(n0|n[^1])[ ]*[m]?[^1]','t2a[ ]*n0[ ]*[m]?[^1]']}
other_wordlist=['thyroid','breast','sarcoma ','uterine','brain','prostate','renal','colon','gastrointestin','rectum','pharyn','ulcer','decub','hiv','oral','head',
                'esophag',' ovar','endometri','hepatic','hepato','liver','neuro','kidney','copd','ckd','ulcer','rectal',' bone','hcc','anal','bladder','gfr']
                           
def make_datetime(date):    
    if len(date[1])==1:
        month='0'+date[1]
    else:   month=date[1]
    if len(date[2])==1:
        day='0'+date[2]
    else:   day=date[2]    
    date=datetime.strptime(month+','+day+','+date[0],'%m,%d,%Y')    
    return date
        

def get(note_d):
    vector_return_list=[]   
    
    ## min and max clinic note datetimes ##
    min_max=dict.fromkeys(note_d.keys())

    for pt in note_d:    
        min_max[pt]=(min([c[0] for c in note_d[pt]]),max([d[0] for d in note_d[pt]]))
        
    
    counts={True:0,False:0}

    instance=0
    for pts,date_note_list in note_d.items():
        
       
        max_date=min_max[pts][1].date()
        total_days=(max_date-min_max[pts][0].date()).days+1           
        
        def add_weights(text,stage_keyword,vector,matches3):
            
            a=re.match('.*('+'|'.join(other_wordlist)+').*',text[max(0,matches3.start()-70):min(matches3.end()+70,len(text))])                
            if a:                    
                vector+=' other_word_inside_match 1';vector+=' '+a.group(1).replace(' ','')+' 1'
            
            b=re.match('.*('+'|'.join(pre_neg_wordlist)+').{,50}'+stage_keyword+'.*',text[max(0,matches3.start()-70):matches3.end()])
            if b:
                vector+=' pre_neg 1'
                vector+=' '+b.group(1).replace(' ','')+' 1'
                
            c=re.match('.*'+stage_keyword+'.{,50}('+'|'.join(post_neg_wordlist)+').*',text[matches3.start():min(matches3.end()+70,len(text))])
            if c:
                vector+=' post_neg 1';vector+=' '+c.group(1).replace(' ','')+' 1'
            d=re.match('.*('+'|'.join(other_wordlist)+').{,50}'+stage_keyword+'.*',text[max(0,matches3.start()-70):matches3.end()])
            if d:
                 vector+=' pre_other 1'
                 vector+=' '+d.group(1).replace(' ','')+' 1'
                
            e=re.match('.*'+stage_keyword+'.{,50}('+'|'.join(other_wordlist)+').*',text[matches3.start():min(matches3.end()+70,len(text))])
            if e:
                vector+=' post_other 1';vector+=' '+e.group(1).replace(' ','')+' 1'
                
            if re.search('c(linical)?[ ]*'+stage_keyword,text) or re.search(stage_keyword+'[ ]*clinical',text):
                vector+=' clinical_stage 1'
            if re.search('p(athological)?[ ]*(stage)?[ ]*'+stage_keyword,text) or re.search(stage_keyword+'.{,10}[ ]path',text):
                vector+=' pathological_stage 1'
            
            if not a and not b and not c and not d and not e:
                vector+=' NO_neg 1'
            return vector
        ####################################################################################################################   
        for date_note in date_note_list:
            date=date_note[0].date()
            day_diff=(max_date-date).days+1        
            text=re.sub('[.,():;\'\"\-\\\/?!+*\{\[\}\]]',' ',date_note[1].lower())       
            
            for stages,wordlist in word_d.items():
                
                for matches1 in re.finditer('(('+'|'.join(wordlist)+').{,250}?('+'|'.join(lung_words)+'))',text):
                    instance+=1
                    vector1=''+pts+'_'+stages+'_'+str(instance)+' UNK'
                    vector1+=' stage_match='+stages+' 1'
                    full_match1=matches1.group(1)
                    stage_keyword1=matches1.group(2)
                    
                    stage_keyword_no_space1=stage_keyword1.replace(' ','')
                    vector1+=' stage_word='+stage_keyword_no_space1+' 1'
                    try:        ## weird bug work around- not returning the final match group
                        vector1+=' lung_word='+matches1.group(3).replace(' ','')+' 1'
                    except: vector1+=' lung_word='+matches1.group(1).split()[-1].strip()+' 1'
                    vector1+=' num_notes '+str(len(note_d[pts]))
                    vector1+=' len_from_end '+str(day_diff)
                    vector1=add_weights(text,stage_keyword1,vector1,matches1)
                    if 'stage' in stage_keyword1: vector1+=' stage_in_stage_keyword 1'
                    

                    tokens1=text[max(0,matches1.start()-70):min(len(text),matches1.end()+70)].replace(stage_keyword1,' '+stage_keyword_no_space1+' ').split()
                    index1=tokens1.index(stage_keyword_no_space1)
                    pre_index1=index1-1;post_index1=index1+1
                    
                    while pre_index1 >=index1-5 and pre_index1>=0:
                        vector1+=' w'+str(pre_index1-index1)+'='+tokens1[pre_index1]+' 1'
                        vector1+=' '+tokens1[pre_index1]+'_in_pre5_window 1'
                        if 'quamou' in tokens1[pre_index1] or 'enocarci' in tokens1[pre_index1] or 'sclc' in tokens1[pre_index1] or 'small' in tokens1[pre_index1]:
                            vector1+=' histology_in_w'+str(pre_index1-index1)+' 1'
                        
                        pre_index1-=1 
                    while post_index1 <=index1+6 and post_index1<len(tokens1):
                        vector1+=' w+'+str(post_index1-index1)+'='+tokens1[post_index1]+' 1'
                        vector1+=' '+tokens1[post_index1]+'_in_post5_window 1'
                        if 'quamou' in tokens1[post_index1] or 'enocarci' in tokens1[post_index1] or 'sclc' in tokens1[post_index1] or 'small' in tokens1[post_index1]:
                            vector1+=' histology_in_w+'+str(post_index1-index1)+' 1'
                        
                        
                        post_index1+=1

                    vector_return_list.append(vector1)

                ############################################################################################################
                for matches2 in re.finditer('(('+'|'.join(lung_words)+').{,250}?('+'|'.join(wordlist)+'))',text):                           
                    vector2=''+pts+'_'+stages+'_'+str(instance)+' UNK'
                    vector2+=' stage_match='+stages+' 1'
                    instance+=1
                    full_match2=matches2.group(1)
                    stage_keyword2=matches2.group(3)
                    stage_keyword_no_space2=stage_keyword2.replace(' ','')
                    if not matches2.group(3): print 'NO FINAL MATCH',matches.group(0);sys.exit()
                    vector2+=' stage_word='+stage_keyword2.replace(' ','')+' 1'
                    vector2+=' lung_word='+matches2.group(2).replace(' ','')+' 1'
                    vector2+=' num_notes '+str(len(note_d[pts]))
                    vector2+=' len_from_end '+str(day_diff)
                    vector2=add_weights(text,stage_keyword2,vector2,matches2)
                    if 'stage' in stage_keyword2: vector2+=' stage_in_stage_keyword 1'
                    else:                        vector2+=' no_stage_in_stage_keyword 1'

                    tokens2=text[max(0,matches2.start()-70):min(len(text),matches2.end()+70)].replace(stage_keyword2,' '+stage_keyword_no_space2+' ').split()
                    index=tokens2.index(stage_keyword_no_space2)
                    
                    pre_index=index-1;post_index=index+1
                  
                    while pre_index >=index-5 and pre_index>=0:
                        vector2+=' w'+str(pre_index-index)+'='+tokens2[pre_index]+' 1'
                        vector2+=' '+tokens2[pre_index]+'_in_pre5_window 1'
                        if 'quamou' in tokens2[pre_index] or 'enocarci' in tokens2[pre_index] or 'sclc' in tokens2[pre_index] or 'small' in tokens2[pre_index]:
                            vector2+=' histology_in_w'+str(pre_index-index)+' 1'
                        
                        pre_index-=1 
                    while post_index <=index+6 and post_index<len(tokens2):
                        vector2+=' w+'+str(post_index-index)+'='+tokens2[post_index]+' 1'
                        vector2+=' '+tokens2[post_index]+'_in_post5_window 1'
                        if 'quamou' in tokens2[post_index] or 'enocarci' in tokens2[post_index] or 'sclc' in tokens2[post_index] or 'small' in tokens2[post_index]:
                            vector2+=' histology_in_w+'+str(post_index-index)+' 1'
                        
                        post_index+=1
                    vector_return_list.append(vector2)
    
    return vector_return_list                
