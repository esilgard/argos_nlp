'''author@esilgard'''
#
# Copyright (c) 2015-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

import global_strings as gb
import aml_swog_classification

__version__='cytogenetics_mutation_parser1.0'

def get(cell_list, karyotype_string, karyo_offset):
    '''
        take a parsed list of cells
        where each element within the cell group has a list of dictionaries of abnormalities
        as well as a cell count, a chromosome number, a warning flag, a chromosome, and 
        a cell order (just the order the cell line was listed in the report)        
        return the same list with an appended swog label dictionary
    '''
    return_errors = []
    return_dictionary_list = [{gb.FIELD:gb.KARYOTYPE_STRING, gb.VALUE:karyotype_string, gb.CONFIDENCE:1.0,
                            gb.VERSION:__version__, gb.STARTSTOPS:[{gb.START:karyo_offset,
                            gb.STOP:karyo_offset + len(karyotype_string)}], gb.TABLE:gb.CYTOGENETICS}]
    ## a dictionary of mutation types and their cell counts
    mutations=dict.fromkeys(['inv(16)', 't(16;16)', 'del(16q)', 't(8;21)', 't(15;17)',
                                      't(8;21)', gb.NORMAL, '+8', '+6', '-Y', 'del(12p)', '-7',
                                      '-5', '3q', '9q', '11q', '17p', '20q', '21q', 'del(7q)',
                                      'del(5q)', 'del(9q)', 't(16;20)', 't(14;16)', 't(11;14)',
                                      't(4;14)', 'del(17p)', 'del(1p)', 'add(1q)', 't(6;9)',
                                      't(9;22)','del(13p)', 'del(13q)', '-13',
                                     gb.MONOS, gb.MUTS, gb.TRIS, gb.WARNING], 0)
    
    ## a dictionary of mutation types and their offsets - which will be stored as a list of tuples (start,stop)
    offsets = {}
    for variation in mutations:
        offsets[variation] = []
   
    # used to track unique mutations
    abnormality_set = set([])
    monosomy_set = set([])
    trisomy_set = set([])
