#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='PathSpecimenType1.0'

import re
import os
import global_strings
path= os.path.dirname(os.path.realpath(__file__))+'/'
dirs=path.split('\\')

def get(disease_group,dictionary):
    '''
    extract the specimen type/procedure from the SpecimenSource
    *there are no character offsets associated with this field*
    '''
    return_dictionary={global_strings.NAME:"PathSpecimenType",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,
                       global_strings.STARTSTOPS:[],global_strings.TABLE:global_strings.PATHOLOGY_TABLE}
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
    except: return ([{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'ERROR: could not access general procedures file at '+path+'procedures.txt -- PathSpecimenType not completed'}],Exception)

    full_text=dictionary[(-1,'FullText',0,None)]
    
    def get_procedures(procedures_list,standardizations):
        procedures=set([])
        start_stops_set=set([])
        text='  '.join((dictionary.get((0,'SpecimenSource',0,None),[(0,{})]).get(0).values()))
        text=re.sub('[.,:;\\\/\-\)\(]',' ',text).lower()
       
        for each_spec_type in procedures_list:           
            for each_match in re.finditer('.*( |^)('+each_spec_type+')( |$).*',text,re.DOTALL):               
                procedures.add(standardizations[each_spec_type])        
        return procedures
    ## spaceholder for more specific procedure lookukp
    spec_type=get_procedures(general_procedures,general_standardizations)    
    return_dictionary[global_strings.VALUE]=';'.join(spec_type)    
    return_dictionary[global_strings.CONFIDENCE]=("%.2f" % .80)
    
    return ([return_dictionary],list)
