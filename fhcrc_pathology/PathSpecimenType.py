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

#############################################################################################################################################################

################################################################################

def get(disease_group,dictionary):  
    '''
    extract the specimen type/procedure from the SpecimenSource
    *there are not always character offsets associated with this field*
    '''
    return_dictionary_list=[]
    ## a list of procedures regex and their standardized forms from a general sites file ##
    general_procedures=[]
    general_standardizations={}
    disease_group_procedures=[]
    disease_group_standardizations={}
    try:
        for line in open(path+'procedures.txt','r').readlines():
            procedures_list=line.split(';')
            for h in procedures_list:
                h=h.strip().lower()
                general_standardizations[h]=procedures_list[0].strip()
                general_procedures.append(h)
        general_procedures=sorted(general_procedures,key=lambda x: len(x),reverse=True)        
    except: return ([{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'ERROR: could not access general procedures file at '+path+'procedures.txt -- PathSpecimenType not completed'}],Exception)

    try:
        for line in open(path+'/'+disease_group+'/procedures.txt','r').readlines():
            disease_group_procedures_list=line.split(';')
            for g in disease_group_procedures_list:
                g=g.strip().lower()
                disease_group_standardizations[g]=disease_group_procedures_list[0].strip()
                disease_group_procedures.append(g)
        disease_group_procedures=sorted(disease_group_procedures,key=lambda x: len(x),reverse=True)        
    except: return ([{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'ERROR: could not access general procedures file at '+path+'/'+disease_group+'/procedures.txt -- PathSpecimenType not completed'}],Exception)

    def get_procedures(specimen,procedures_list,standardizations):        
        procedures=set([])
        procedure_start_stops_set=set([])
        
        ## helper method that has visibility of local variables, both for lookups and return dictionaries    
        def find_procedure_match(text):
            text=re.sub('[.,:;\\\/\-\)\(]',' ',text).lower()
                    
            for each_spec_type in procedures_list:                
                for each_match in re.finditer('.*( |^)('+each_spec_type+')( |$).*',text,re.MULTILINE):
                    proc=standardizations[each_spec_type]
                    ## this is trying to avoid a duplicate match span for a less specific procedure (e.g. just "biopsy)
                    general_proc=False
                    
                    for each in procedures:                       
                        if proc in each and len(proc)<len(each):                            
                            general_proc=True
                    if not general_proc:
                        procedures.add(standardizations[each_spec_type])                       
                        if line_onset:                                
                            procedure_start_stops_set.add((each_match.start(2)+line_onset,each_match.end(2)+line_onset))
                   
        for section in sorted(dictionary):           
            section_specimen=section[3]                
            line_onset=section[2]
            header=section[1]
            if section==(0,'SpecimenSource',0,None):
                if dictionary[section][0].get(specimen):
                    find_procedure_match(dictionary[section][0].get(specimen))
            elif ('FINAL DIAGNOSIS' in header) and 'CLINICAL' not in header:
                for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):                    
                    if specimen in section_specimen:
                        find_procedure_match(results)          
                     
        return (procedures,procedure_start_stops_set)
 
    ##############################################################################################################################################################        
    procedure_set=set([])
    procedure_start_stops_set=set([])

    ## loop through explicitly labeled specimens to look for corresponding procedures in relevant sections
    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():     
        for specimen,description in specimen_dictionary.items():          
            specimen_procedure_set,specimen_procedure_start_stops_set=get_procedures(specimen,disease_group_procedures,disease_group_standardizations)
            
            ## back off to general procedures
            if not specimen_procedure_set:                
                specimen_procedure_set,specimen_procedure_start_stops_set=get_procedures(specimen,general_procedures,general_standardizations)                
            if specimen_procedure_set:                
                return_dictionary_list.append({global_strings.NAME:"PathSpecimenType",global_strings.KEY:specimen,global_strings.TABLE:global_strings.FINDING_TABLE,global_strings.VALUE:';'.join(specimen_procedure_set),
                                               global_strings.CONFIDENCE:("%.2f" % .7),global_strings.VERSION:__version__,
                                               global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in specimen_procedure_start_stops_set]})
                procedure_set=procedure_set.union(specimen_procedure_set)             
                procedure_start_stops_set=procedure_start_stops_set.union(specimen_procedure_start_stops_set)
            
    ## back off model - to cover the case where there's no explicitly labeled specimen - assign to a general "UNK" specimen
    if not procedure_set:        
        specimen_procedure_set,specimen_procedure_start_stops_set=get_procedures('',disease_group_procedures,disease_group_standardizations)
        ## back off to general procedures
        if not specimen_procedure_set:
            specimen_procedure_set,specimen_procedure_start_stops_set=get_procedures('',general_procedures,general_standardizations)
        if specimen_procedure_set:
            procedure_set=procedure_set.union(specimen_procedure_set)
            procedure_start_stops_set=procedure_start_stops_set.union(specimen_procedure_start_stops_set)
            return_dictionary_list.append({global_strings.NAME:"PathSpecimenType",global_strings.KEY:"UNK",global_strings.TABLE:global_strings.FINDING_TABLE,global_strings.VALUE:';'.join(specimen_procedure_set),global_strings.CONFIDENCE:("%.2f" % .50),
                                      global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in specimen_procedure_start_stops_set]})
   
    ## aggregate procedures of individual specimens for overall histology
    if procedure_set:       
        return_dictionary_list.append({global_strings.NAME:"PathSpecimenType",global_strings.KEY:'ALL',global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:';'.join(procedure_set),
                                       global_strings.CONFIDENCE:("%.2f" % (sum([float(x.get(global_strings.CONFIDENCE)) for x in return_dictionary_list])/len(return_dictionary_list))),
                                      global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in procedure_start_stops_set]})     
    
    return (return_dictionary_list,list)  
    
