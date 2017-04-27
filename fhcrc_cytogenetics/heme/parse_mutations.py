'''author@esilgard'''
#
# Copyright (c) 2015-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

import global_strings as gb
import aml_swog_classification
import eln_classification

__version__='cytogenetics_mutation_parser1.0'

def get(cell_list, karyotype_string, karyo_offset):

    '''
        take a parsed list of cells, where each element within the cell group 
        has a list of dictionaries of abnormalities as well as a cell count, 
        a chromosome number, a warning flag, a chromosome, and a cell order 
        (just the order the cell line was listed in the report)        
        return the same list with an appended swog label dictionary
    '''
    return_errors = []
    return_dictionary_list = [{gb.NAME:gb.KARYOTYPE_STRING, 
        gb.VALUE:karyotype_string, gb.CONFIDENCE:1.0, gb.VERSION:__version__, 
        gb.STARTSTOPS:[{gb.START:karyo_offset, gb.STOP:karyo_offset + 
        len(karyotype_string)}], gb.TABLE:gb.CYTOGENETICS}]
   
   ## a dictionary of mutation types and their cell counts
    mutations=dict.fromkeys(['inv(16)', 't(16;16)', 'del(16q)', 't(8;21)', 
        't(15;17)', 't(8;21)', gb.NORMAL, '+8', '+6', '-Y', 'del(12p)', '-7',
        '-5', '3q', '9q', '11q', '20q', '21q', 'del(7q)', '17p', 'del(5q)', 
        'del(9q)', 't(16;20)', 't(14;16)', 't(11;14)', 't(4;14)', 'del(17p)', 
        'del(1p)', 'add(1q)', 't(6;9)', 't(9;22)','del(13p)', 'del(13q)', 
        '-13', '-12','-17', 'add(12p)', 'add(17p)', 'inv(12p)', 'inv(17p)', 
        'dup(12p)', 'dup(17p)', 'trp(12p)', 'trp(17p)', 'translocation(12p)',
        'translocation(17p)', gb.MONOS, gb.MUTS, gb.TRIS], 0)
    
    ## a dictionary of mutation types and their offsets - which will be stored as a list of tuples (start,stop)
    offsets = {}
    for variation in mutations:
        offsets[variation] = []
   
    # used to track unique mutations
    abnormality_set = set([])
    monosomy_set = set([])
    other_structural_abnormalities_set = set([])
    trisomy_set = set([])
    ###########################################################################
    mutations[gb.HYPER] = False; offsets[gb.HYPER] = []
    mutations[gb.HYPO] = False; offsets[gb.HYPO] = []
    mutations[gb.MONO_TYPE] = False; offsets[gb.MONO_TYPE] = []
    mutations[gb.CMPX_TYPE] = False; offsets[gb.CMPX_TYPE] = []
    mutations[gb.WARNING] = False; offsets[gb.WARNING] = []
    
    ## start by counting cells with each type of pertinent aberration      
    for x in cell_list:         
        if x[gb.WARNING]:
            mutations[gb.WARNING] = True            
        try:
            cell_count = x[gb.CELL_COUNT]           
            cell_offset = x['Offset']
            ## NOTE - this only gets the lower limit of cells in cases of "43-47"
            chromosome_number = int(x['ChromosomeNumber'][:2])
            ## hyperploidy and hypoploidy - ASK MIN ABOUT THIS LOGIC
            if chromosome_number < 45: # and cell_count >= clone_minimum: 
                offsets[gb.HYPO].append((cell_offset,cell_offset+2))
                mutations[gb.HYPO] = True
            if chromosome_number > 47: # and cell_count >= clone_minimum:
                offsets[gb.HYPER].append((cell_offset,cell_offset+2))
                mutations[gb.HYPER] = True
                 
            # If not
            if x[gb.ABNORMALITIES]:
               
                for y in x[gb.ABNORMALITIES]:
                    try:  
                        for z, zz in y.items():                            
                            variation_string = z + zz[0] + zz[1]
                            stripped_chr = zz[0].strip('(').strip(')')
                            if cell_count >= 2:                                
                                #if z == '-' or z == '+':
                                #    variation_string = z + zz[0] + zz[1]                            
                                variation_start = cell_offset + \
                                (karyotype_string[cell_offset-karyo_offset:].find(variation_string))
                                variation_end = variation_start + len(variation_string)  
                                offsets[gb.MUTS].append((variation_start,variation_end))
                                ## all trisomies
                                if z == '+':                                                             
                                    abnormality_set.add(variation_string) 
                                    try:
                                        # only add in "full" trisomies
                                        int(stripped_chr)
                                        offsets[gb.TRIS].append((variation_start,variation_end))
                                        trisomy_set.add(variation_string)
                                    except:
                                        pass                                    
                                    for each in ['8', '6']:
                                        if stripped_chr == each:
                                            mutations['+' + each] += cell_count
                                            offsets['+' + each].append((variation_start, variation_end))                                    
                                ## all monosomies                            
                                elif z == '-' and cell_count >= 3:                                    
                                    # track only autosomal monosomies for 
                                    # monosomal karyotype classification
                                    if stripped_chr not in ['X','Y']:
                                        monosomy_set.add(variation_string)
                                    abnormality_set.add(variation_string)                                    
                                    offsets[gb.MONOS].append((variation_start, variation_end))
                                   
                                    for each in ['Y', '7', '5', '12', '13', '17']:
                                        if stripped_chr == each:                                                
                                            mutations['-'+each] += cell_count
                                            offsets['-'+each].append((variation_start, variation_end))
                                ## all other abnormalities do not have a cell count minimum
                                else:
                                    abnormality_set.add(variation_string) 
                                    # track other structural abnormalities for 
                                    # monosomal karyotype classificaiton
                                    if z not in ['r','mar','add']:
                                        other_structural_abnormalities_set.add(variation_string)                                        
                                ## all chromosome 16 abnormalities
                                if '16' in stripped_chr:                                                 
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
                                        if stripped_chr == each[2:-1]:
                                            mutations[each] += cell_count
                                            offsets[each].append((variation_start, variation_end)) 
                                    for each in ['12','17']:
                                        chr_list = stripped_chr.split(';')
                                        if each in chr_list:
                                            location = chr_list.index(each)
                                            if 'p' in zz[1].split(';')[location]:
                                                mutations['translocation(' + each + 'p)'] += cell_count
                                                offsets['translocation(' + each + 'p)'].append((variation_start, variation_end))
                                ## dic variations for 12p and 17p   
                                elif 'dic' in z:
                                    for each in ['12','17']:
                                        chr_list = stripped_chr.split(';')
                                        if each in chr_list:
                                            location = chr_list.index(each)
                                            if 'p' in zz[1].split(';')[location]:
                                                mutations['translocation(' + each + 'p)'] += cell_count
                                                offsets['translocation(' + each + 'p)'].append((variation_start, variation_end))
                                ## der 12 and 17 derivations
                                elif 'der' in z:
                                    for each in ['12','17']:
                                        chr_list = stripped_chr.split(';')                                        
                                        # if the der involves another abnormality type
                                        # this won't necessarily split two chromosomes cleanly 
                                        # e.g.  ['12)t(12','15']
                                        for chr_part in chr_list:
                                            if each in chr_part:
                                                location = chr_list.index(chr_part)
                                                # a derivitive from q10 on will mean a full loss of the p arm
                                                if 'q10' in zz[1].split(';')[location]:
                                                    mutations['del(' + each + 'p)'] += cell_count
                                                    offsets['del(' + each + 'p)'].append((variation_start, variation_end))
                                                else:
                                                    mutations['translocation(' + each + 'p)'] += cell_count
                                                    offsets['translocation(' + each + 'p)'].append((variation_start, variation_end))
                                ## explicit del of p or q arms (also subsegmental deletetions)
                                elif 'del' in 'z':
                                    for each in ['5','7','13']:                                    
                                        if stripped_chr == each and 'q' in zz[1]:
                                            mutations['del(' + each + 'q)'] += cell_count
                                            offsets['del(' + each + 'q)'].append((variation_start, variation_end))                                        
                                    for each in ['1','17','12','13']:
                                        if stripped_chr == each and 'p' in zz[1]:
                                            mutations['del(' + each + 'p)'] += cell_count
                                            offsets['del(' + each + 'p)'].append((variation_start, variation_end))
                               
                                ## implicit del of p or q arms from isochromes
                                elif z == 'i' or z == '?i':                                    
                                    for each in ['5','7','13']:                                    
                                        if stripped_chr == each and 'p10' in zz[1]:
                                            mutations['del(' + each + 'q)'] += cell_count
                                            offsets['del(' + each + 'q)'].append((variation_start, variation_end))                                        
                                    for each in ['1','17','12','13']:
                                        if stripped_chr == each and 'q10' in zz[1]:                                           
                                            mutations['del(' + each + 'p)'] += cell_count
                                            offsets['del(' + each + 'p)'].append((variation_start, variation_end))
                                             
                                ## additions in p and q arms
                                elif 'add' in z:
                                    for each in ['1']:
                                        if stripped_chr == each and 'q' in zz[1]:
                                            mutations['add(' + each + 'q)'] += cell_count
                                            mutations['add(' + each + 'q)'].append((variation_start, variation_end))
                                    for each in ['12','17']:
                                        if stripped_chr == each and 'p' in zz[1]:
                                            mutations['add(' + each + 'p)'] += cell_count
                                            mutations['add(' + each + 'p)'].append((variation_start, variation_end)) 
                                ## duplicataes, triplicates, and inversions in p arms of 12 and 17
                                elif z in ['dup','trp','inv','ins']:  
                                    for each in ['12','17']:
                                        if stripped_chr == each and 'p' in zz[1]:
                                            if z == 'ins': z = 'translocation'
                                            mutations[z + '(' + each + 'p)'] += cell_count
                                            mutations[z + '(' + each + 'p)'].append((variation_start, variation_end)) 
                               
                                ## NOTE _ THIS SHOULD BE CHANGED TO MIN'S ENCODINGS FOR SIMPLICITY and NOT OVERLAPPING TYPES                                 
                                ## any mutation involving 21q, 20q, 11q, 9q, 3q  - we want to capture things like t(3;3) but NOT -13
                                ## also must make sure the 'q' is on the '11' arm - do not want to capture things like t(11;22)(p4;q20)
                                '''
                                come back to this - we should switch to mutually exclusive types of abnormalities - this double captures/counts some
                                '''
                                location = stripped_chr.split(';')
                                arm = zz[1].split(';')                               
                                    
                                if 'q' in zz[1] or 'i' in z:
                                    for each in ['3', '9', '11', '20', '21']:                                    
                                        if each in location:                                       
                                            if 'q' in arm[location.index(each)] or 'i' in z:                                          
                                                mutations[each+'q'] += cell_count
                                                offsets[each+'q'].append((variation_start,variation_end))                    
                                
                    ## catch any other formatting abnormalities/parsing errors
                    except:
                        mutations[gb.WARNING] = True
                        x[gb.WARNING] = True                  
            ## there are no abnormalities - add up the "normal" cells
            elif x['Chromosome'] in ['XX','XY']:
                mutations[gb.NORMAL] += cell_count
                ## this is a normal XX or XY; string len is always 2
                offsets[gb.NORMAL].append((cell_offset,cell_offset + 2))
            else:
                ## other sec chromosome abnormalities
                mutations[gb.SEX_CHRM_ABN] += cell_count
                ## this is a normal XX or XY; string len is always 2
                offsets[gb.SEX_CHRM_ABN].append((cell_offset,cell_offset + len(x['Chromosome'])))
         ## catch trouble with cell counts etc       
        except:
            mutations[gb.WARNING] = True            
            x[gb.WARNING] = True   
           
    mutations[gb.MUTS] = len(abnormality_set)    
    mutations[gb.MONOS] = len(monosomy_set)
    mutations[gb.TRIS] = len(trisomy_set)
    ## complex and monosomal karyotype classifications
    ## need to add in char offset tracking
    if len(abnormality_set) > 2:
        mutations[gb.CMPX_TYPE] = True
    if len(monosomy_set) > 1 or (len(monosomy_set) == 1 and \
        len(other_structural_abnormalities_set)) > 0:
        mutations[gb.MONO_TYPE] = True
    #append all abnormality info to return_list
    for each_variation in mutations:
        confidence = 0.95
        if mutations[gb.WARNING] == True:
            confidence = .6
        return_dictionary_list.append({gb.NAME:each_variation, \
            gb.VALUE:mutations[each_variation], gb.CONFIDENCE:confidence, \
            gb.VERSION:__version__, gb.STARTSTOPS:[{gb.START:a[0], gb.STOP:a[1]} \
            for a in offsets[each_variation]], gb.TABLE:gb.CYTOGENETICS})
   
    return_dictionary_list.append(aml_swog_classification.get(mutations, abnormality_set, offsets, cell_list))
    #return_dictionary_list.append(eln_classification.get(mutations, abnormality_set, offsets))
    return return_dictionary_list, return_errors
