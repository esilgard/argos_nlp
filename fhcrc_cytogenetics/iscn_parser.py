'''author@esilgard'''
#
# Copyright (c) 2015-2017 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import re
import global_strings as gb
__version__ = 'iscn_parser1.0'

def get(karyotype_string, karyo_offset):
    '''
    parse ISCN cytogenetic information from a short string of text containing
    information about the genetic variation/karyotype in the ISCN format
    ISCN formatting guidelines: http://www.cydas.org/Docs/ISCNAnalyser/Analysis.html
    list of cell types includes number of cells and dictionary of genetic abnormalities
    '''
    return_list = []
    seperate_cell_types = karyotype_string.split('/')
    cell_type_order = 0

    for each_cell_type in seperate_cell_types:    
        d = {}
        #cell_type_order makes up for the character loss of the '/'
        d[gb.OFFSET] = karyo_offset + karyotype_string.find(each_cell_type) + cell_type_order
        d[gb.ABNORMALITIES] = []
        d[gb.POLY] = False
        d[gb.CELL_ORDER] = cell_type_order
        cell_count = re.match(r'.*(\[c?C?p?P?([\d ]+)\]).*', each_cell_type)
        if cell_count:
            try:
                # strip off any trailing whitespace or "compositite" and cast as int
                # eventually we'll want to represent compisite counts as "no more than N"
                d[gb.CELL_COUNT] = int(cell_count.group(2).strip('cp').strip())
                each_cell_type = each_cell_type[:each_cell_type.find(cell_count.group(1))]
            ## catches error when there is no cell count
            except ValueError:
                d[gb.WARNING] = True                
            
            # cell description list - order is important to refer back to
            # previous cell lines
            cell_description = each_cell_type.split(',')
            
            try:
                d[gb.CHROMOSOME_NUM] = cell_description[0].strip()
                try:
                    if re.search(r'[\d][nN]', cell_description[1]):
                        ## SHOULD add these copies into total cell counts - ASK MIN
                        ## for NOW - just flag warning                        
                        d[gb.POLY] = True
                        d[gb.CHROMOSOME_NUM] += cell_description[1]
                        cell_description = cell_description[1:]                    
                    d[gb.CHROMOSOME] = cell_description[1].strip()
                    d[gb.WARNING] = False

                except:
                    # catches error when there are no sex chromosomes
                    d[gb.WARNING] = True
            except ValueError:
                ## catches error when there is no chromosome type number and type
                d[gb.WARNING] = True
            ## if the length of the cell_description is greater than 2, there are abnormalities
            if len(cell_description) > 2:
                d[gb.ABNORMALITIES] = cell_description[2:]
                if (d[gb.CHROMOSOME] == 'sl' or 'idem' in d[gb.CHROMOSOME]) \
                and len(seperate_cell_types) > 1:
                    try:
                        d[gb.CHROMOSOME] = return_list[0][gb.CHROMOSOME]
                    except ValueError:
                        d[gb.WARNING] = True
                        d[gb.CHROMOSOME] = 'UNK'
                    d[gb.ABNORMALITIES] += return_list[0][gb.ABNORMALITIES]

                ## catch this typo - where the XX and XY is included in the idem/sl reference
                ## exclude the reference itself from the list of abnormalities
                elif (d[gb.ABNORMALITIES][0] == 'sl' or 'idem' in d[gb.ABNORMALITIES][0])\
                and len(seperate_cell_types) > 1:
                    d[gb.ABNORMALITIES] = return_list[0][gb.ABNORMALITIES] + d[gb.ABNORMALITIES][1:]
                ## when sdl is used to refer back to sl
                elif d[gb.CHROMOSOME] == 'sdl' and len(seperate_cell_types) > 2:
                    d[gb.CHROMOSOME] = return_list[1][gb.CHROMOSOME]
                    d[gb.ABNORMALITIES] += return_list[1][gb.ABNORMALITIES]
                ## catch the specific cell line references like sdl1 or sdl2 ##
                elif 'sdl' in d[gb.CHROMOSOME]:
                    try:
                        d[gb.CHROMOSOME] = return_list[cell_type_order-1][gb.CHROMOSOME]
                        d[gb.ABNORMALITIES] = return_list[cell_type_order-1][gb.ABNORMALITIES]\
                        + d[gb.ABNORMALITIES]
                    except ValueError:                        
                        d[gb.WARNING] = True

            ## parse abnormalities into dictionaries of type of abnormality: (num/further abn type, arm loc)
            for i in range(len(d[gb.ABNORMALITIES])):                
                if isinstance(d[gb.ABNORMALITIES][i], str):
                    # first group is the general type of abnormality 
                    # second group is the affected chromosome (sometimes involving a more complicated type of abnormality)                    
                    loss_gain = re.match(r'[ ]?([\+\-\?a-zA-Z ]+)[ ]?([\(]?[\d\w\~\?\(\)\-\.\;]+[\)]?)', d[gb.ABNORMALITIES][i])
                    # not doing anything with this match yet
                    copy = re.match('[xX][\d]', d[gb.ABNORMALITIES][i][-2:])                    
                    if loss_gain:   
                        # this group is the p and or q arm location (if there is one)
                        arm_location = re.match('.*([\(][pq][pq;\?\d\.]+[\)])',loss_gain.group(0))
                        if arm_location:
                            chromosomes = loss_gain.group(2)[:loss_gain.group(2).find(arm_location.group(1))]
                            d[gb.ABNORMALITIES][i] = {loss_gain.group(1): (chromosomes, arm_location.group(1))}                            
                        else:
                            d[gb.ABNORMALITIES][i] = {loss_gain.group(1): (loss_gain.group(2), '')}                       
                    else:
                        ## case where there's no type of abnormality (eg del, +)
                        abnormal_chromosome = \
                        re.match(r'[ ]?([\d\-\~?\ ]*)[ ]?(mar|r|dmin|pstk+|inc)[ ]?',\
                        d[gb.ABNORMALITIES][i])
                        ## record presense of other, unrecognized abnormality
                        if abnormal_chromosome:
                            d[gb.ABNORMALITIES][i] = {'other aberration': \
                            (abnormal_chromosome.group(1), abnormal_chromosome.group(2))}
                        else:                            
                            d[gb.WARNING] = True
        
        ## warning flag for error finding cell count
        else:
            d[gb.WARNING] = True
        return_list.append(d)
        cell_type_order += 1
    return return_list, None, list


if __name__ == '__main__':
    get('39-44,XY,-5,add(5)(q11.2),add(11)(p11.2),?del(13)(qq12q14),-15,add(15)(p11.2),der(17)t(15;17)(q11.2; p11.2),-19,-21,i(21)(q10),-22,+1~3mar,1dmin,inc[cp6]/46,XY[14]', 0)