# -*- coding: utf-8 -*-

'''author@esilgard'''
#
# Copyright (c) 2017 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import global_strings as gb
import re

__version__='eln_classification1.0'

def get(abnormality_dictionary, abnormality_set, offsets, karyotype_string, karyo_offset):
    '''
    Assign ELN risk categories based on important mutations
    '''
   
    eln_dictionary = {gb.NAME:gb.ELN, gb.TABLE:gb.CYTOGENETICS,
                       gb.VALUE:gb.INTERMEDIATE,gb.CONFIDENCE:0.75,
                       gb.STARTSTOPS:[], gb.VERSION:__version__, 'Rationale' : []}
    classification_found = False
    # NOTE *** right now there is not a specific enough check for arm locations
    # relative to the chromosome location in string (could over capture for 
    # complex 3-4 chromosome abnormalities)
    favorable_abns = {'t(8;21)':'q22[.\d]*;q22','inv(16p)':'p13[.\d]*q22',
        't(16;16)':'p13[.\d]*;q22', 't(15;17)':''}
    unfavorable_abns = {'t(6;9)':'p23[.\d]*;q34','t(9;22)':'q34[.\d]*;q11.2',
        'inv(3)':'q21[.\d]*q26', 't(3;3)':'q21[.\d]*;q26', '-7':'', '-17':'', '-5':'',
        'del(5q)':'', 'translocation(17p)':'', 'inv(17p)':'','dup(17p)':'', 
        'trp(17p)':'', 'del(17p)':'', 'add(17p)':'', 'del(7q)':'', 'add(5q)':'',
        'translocation(11q)':'q23[.\d]*'}

    # if FAVORABLE abnormality found: stop (this trumps all others)
    for fav_abn in set(favorable_abns.keys()).intersection(set(abnormality_dictionary.keys())):
        
        for off in offsets[fav_abn]:
            if re.search(favorable_abns[fav_abn],karyotype_string[off[0]-karyo_offset:off[1]-karyo_offset]):
                print ''
                print fav_abn
                classification_found = True
                eln_dictionary[gb.VALUE] = gb.FAVORABLE        
                eln_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[fav_abn]]
                eln_dictionary['Rationale'].append(karyotype_string[off[0]-karyo_offset:off[1]-karyo_offset])
                print eln_dictionary['Rationale']
    
    # if not favorable, classify unfavorable abnormalites
    if not classification_found:
        for unfav_abn in set(unfavorable_abns.keys()).intersection(set(abnormality_dictionary.keys())):            
            for off in offsets[unfav_abn]:
                abn_str = karyotype_string[off[0]-karyo_offset:off[1]-karyo_offset]
                # any translocation EXCEPT a 9;11 will count
                if unfav_abn == 'translocation(11q)' and '9;11' in abn_str:
                    pass
                elif re.search(unfavorable_abns[unfav_abn], abn_str): 
                    classification_found = True
                    eln_dictionary[gb.VALUE] = gb.UNFAVORABLE        
                    eln_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[unfav_abn]]
                    eln_dictionary['Rationale'].append(karyotype_string[off[0]-karyo_offset:off[1]-karyo_offset])
                    
        # UNFAVORABLE for complex and monosomal karyotypes 
        # (there are not currently offsets associated with these fields)
        if abnormality_dictionary[gb.CMPX_TYPE] > 0 \
            or abnormality_dictionary[gb.MONO_TYPE] > 0:
                eln_dictionary[gb.VALUE] = gb.UNFAVORABLE
                classification_found = True
                eln_dictionary['Rationale'].append('Complex Or Monosomal Karyotype')
    
    # insufficient cells or all other abnormalities will default to "INTERMEDIATE"
    if not classification_found:
        eln_dictionary['Rationale'].append('Insufficient Cells, Normal Karyotype, or Other Abnormalities')
    
    return eln_dictionary
