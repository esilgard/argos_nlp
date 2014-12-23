#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''
    written October 2014, updates:
    December 2014 - added table_name to return dictionary
'''
__version__='PathSpecimenType1.0'

import re
import os
path= os.path.dirname(os.path.realpath(__file__))+'/'
dirs=path.split('\\')

def get(disease_group,dictionary):
    '''
    extract the specimen type/procedure from the SpecimenSource   
    
    return a dictionary of
        {"name":"PathSpecimenType",
        "value":spec type or None,
        "algorithmVersion": __version__,        
        "confidence": confidence_value,
        "table":table_name,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"PathSpecimenType","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
    ## a list of general procedures and their standardized forms from a general sites file ##
    general_procedures=[]
    general_standardizations={}
    
    try:
        for line in open(path+'procedures.txt','r').readlines():
            procedures_list=line.split(';')
            for h in procedures_list:
                h=h.strip().lower()
                general_standardizations[h]=procedures_list[0].strip()
                general_procedures.append(h)
        general_procedures=sorted(general_procedures,key=lambda x: len(x),reverse=True)        
    except: return ([{'errorType':'Exception','errorString':'ERROR: could not access general procedures file at '+path+'procedures.txt -- PathSpecimenType not completed'}],Exception)

    full_text=dictionary[(-1,'FullText',0,None)]
    
    def get_procedures(procedures_list,standardizations):
            procedures=set([])            
            for section in sorted(dictionary):
                if 'SPECIMEN' in section[1]:
                    section_onset=section[2]                                                          
                    text='\n'.join(results.lower() for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])))
                    text=re.sub('[.,:;\\\/\-\)\(]',' ',text)                     
                    for each_spec_type in procedures_list:                        
                        for each_match in re.finditer('.*( |^)'+each_spec_type+'( |$).*',text,re.DOTALL):
                            if standardizations[each_spec_type] not in procedures:
                                procedures.add(standardizations[each_spec_type])                            
                            return_dictionary["startStops"].append({'startPosition':each_match.start(2)+section_onset,'stopPosition':each_match.end(2)+section_onset})
                    
            return procedures
    
    spec_type=get_procedures(general_procedures,general_standardizations)    
    return_dictionary['value']=';'.join(spec_type)
    return_dictionary["table"]='Pathology'
    return_dictionary["confidence"]=.8
    
    return ([return_dictionary],list)
