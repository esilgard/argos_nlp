#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''
    written 2013, updates:
    December 2014: added table_name to return dictionary
'''
__version__='PathHistology1.0'

import re
import os
path= os.path.dirname(os.path.realpath(__file__))+'/'


#############################################################################################################################################################

#############################################################################################################################################################

def get(disease_group,dictionary):
    
    '''
    extract the histology from the lower cased text of the pathology report   
    
    return a list of dictionaries of each PathFinding (per specimen) and overall PathHistology (for the entire report)

    for example:
        {"name":"PathHistology",
        "value":histology/histologies
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "table":table_name,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
   
    return_dictionary_list=[]
    ## a list of histologies from the disease relevent histology_file
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
    except: return ([{'errorType':'Exception','errorString':'ERROR: could not access histology file at '+path+'/'+disease_group+'/'+'histologies.txt -- PathHistology not completed'}],Exception)
    
    full_text=dictionary[(-1,'FullText',0,None)]   
    
    histology_list=[]
    start_stops_list=[]
    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():
        for specimen,description in specimen_dictionary.items():
            
            specimen_histology_list=[]
            specimen_start_stops_list=[]

            for section in sorted(dictionary):                
                section_specimen=section[3]
                line_onset=section[2]
                header=section[1]
                
                if ('CYTOLOGIC IMPRESSION' in header or 'FINAL DIAGNOSIS' in header or 'COMMENT' in header):            
                    for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):
                        
                        ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                        ## these can contain confusing general statements about the cancer and/or patients in general ##
                        if re.search('[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',results):pass               
                        elif specimen in section_specimen:
                           
                            text=results.lower()
                            text=re.sub('[.,:;\\\/\-]',' ',text)                    
                            histology,onset,offset=find_histology(text,histologies)                           
                            if histology:
                                
                                specimen_start_stops_list.append({"startPosition":line_onset+onset,"stopPostion":line_onset+offset})                        
                                already_seen=False
                                for each in histology_list:
                                    if standardizations[histology] in each:
                                        already_seen=True
                                if not already_seen:                                    
                                    specimen_histology_list.append(standardizations[histology])
            
            if specimen_histology_list:                
                return_dictionary_list.append({"name":"PathFindHistology","recordKey":specimen,"table":"PathologyFinding","value":';'.join(set(specimen_histology_list)),"confidence":("%.2f" % .85),
                                          "algorithmVersion":__version__,"startStops":specimen_start_stops_list})
                histology_list+=specimen_histology_list
                start_stops_list+=specimen_start_stops_list                         
    if histology_list:
        return_dictionary_list.append({"name":"PathHistology","table":"Pathology","value":';'.join(set(histology_list)),"confidence":("%.2f" % .85),
                                      "algorithmVersion":__version__,"startStops":start_stops_list})
    else:
        ## back off model - not fully developed - looks for disease specific histologies anywhere in the text - regardless of specimens
        histology,onset,offset=find_histology(full_text,histologies)
        if histology:
            return_dictionary_list.append({"name":"PathHistology","table":"Pathology","value":standardizations[histology],"confidence":("%.2f" % .70),
                                      "algorithmVersion":__version__,"startStops":[{"startPosition":onset,"stopPostion":offset}]})

    return (return_dictionary_list,list)        
                
            
## check for the presence of a non-negated string ##
def find_histology(short_text,histologies):      
    for histo in histologies:        
        if re.search(r'([\W]|^)'+histo+r'([\W]|$)',short_text):            
            if not re.search(r'( no |negative |free of |against |(hx|history) of | to rule out|preclud)[\w ]{,50}'+histo+r'([\W]|$)',short_text) and \
               not re.search(r'([\W]|^)'+histo+r'[\w ]{,40}( unlikely| not (likely|identif)| negative)',short_text):                
                return (histo,short_text.find(histo),short_text.find(histo)+len(histo))
    return None,None,None
                      
