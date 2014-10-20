#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''October 2014'''

import re


   

## a list of histologies from the disease relevent histology_file
try:    histologies=sorted([x.strip().lower() for x in open('fhcrc_pathology/lung/lung_histologies.txt','r').readlines()],key=lambda x: len(x))
except: print 'ERROR: could not access lung histology file at fhcrc_pathology/lung/lung_histologies.txt -- program aborted';sys.exit(0)

#############################################################################################################################################################

#############################################################################################################################################################


def get(dictionary):                 
    '''
    associate the accessions with their histology
    '''
    histology_list=[]
    for section in dictionary:
        if 'CYTOLOGIC IMPRESSION' in section or 'FINAL DIAGNOSIS' in section or 'COMMENT' in section:
            for index,results in dictionary[section].items():
                if re.search('[\d]{4};[\d]{1,4}:[\d\-]{1,6}',results):pass      ## weed out references to literature/papers - picking up pub. info like this: 2001;30:1-14.
                else:                              
                    text=results.lower()
                    textb=re.sub('[.,:;\\\/\-]',' ',text)
                    textb=re.sub('[a-zA-Z]([\\\/\-])',' ',text)
                    histology=find_histology(textb)
                    if histology:
                        already_seen=False
                        for each in histology_list:
                            if histology in each:
                                already_seen=True
                        if not already_seen:
                            histology_list.append(histology)
    if not histology_list:   histology=None
    else:               histology=';'.join(histology_list)  
    return histology          
                

            

def find_histology(text):      
    for h in histologies:        
        if re.search(r'([\W]|^)'+h+r'([\W]|$)',text):            
            if not re.search(r'( no |negative |free of |against |(hx|history) of | to rule out|preclud)[\w ]{,50}'+h+r'([\W]|$)',text) and \
               not re.search(r'([\W]|^)'+h+r'[\w ]{,40}( unlikely| not (likely|identif)| negative)',text):               
                return h   
    return None
                      
