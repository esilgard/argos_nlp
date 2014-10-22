#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''written 2013, last update October 2014'''
__version__='PathHistology1.0'

import re
import os,sys
path= os.path.dirname(os.path.realpath(__file__))+'/'


#############################################################################################################################################################

#############################################################################################################################################################


def get(dictionary):
   
    '''
    extract the histology from the lower cased text of the pathology report   
    
    return a dictionary of
        {"name":"PathHistology",
        "value":histology/histologies/or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"PathHistology","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}

    ## a list of histologies from the disease relevent histology_file
    try:    histologies=sorted([x.strip().lower() for x in open(path+'lung_histologies.txt','r').readlines()],key=lambda x: len(x))
    except: return ({'errorType':'Exception','errorString':'ERROR: could not access lung histology file at '+path+'lung_histologies.txt -- PathHistology not completed'},Exception)


    ## dictionary= sorted dictionary ##
    text='\n'.join([y for x in dictionary.keys() for x,y in sorted(dictionary[x].items())])
    ##*** NEED TO DEAL WITH CHAR OFFSETS AND DIFF TEXTS ***##
    histology_list=[]
    for section in dictionary:
        ##starting_index=
        if 'CYTOLOGIC IMPRESSION' in section or 'FINAL DIAGNOSIS' in section or 'COMMENT' in section:
            ## GET CHAR OFFSETS for sections? ##
            for index,results in dictionary[section].items():
                if re.search('[\d]{4};[\d]{1,4}:[\d\-]{1,6}',results):pass      ## weed out references to literature/papers - picking up pub. info like this: 2001;30:1-14.
                else:                              
                    text=results.lower()
                    textb=re.sub('[.,:;\\\/\-]',' ',text)
                    textb=re.sub('[a-zA-Z]([\\\/\-])',' ',text)
                    histology=find_histology(textb,histologies)
                    if histology:
                        already_seen=False
                        for each in histology_list:
                            if histology in each:
                                already_seen=True
                        if not already_seen:
                            histology_list.append(histology)
    if not histology_list:
        return_dictionary['value']=None
    else:
        return_dictionary['value']=';'.join(histology_list)
        return_dictionary['confidence']=("%.2f" % .8)
        return_dictionary['startStops'].append({"startPosition":0,"stopPostion":0})
    return (return_dictionary,dict)        
                

            

def find_histology(text,histologies):      
    for h in histologies:        
        if re.search(r'([\W]|^)'+h+r'([\W]|$)',text):            
            if not re.search(r'( no |negative |free of |against |(hx|history) of | to rule out|preclud)[\w ]{,50}'+h+r'([\W]|$)',text) and \
               not re.search(r'([\W]|^)'+h+r'[\w ]{,40}( unlikely| not (likely|identif)| negative)',text):               
                return h   
    return None
                      
