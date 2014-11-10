#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''last update October 2014'''
__version__='PathSpecimenType1.0'

import re
import os
path= os.path.dirname(os.path.realpath(__file__))
dirs=path.split('\\')

def get(dictionary):
    '''
    extract the specimen type/procedure from the SpecimenSource   
    
    return a dictionary of
        {"name":"PathSpecimenType",
        "value":spec type or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"PathSpecimenType","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
    ## a list of general procedures and their standardized forms from a general sites file ##
    general_procedures=[]
    general_standardizations={}
    
    try:
        for line in open('/'.join(dirs[:-1])+'/general_procedures.txt','r').readlines():
            procedures_list=line.split(';')
            for h in procedures_list:
                h=h.strip().lower()
                general_standardizations[h]=procedures_list[0].strip()
                general_procedures.append(h)
        general_procedures=sorted(general_procedures,key=lambda x: len(x),reverse=True)        
    except: return ({'errorType':'Exception','errorString':'ERROR: could not access general procedures file at '+'/'.join(dirs[:-1])+'/general_procedures.txt -- PathSpecimenType not completed'},Exception)

    ignore_section=sorted([(x,y) for z in sorted(dictionary.keys(), key=lambda c: c[0]) for x,y in dictionary[z].items()],key=lambda b:int(b[0]))
    full_text='\n'.join([a[1] for a in ignore_section])    
    
    if 'SpecimenSource' in dictionary:
        return_dictionary["value"]=dictionary["SpecimenSource"].values()[0].strip()
    text='\n'.join([y for x in dictionary.keys()  for x,y in sorted(dictionary[x].items())])

    def get_procedures(procedures_list,standardizations):
            procedures=set([])
            chars_up_to_this_point=0
            for section in sorted(dictionary):
                for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):
                    if 'Specimen' in section[1] or 'SPECIMEN' in section[1]:                    
                        text=results.lower()
                        text=re.sub('[.,:;\\\/\-\)\(]',' ',text)                     
                        for each_spec_type in procedures_list:                        
                            for each_match in re.finditer('.*( |^)'+each_spec_type+'( |$).*',text):
                                if standardizations[each_spec_type] not in procedures:
                                    procedures.add(standardizations[each_spec_type])                            
                                return_dictionary["startStops"].append({'startPosition':each_match.start(2)+chars_up_to_this_point,'stopPosition':each_match.end(2)+chars_up_to_this_point})
                    chars_up_to_this_point+=len(results)+1
            return procedures
    #print general_standardizations
    spec_type=get_procedures(general_procedures,general_standardizations)    
    return_dictionary['value']=';'.join(spec_type)
    
    return (return_dictionary,dict)
