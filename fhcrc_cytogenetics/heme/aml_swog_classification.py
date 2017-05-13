'''author@esilgard'''
#
# Copyright (c) 2015-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import re
import global_strings as gb

__version__='swog_classification1.0'

def get(mutation_dictionary, abnormality_set, offsets, cell_list):
    '''
    Assign SWOG risk categories for AML based on important mutations
    '''
    
    swog_dictionary = {gb.NAME:gb.SWOG, gb.TABLE:gb.CYTOGENETICS,
                       gb.VALUE:gb.UNKNOWN,gb.CONFIDENCE:1.0,
                       gb.STARTSTOPS:[], gb.VERSION:__version__}
    ## not all swog risk categories return a list of character offsets, since some classifications rely on the ABSENCE of some given evidence
    
    # any kind of abnormality that is not specifically outlined in SWOG criteria -> MISCELLANEOUS                  
    if len(abnormality_set) >= 1:
        swog_dictionary[gb.VALUE] = gb.MISCELLANEOUS
    
    # any INTERMEDIATE abnormality will trump the miscellaneous categorization   
    for each in ['+8', '+6', 'del(12p)', '-Y']:
        if mutation_dictionary.get(each):
            swog_dictionary[gb.VALUE] = gb.INTERMEDIATE
            swog_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[each]]
    
    # INTERMEDIATE due to NORMAL karyotype will trump miscellaneous    
    if (len(abnormality_set) == 0 and  mutation_dictionary[gb.WARNING] == 0 and mutation_dictionary[gb.NORMAL] >= 10) :        
        swog_dictionary[gb.VALUE] = gb.INTERMEDIATE
        swog_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[gb.NORMAL]] 
    
    # UNFAVORABLE mutations will trump any previous risk categorization (misc or intermediate)
    if len(abnormality_set) >= 3:
        swog_dictionary[gb.VALUE] = gb.UNFAVORABLE        
    for each in ['-7', '-5', '3q', '9q', '11q', '17p', '20q', '21q', 'del(7q)', 'del(5q)', 't(6;9)', 't(9;22)']:                                                                                   
        if mutation_dictionary.get(each):
            swog_dictionary[gb.VALUE] = gb.UNFAVORABLE
            swog_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[each]] 
     
    # FAVORABLE mutations will trump any previous risk categorization (misc, intermediate, or unfavorable)
    for each in ['inv(16)', 't(16;16)', 'del(16q)', 't(15;17)']:
        if mutation_dictionary.get(each):
            swog_dictionary[gb.VALUE] = gb.FAVORABLE
            swog_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[each]]
            
    if mutation_dictionary.get('t(8;21)', 0) > 1 and not mutation_dictionary.get('del(9q)') and len(abnormality_set) < 3:
        swog_dictionary[gb.VALUE] = gb.FAVORABLE
        swog_dictionary[gb.STARTSTOPS] = [{gb.START:a[0],gb.STOP:a[1]} for a in offsets['t(8;21)']] 
     
    #if the patient had fewer than 10 cells sampled, and no parsing errors encountering a cell count, then they are "INSUFFICIENT"
    try:
 
        if  sum([int(x[gb.CELL_COUNT]) for x in  cell_list])<10:                      
            swog_dictionary[gb.VALUE] = gb.INSUFFICIENT
    except:
        mutation_dictionary[gb.WARNING] = 1
    if  mutation_dictionary[gb.WARNING] == 1:
        swog_dictionary[gb.VALUE] = gb.UNKNOWN
    return swog_dictionary
