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
   
    # chromosomes that can be generally coded with the six coding groups:
    # translocation(chr,arm), -chr, add(chr,arm), del(chr,arm), inv(chr,arm),
    # and dup or trp(chr,arm)
    all_chromosomes = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14', \
        '15','16','17','18','19','20','21','22','X','Y']
    coding_chr_group = ['1','2','3','4','5','6','7','8','9','10','11','12', \
        '17','18','19','20','X','Y']
    ## a dictionary of mutation types and their cell counts
    abnormalities = {}
    ## a dictionary of mutation types and their offsets - which will be stored as a list of tuples (start,stop)
    offsets = {}
    def add_to_d(abnormality, cell_count, variation_start, variation_end):
        '''
        helper function to put the abnormalities cell counts and the 
        start and stop positions of the abnormality string into the 
        abnormalities and offsets dictionaries
        '''
        if cell_count:
            # None cell_counts are binary values; only integers get added
            abnormalities[abnormality] = abnormalities.get(abnormality, 0) + cell_count
        offsets[abnormality] = offsets.get(abnormality, [])
        offsets[abnormality].append((variation_start, variation_end)) 
        
    # used to track unique abnormalities
    abnormality_set = set([])
    monosomy_set = set([])
    other_structural_abnormalities_set = set([])
    trisomy_set = set([])
    ###########################################################################
    abnormalities[gb.HYPER] = False; offsets[gb.HYPER] = []
    abnormalities[gb.HYPO] = False; offsets[gb.HYPO] = []
    abnormalities[gb.MONO_TYPE] = False; offsets[gb.MONO_TYPE] = []
    abnormalities[gb.CMPX_TYPE] = False; offsets[gb.CMPX_TYPE] = []
    abnormalities[gb.WARNING] = False; offsets[gb.WARNING] = []
    
    ## start by counting cells with each type of pertinent aberration      
    for x in cell_list:         
        if x[gb.WARNING]:
            abnormalities[gb.WARNING] = True            
        try:
            cell_count = x[gb.CELL_COUNT]           
            cell_offset = x['Offset']
            ## NOTE - this only gets the lower limit of cells in cases of "43-47"
            chromosome_number = int(x['ChromosomeNumber'][:2])
            ## hyperploidy and hypoploidy - ASK MIN ABOUT THIS LOGIC
            if chromosome_number < 45: # and cell_count >= clone_minimum: 
                abnormalities[gb.HYPO] = True
                add_to_d(gb.HYPO, None, cell_offset, cell_offset+2)
            if chromosome_number > 47: # and cell_count >= clone_minimum:
                abnormalities[gb.HYPER] = True
                add_to_d(gb.HYPER, None, cell_offset, cell_offset+2)

            if x[gb.ABNORMALITIES]:               
                for y in x[gb.ABNORMALITIES]:
                    try:  
                        for z, zz in y.items():                            
                            variation_string = z + zz[0] + zz[1]
                            stripped_chr = zz[0].strip('(').strip(')')
                            if cell_count >= 2: 
                                variation_start = cell_offset + \
                                (karyotype_string[cell_offset-karyo_offset:].find(variation_string))
                                variation_end = variation_start + len(variation_string)  
                                add_to_d(gb.MUTS, None, variation_start, variation_end)
                                ## all trisomies
                                if z == '+':                                                             
                                    abnormality_set.add(variation_string) 
                                    try:
                                        # only add in "full" trisomies
                                        int(stripped_chr)
                                        trisomy_set.add(variation_string)
                                        add_to_d(gb.TRIS, None, variation_start, variation_end)
                                    except:
                                        pass                                    
                                    for each in all_chromosomes:
                                        if stripped_chr == each: 
                                            add_to_d('+' + each, cell_count, variation_start, variation_end)
                                ## all monosomies                            
                                elif z == '-' and cell_count >= 3:                                    
                                    # track only autosomal monosomies for 
                                    # monosomal karyotype classification
                                    if stripped_chr not in ['X','Y']:
                                        monosomy_set.add(variation_string)
                                    abnormality_set.add(variation_string)
                                    add_to_d(gb.MONOS, None, variation_start, variation_end)
                                    for each in all_chromosomes:
                                        if stripped_chr == each:   
                                            add_to_d('-' + each, cell_count, variation_start, variation_end)
                                ## all other abnormalities do not have a cell count minimum
                                else:
                                    abnormality_set.add(variation_string) 
                                    # track other structural abnormalities for 
                                    # monosomal karyotype classificaiton
                                    if z not in ['r','mar','add']:
                                        other_structural_abnormalities_set.add(variation_string)                                        
                                ## all chromosome 16 abnormalities
                                #if '16' in stripped_chr:                                                 
                                    #if (z == 'inv'):
                                    #    add_to_d('inv(16)', cell_count, variation_start, variation_end)
                                    #elif (z == 't' and '16;16' in zz[0]):
                                    #    add_to_d('t(16;16)', cell_count, variation_start, variation_end)
                                    #elif (z == 'del' and 'q' == zz[1]):
                                    #    add_to_d('del(16q)', cell_count, variation_start, variation_end)
                                
                                ## specific translocations
                                if z == 't':
                                    for each in ['t(15;17)', 't(6;9)', 't(9;22)', 't(8;21)', 't(16;16)'
                                                 't(4;14)', 't(11;14)', 't(14;16)', 't(16;20)', 't(3;3)']:
                                        if stripped_chr == each[2:-1]:
                                            add_to_d(each, cell_count, variation_start, variation_end)
                                    # general translocations involving p or q arms
                                    for each in coding_chr_group:
                                        chr_list = stripped_chr.split(';')
                                        if each in chr_list:
                                            location = chr_list.index(each)
                                            for arm in ['p','q']:
                                                if arm in zz[1].split(';')[location]:
                                                    add_to_d('translocation(' + each + arm + ')', cell_count, variation_start, variation_end)
                                # dicentric chromosome
                                elif 'dic' in z:
                                    for each in coding_chr_group:
                                        chr_list = stripped_chr.split(';')                                        
                                        if each in chr_list:
                                            location = chr_list.index(each)
                                            for arm in ['p','q']:
                                                if arm in zz[1].split(';')[location]:
                                                    add_to_d('translocation(' + each + arm + ')', cell_count, variation_start, variation_end)
                                # derivative chromosomes 
                                elif 'der' in z:
                                    print z, zz
                                    for each in coding_chr_group:
                                        chr_list = stripped_chr.split(';')                                        
                                        # if the der involves another abnormality type
                                        # this won't necessarily split two chromosomes cleanly 
                                        # e.g.  ['12)t(12','15']
                                        for chr_part in chr_list:
                                            if each in chr_part:
                                                location = chr_list.index(chr_part)
                                                #print each, chr_list, location, zz[1].split(';')
                                                # a derivitive from q10 on will mean a full loss of the p arm
                                                if 'q10' in zz[1].split(';')[location]:
                                                    add_to_d('del(' + each + 'p)', cell_count, variation_start, variation_end)
                                                else:
                                                    for arm in ['p','q']:
                                                        if arm in  zz[1].split(';')[location]:
                                                            add_to_d('translocation(' + each + arm + ')', cell_count, variation_start, variation_end)
                                ## deletion of arms
                                elif 'del' in z:
                                    for each in all_chromosomes:  
                                        for arm in ['p','q']:
                                            if stripped_chr == each and arm in zz[1]:
                                                add_to_d('del(' + each + arm + ')', cell_count, variation_start, variation_end)                               
                               
                                ## isochromes - implicit deletion of p or q arms
                                elif z == 'i' or z == '?i':                                    
                                    for each in all_chromosomes:                                    
                                        if stripped_chr == each and 'p10' in zz[1]:
                                            add_to_d('del(' + each + 'q)', cell_count, variation_start, variation_end)
                                        #for each in ['1','17','12','13']:
                                        if stripped_chr == each and 'q10' in zz[1]:                                           
                                            add_to_d('del(' + each + 'p)', cell_count, variation_start, variation_end)
                                             
                                ## additions in p and q arms
                                elif 'add' in z:
                                    for each in all_chromosomes:
                                        for arm in ['q','p']:
                                            if stripped_chr == each and arm in zz[1]:       
                                                add_to_d('add(' + each + arm + ')', cell_count, variation_start, variation_end)
                                   
                                ## duplicataes, triplicates, and inversions and insertions
                                elif z in ['dup','trp','inv','ins']:  
                                    for each in coding_chr_group:
                                        for arm in ['q','p']:
                                            if stripped_chr == each and arm in zz[1]:
                                                if z == 'ins': z = 'translocation'
                                                add_to_d(z + '('+ each + arm + ')', cell_count, variation_start, variation_end)
                               
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
                                                add_to_d(each + 'q', cell_count, variation_start, variation_end)
                                    
                                
                    ## catch any other formatting abnormalities/parsing errors
                    except:
                        abnormalities[gb.WARNING] = True
                        x[gb.WARNING] = True
                        print 'PARSING ERROR?', karyotype_string
                        
            ## there are no abnormalities - add up the "normal" cells
            elif x['Chromosome'] in ['XX','XY']:
                add_to_d(gb.NORMAL, cell_count, cell_offset, cell_offset + 2)
            else:
                ## other sec chromosome abnormalities
                add_to_d(gb.SEX_CHRM_ABN, cell_count, cell_offset, cell_offset + len(x['Chromosome']))

         ## catch trouble with cell counts etc       
        except:
            abnormalities[gb.WARNING] = True            
            x[gb.WARNING] = True   
                      
    abnormalities[gb.MUTS] = len(abnormality_set)    
    abnormalities[gb.MONOS] = len(monosomy_set)
    abnormalities[gb.TRIS] = len(trisomy_set)
    ## complex and monosomal karyotype classifications
    ## need to add in char offset tracking
    if len(abnormality_set) > 2:
        abnormalities[gb.CMPX_TYPE] = True
    if len(monosomy_set) > 1 or (len(monosomy_set) == 1 and \
        len(other_structural_abnormalities_set)) > 0:
        abnormalities[gb.MONO_TYPE] = True
    #append all abnormality info to return_list
    for each_variation in abnormalities:
        confidence = 0.95
        if abnormalities[gb.WARNING] == True:
            confidence = .6
        offsets[each_variation] = offsets.get(each_variation, [])
        return_dictionary_list.append({gb.NAME:each_variation, \
            gb.VALUE:abnormalities[each_variation], gb.CONFIDENCE:confidence, \
            gb.VERSION:__version__, gb.STARTSTOPS:[{gb.START:a[0], gb.STOP:a[1]} \
             for a in offsets[each_variation] ], gb.TABLE:gb.CYTOGENETICS})
   
    
    return_dictionary_list.append(aml_swog_classification.get(abnormalities, abnormality_set, offsets, cell_list))
    #return_dictionary_list.append(eln_classification.get(abnormalities, abnormality_set, offsets))
    return return_dictionary_list, return_errors
