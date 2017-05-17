# -*- coding: utf-8 -*-

'''author@esilgard'''
#
# Copyright (c) 2017 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import global_strings as gb

__version__='eln_classification1.0'

def get(mutation_dictionary, abnormality_set, offsets, karyotype_string, karyo_offset):
    '''
    Assign ELN risk categories based on important mutations
    '''
   
    eln_dictionary = {gb.NAME:gb.ELN, gb.TABLE:gb.CYTOGENETICS,
                       gb.VALUE:gb.UNKNOWN,gb.CONFIDENCE:1.0,
                       gb.STARTSTOPS:[], gb.VERSION:__version__}
   
   
    # classify FAVORABLE classified abnormalities
    # if FAVORABLE abnormality found: stop (this trumps all others)
    if 't(8;21)' in mutation_dictionary:
        for off in offsets['t(8;21)']:
            print off, '....', karyotype_string[off[0]-karyo_offset:off[1]-karyo_offset]#(q22;q22.1)
    #inv(16)(p13.1q22)
    #t(16;16)(p13.1;q22)  Emily’s program is good with this step
    #t(15;17)

    
    # if not favorable, classify unfavorable abnormalites
    # !!! need to add in "any 17p"
    for each in [gb.CMPX_TYPE, gb.MONO_TYPE, '-7','-17','-5','del(5q)']:
        if each in mutation_dictionary and mutation_dictionary[each] > 1:
            if offsets[each]:
                #print each, 'HIT',
                for off in offsets[each]:
                    pass
                    #print off, '....', karyotype_string[off[0]-karyo_offset:off[1]-karyo_offset]
            else:
                print each, 'HIT'
            eln_dictionary[gb.VALUE] = gb.UNFAVORABLE        
            eln_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[each]] 
    ## UNFAVORABLE string search for t(6;9)(p23;q34.1); t(v;11(q23.3) ; 
    ## t(9;22)(q34.1;q11.2); inv(3)(q21.3;q26.2) ; t(3;3)(q21.3;q26.2)
    
    # othewise, classify intermediate risk  
    if 't(9;11)(p21.3;q23.3)' in abnormality_set:
        eln_dictionary[gb.VALUE] = gb.INTERMEDIATE
        # REFER TO CELL LIST FOR ABNORMALITIES START STOP? OR PASS STRING
        #eln_dictionary[gb.STARTSTOPS] = [{gb.START:karyotype_string.find('t(9;11)(p21.3;q23.3)')
        #, gb.STOP:a[1]} for a in offsets[kar]]

     # not all ELN risk categories return a list of character offsets, 
    # since some classifications rely on the ABSENCE of some given evidence
    
    # any kind of abnormality that is not specifically outlined in ELN criteria -> INTERMEDIATE  
    if len(abnormality_set) >= 1:
        eln_dictionary[gb.VALUE] = gb.INTERMEDIATE
    if len(abnormality_set) == 0:
        eln_dictionary[gb.VALUE] = gb.INTERMEDIATE
        eln_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[gb.NORMAL]]
    
    
    #if the patient had fewer than 10 cells sampled, and no parsing errors encountering a cell count, then they are "INSUFFICIENT"
    try: 
        if  sum([int(x[gb.CELL_COUNT]) for x in  cell_list])<10:                      
            eln_dictionary[gb.VALUE] = gb.INSUFFICIENT
    except:
        mutation_dictionary[gb.WARNING] = True
    if  mutation_dictionary[gb.WARNING] == True:
        eln_dictionary[gb.VALUE] = gb.UNKNOWN
    return eln_dictionary