##################################################################################################################################

    ## start by counting cells with each type of pertinent aberration      
    for x in cell_list:        
        if x[gb.WARNING]:
            mutations[gb.WARNING] = 1
        try:
            cell_count = int(x[gb.CELL_COUNT])            
            cell_offset = x['Offset']
            ## minimum number of cells needed to verify a clone (either 2 or 3)
            clone_minimum = 2            
            if int(x['ChromosomeNumber'][:2]) < 46:clone_minimum = 3
            if x[gb.ABNORMALITIES]:
                for y in x[gb.ABNORMALITIES]:
                    try:                        
                        for z, zz in y.items():                            
                            variation_string = z + '(' + zz[0] + ')' + zz[1]
                            if cell_count >= clone_minimum:
                                if z == '-' or z == '+':
                                    variation_string = z + zz[0] + zz[1]                            
                                variation_start = cell_offset + (karyotype_string[cell_offset-karyo_offset:].find(variation_string))
                                variation_end = variation_start + len(variation_string)                            
                                ## all trisomies
                                if z == '+':
                                    if cell_count >= 2:                             
                                        abnormality_set.add(variation_string) 
                                        trisomy_set.add(variation_string)
                                        offsets[gb.TRIS].append((variation_start,variation_end))
                                        for each in ['8', '6']:
                                            if zz[0] == each:
                                                mutations['+' + each] += cell_count
                                                offsets['+' + each].append((variation_start, variation_end))
                                    
                                ## all monosomies                            
                                elif z == '-':
                                    if cell_count >= 3:
                                        monosomy_set.add(variation_string)
                                        abnormality_set.add(variation_string) 
                                        offsets[gb.MONOS].append((variation_start, variation_end))
                                       
                                        for each in ['Y', '7', '5', '13']:
                                            if zz[0] == each:                                                
                                                mutations['-'+each] += cell_count
                                                offsets['-'+each].append((variation_start, variation_end))
                                ## all other abnormalities do not have a cell count minimum
                                else:
                                    abnormality_set.add(variation_string) 
                                ## all chromosome 16 abnormalities
                                if '16' in zz[0]:                                                 
                                    if (z == 'inv'):
                                        mutations['inv(16)'] += cell_count
                                        offsets['inv(16)'].append((variation_start, variation_end))
                                    elif (z == 't' and '16;16' in zz[0]):
                                        mutations['t(16;16)'] += cell_count
                                        offsets['t(16;16)'].append((variation_start, variation_end))
                                    elif (z == 'del' and 'q' == zz[1]):
                                        mutations['del(16q)'] += cell_count
                                        offsets['del(16q)'].append((variation_start, variation_end))
                                
                                ## translocations
                                if z == 't':
                                    for each in ['t(15;17)', 't(6;9)', 't(9;22)', 't(8;21)',
                                                 't(4;14)', 't(11;14)', 't(14;16)', 't(16;20)']:
                                        if zz[0] == each[2:-1]:
                                            mutations[each] += cell_count
                                            offsets[each].append((variation_start, variation_end))                                  
                                            
                                ## del of p or q arms (also subsegmental deletetions)
                                elif z == 'del':
                                    for each in ['5','7','13']:
                                        if zz[0] == each and 'q' in zz[1]:
                                            mutations['del(' + each + 'q)'] += cell_count
                                            offsets['del(' + each + 'q)'].append((variation_start, variation_end))
                                    for each in ['1','17','12','13']:
                                        if zz[0] == each and 'p' in zz[1]:
                                            mutations['del(' + each + 'p)'] += cell_count
                                            offsets['del(' + each + 'p)'].append((variation_start, variation_end))
                                ## additions in p or q arms
                                elif z == 'add':
                                    for each in ['1']:
                                        if zz[0] == each and 'q' in zz[1]:
                                            mutations['del(' + each + 'q)'] += cell_count
                                            mutations['del(' + each + 'q)'].append((variation_start, variation_end))   
                                                                  
                                ## any mutation involving 17p, 21q, 20q, 11q, 9q, 3q  - we want to capture things like t(3;3) but NOT -13
                                ## also must make sure the 'q' is on the '11' arm - do not want to capture things like t(11;22)(p4;q20)
                                location = zz[0].split(';')
                                arm = zz[1].split(';')                               
                                    
                                if 'q' in zz[1] or 'i' in z:
                                    for each in ['3', '9', '11', '20', '21']:                                    
                                        if each in location:                                       
                                            if 'q' in arm[location.index(each)] or 'i' in z:                                          
                                                mutations[each+'q'] += cell_count
                                                offsets[each+'q'].append((variation_start,variation_end))
                                
                                if 'p' in zz[1] or 'i' in z:                                    
                                    if '17' in location and ((len(arm) > location.index('17') and 'p' in arm[location.index('17')]) or 'i' in z):                                           
                                        mutations['17p'] += cell_count
                                        offsets['17p'].append((variation_start,variation_end))

                    ## catch any other formatting abnormalities/parsing errors
                    except:
                        mutations[gb.WARNING] = 1
                        x[gb.WARNING] = 1                   
            ## there are no abnormalities - add up the "normal" cells
            else:              
                mutations[gb.NORMAL] += cell_count
                ## this is a normal XX or XY; string len is always 2
                offsets[gb.NORMAL].append((cell_offset,cell_offset + 2))
         ## catch trouble with cell counts etc       
        except:
            mutations[gb.WARNING] = 1            
            x[gb.WARNING] = 1      
           
    mutations[gb.MUTS] = len(abnormality_set)    
    mutations[gb.MONOS] = len(monosomy_set)
    mutations[gb.TRIS] = len(trisomy_set)
       
    for each_variation in mutations:
        confidence = 0.95
        if mutations[gb.WARNING] == 1:
            confidence = .6
        return_dictionary_list.append({gb.FIELD:each_variation, gb.VALUE:mutations[each_variation], \
                                       gb.CONFIDENCE:confidence, gb.VERSION:__version__, \
                                       gb.STARTSTOPS:[{gb.START:a[0], gb.STOP:a[1]} \
                                       for a in offsets[each_variation]], gb.TABLE:gb.CYTOGENETICS})
    return_dictionary_list.append(aml_swog_classification.get(mutations, abnormality_set, offsets, cell_list))
    return return_dictionary_list, return_errors
