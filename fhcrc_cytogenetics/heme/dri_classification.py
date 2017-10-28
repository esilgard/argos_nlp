# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:59:11 2017

@author: esilgard
"""

#
# Copyright (c) 2017 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import global_strings as gb
import re

__version__='dri_classification1.0'

def get(abnormality_dictionary, abnormality_set, offsets, karyotype_string, karyo_offset):
    '''
    Assign DRI risk categories based on important mutations
    '''
    dri_dictionary = {gb.NAME:gb.DRI, gb.TABLE:gb.CYTOGENETICS,
                       gb.VALUE:gb.INTERMEDIATE,gb.CONFIDENCE:0.75,
                       gb.STARTSTOPS:[], gb.VERSION:__version__, 'Rationale' : []}
    classification_found = False
    # NOTE *** right now there is not a specific enough check for arm locations
    # relative to the chromosome location in string (could over capture for 
    # complex 3-4 chromosome abnormalities)
    favorable_abns = {'t(8;21)':'', 'inv(16p)':'', 't(15;17)':''}
    if '46,XY,inv(3)(q21q26.2)[3]' in karyotype_string:
        print karyotype_string
        print abnormality_dictionary
        print abnormality_set

    # if FAVORABLE abnormality found: stop (this trumps all others)
    for fav_abn in set(favorable_abns.keys()).intersection(set(abnormality_dictionary.keys())):
        
        for off in offsets[fav_abn]:
            if re.search(favorable_abns[fav_abn],karyotype_string[off[0]-karyo_offset:off[1]-karyo_offset]):
                classification_found = True
                dri_dictionary[gb.VALUE] = gb.FAVORABLE        
                dri_dictionary[gb.STARTSTOPS] = [{gb.START:a[0], gb.STOP:a[1]} for a in offsets[fav_abn]]
                dri_dictionary['Rationale'].append(karyotype_string[off[0]-karyo_offset:off[1]-karyo_offset])
    
    # if not favorable, classify unfavorable abnormalites
    if not classification_found:                           
        # UNFAVORABLE for complex (4 or more abnormalities)
        # (there are not currently offsets associated with these fields)
        if len(abnormality_set) > 3:
            dri_dictionary[gb.VALUE] = gb.UNFAVORABLE
            classification_found = True
            dri_dictionary['Rationale'].append('Complex Karyotype')
    
    # insufficient cells or all other abnormalities will default to "INTERMEDIATE"
    if not classification_found:
        if abnormality_dictionary.get(gb.MUTS,0):
            dri_dictionary['Rationale'].append('Other Abnormalities')
        elif abnormality_dictionary.get(gb.NORMAL, 0) > 9:
            dri_dictionary['Rationale'].append('Normal Karyotype')
        else:
            dri_dictionary['Rationale'].append('Insufficient Cells')
    #print abnormality_dictionary.get(gb.NORMAL,0), abnormality_set, dri_dictionary['Rationale']
    dri_dictionary['Rationale'] = list(set(dri_dictionary['Rationale']))
    return dri_dictionary
