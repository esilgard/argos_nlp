#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''written 2013, last update October 2014'''
__version__='PathHistology1.0'

import re
import os
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
    histologies=[]
    standardizations={}
    try:
        for line in open(path+'lung_histologies.txt','r').readlines():
            histos=line.split(';')
            for h in histos:
                h=h.strip().lower()
                standardizations[h]=histos[0].strip()
                histologies.append(h)
        histologies=sorted(histologies,key=lambda x: len(x),reverse=True)        
    except: return ({'errorType':'Exception','errorString':'ERROR: could not access lung histology file at '+path+'lung_histologies.txt -- PathHistology not completed'},Exception)

    
    full_text=text=dictionary[(-1,'FullText',0)]
   
    
    histology_list=[]
    for section in sorted(dictionary):
        section_onset=section[2]
        header=section[1]
        if 'CYTOLOGIC IMPRESSION' in header or 'FINAL DIAGNOSIS' in header or 'COMMENT' in header:            
            for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):               
                ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                ## these can contain confusing general statements about the cancer and/or patients in general ##
                if re.search('[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',results):pass
               
                else:                              
                    text=results.lower()
                    text=re.sub('[.,:;\\\/\-]',' ',text)                    
                    histology,onset,offset=find_histology(text,histologies)                    
                    if histology:
                        return_dictionary['startStops'].append({"startPosition":section_onset+onset,"stopPostion":section_onset+offset})                        
                        already_seen=False
                        for each in histology_list:
                            if standardizations[histology] in each:
                                already_seen=True
                        if not already_seen:
                            histology_list.append(standardizations[histology])
        
                      
    if not histology_list:
        return_dictionary['value']=None
    else:
        return_dictionary['value']=';'.join(histology_list)
        return_dictionary['confidence']=("%.2f" % .85)
    ##print out to file to double check char offsets ##
    '''
    if 'SU-11-32011' in full_text:
        offsets=sorted(return_dictionary['startStops'],key=lambda x: x['startPosition'])
        offset_list=[y.values() for y in offsets]
        print 'OFFSET LIST',offset_list
        print return_dictionary['value']
        for start,end in reversed(offset_list):            
            full_text=full_text[:end]+']*]'+full_text[end:]
            full_text=full_text[:start]+'[*['+full_text[start:]
        with open('H:/NLP/offset_tester.txt','w') as output:
         output.write(full_text)
    '''   
    return (return_dictionary,dict)        
                
            
## check for the presence of a non-negated string ##
def find_histology(short_text,histologies):      
    for histo in histologies:        
        if re.search(r'([\W]|^)'+histo+r'([\W]|$)',short_text):            
            if not re.search(r'( no |negative |free of |against |(hx|history) of | to rule out|preclud)[\w ]{,50}'+histo+r'([\W]|$)',short_text) and \
               not re.search(r'([\W]|^)'+histo+r'[\w ]{,40}( unlikely| not (likely|identif)| negative)',short_text):                
                return (histo,short_text.find(histo),short_text.find(histo)+len(histo))
    return None,None,None
                      
