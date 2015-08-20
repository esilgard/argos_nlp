#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='PathHistology1.0'

import re
import os
import global_strings
path= os.path.dirname(os.path.realpath(__file__))+'/'


#############################################################################################################################################################

#############################################################################################################################################################

def get(disease_group,dictionary):
   
    '''
    extract the histology from the lower cased text of the pathology report       
    return a list of dictionaries of each PathFindHistology (per specimen) and overall PathHistology (for the entire report)
    '''
   
    return_dictionary_list=[]
    ## a list of histologies from the disease relevent histology file
    histologies=[]
    standardizations={}
    try:
        for line in open(path+'/'+disease_group+'/'+'histologies.txt','r').readlines():
            histos=line.split(';')
            for h in histos:
                h=h.strip().lower()
                standardizations[h]=histos[0].strip()
                histologies.append(h)
        histologies=sorted(histologies,key=lambda x: len(x),reverse=True)
        ## append generic carcinoma histology to end of list as a last resort string match
        histologies.append('carcinoma');standardizations['carcinoma']='Carcinoma'
    except: return ([{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'ERROR: could not access histology file at '+path+'/'+disease_group+'/'+'histologies.txt -- PathHistology not completed'}],Exception)
    
    full_text=dictionary[(-1,'FullText',0,None)]   
    
    histology_list=[]
    start_stops_set=set([])
    
    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():        
        for specimen,description in specimen_dictionary.items():            
            specimen_histology_list=[]
            specimen_start_stops_set=set([])
            for section in sorted(dictionary):                
                section_specimen=section[3]                
                line_onset=section[2]
                header=section[1]                
                if ('IMPRESSION' in header or 'FINAL DIAGNOSIS' in header or 'COMMENT' in header) and 'CLINICAL' not in header:                    
                    for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):                        
                        ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                        ## these can contain confusing general statements about the cancer and/or patients in general ##
                        if re.search('[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',results):pass 
                        elif specimen in section_specimen:                           
                            text=results.lower()
                            text=re.sub('[.,:;\\\/\-]',' ',text)                            
                            histology,onset,offset=find_histology(text,histologies)                           
                            if histology:                               
                                specimen_start_stops_set.add((line_onset+onset,line_onset+offset))                                
                                already_seen=False
                                for each in specimen_histology_list:
                                    if standardizations[histology] in each:
                                        already_seen=True
                                if not already_seen: 
                                    specimen_histology_list.append(standardizations[histology])                       
            if specimen_histology_list:
                return_dictionary_list.append({global_strings.NAME:"PathFindHistology",global_strings.KEY:specimen,global_strings.TABLE:global_strings.FINDING_TABLE,global_strings.VALUE:';'.join(set(specimen_histology_list)),
                                               global_strings.CONFIDENCE:("%.2f" % .85),global_strings.VERSION:__version__,
                                               global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in specimen_start_stops_set]})
                histology_list+=specimen_histology_list
                start_stops_set=start_stops_set.union(specimen_start_stops_set)
              
    '''
    if not histology_list:
        ## back off model - not fully developed - it's dangerous to look for histologies anywhere in the text, but we'd like to cover the case
        ## where there's no explicitly labeled specimen
        histology,onset,offset=find_histology(full_text,histologies)
        print histology
        if histology:
           start_stops_set.add((onset,offset))
           histology_list.append(standardizations[histology])
           return_dictionary_list.append({global_strings.NAME:"PathFindHistology",global_strings.KEY:"UNK",global_strings.TABLE:global_strings.FINDING_TABLE,global_strings.VALUE:standardizations[histology],global_strings.CONFIDENCE:("%.2f" % .70),
                                      global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:onset,global_strings.STOP:offset}]})
    '''
    if histology_list:
        x= [{global_strings.START:char[0],global_strings.STOP:char[1]} for char in start_stops_set]
        return_dictionary_list.append({global_strings.NAME:"PathHistology",global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:';'.join(set(histology_list)),global_strings.CONFIDENCE:("%.2f" % .85),
                                      global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in start_stops_set]})     
    return (return_dictionary_list,list)        
                
            
## check for the presence of a non-negated string ##
def find_histology(short_text,histologies):      
    for histo in histologies:        
        if re.search(r'([\W]|^)'+histo+r'([\W]|$)',short_text):            
            if not re.search(r'( no |negative |free of |against |(hx|history) of | to rule out|preclud)[\w ]{,50}'+histo+r'([\W]|$)',short_text) and \
               not re.search(r'([\W]|^)'+histo+r'[\w ]{,40}( unlikely| not (likely|identif)| negative)',short_text):                
                return (histo,short_text.find(histo),short_text.find(histo)+len(histo))
    return None,None,None
                      
