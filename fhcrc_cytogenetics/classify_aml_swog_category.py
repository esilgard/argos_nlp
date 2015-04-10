#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import re,global_strings


'''author@esilgard'''
'''February 2015'''
__version__='classify_aml_swog_category1.0'


def get(cell_list,karyotype_string):
    karyo_offset=min([x['Offset'] for x in cell_list])
    '''
    take a parsed list of cells
        where each element within the cell group has a list of dictionaries of abnormalities
        as well as a cell count, a chromosome number, a warning, a chromosome, and 
        a cell order (just the order the cell line was listed in the report)
        
    return the same list with an appended swog label dictionary
    '''
    return_errors=[]
    return_dictionary_list=[{global_strings.NAME:"KaryotypeString",global_strings.VALUE:karyotype_string,global_strings.CONFIDENCE:1.0,
                            global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:karyo_offset,
                                                                                          global_strings.STOP:karyo_offset+len(karyotype_string)}]}]
    ## a dictionary of mutation types and their cell counts
    aml_swog_mutations=dict.fromkeys(['inv(16)','t(16;16)','del(16q)','t(8;21)','t(15;17)','t(18;21)','normal','+8','+6','-Y','del(12p)','-7','-5',
                                      '3q','9q','11q','17p','20q','21q','del(7q)','del(5q)','del(9q)','t(6;9)','t(9;22)',
                                      'monosomies','mutations','trisomies'],0)
    ## a dictionary of mutation types and their offsets - which will be stored as a list of tuples (start,stop)
    aml_swog_offsets={}
    for variation in aml_swog_mutations:
        aml_swog_offsets[variation]=[]
   
    # used to track unique mutations
    abnormality_set=set([])
    monosomy_set=set([])
    trisomy_set=set([])
##################################################################################################################################
  
    ## start by counting cells with each type of pertinent aberration   
    warning=False
    for x in cell_list:
        if x[global_strings.WARNING]: warning=True
        try:
            cell_count=int(x['CellCount'])
            cell_offset=x['Offset']
            if x[global_strings.ABNORMALITIES]:                
                for y in x[global_strings.ABNORMALITIES]:
                   
                    try:                        
                        for z,zz in y.items():
                            variation_string=z+'('+zz[0]+')'+zz[1]
                            if z=='-' or z=='+':
                                variation_string=z+zz[0]+zz[1]
                            #print 'VARIATION STRING',variation_string
                            variation_start=cell_offset+(karyotype_string[cell_offset:].find(variation_string))
                            #print variation_start
                            variation_end=variation_start+len(variation_string)
                            #print variation_end

                            #print '####',karyotype_string,'####',variation_string,'####',variation_start,'####',variation_end
                            abnormality_set.add(variation_string)                    
                            ## all trisomies
                            if z=='+':
                                trisomy_set.add(variation_string)
                                aml_swog_offsets['trisomies'].append((variation_start,variation_end))
                                for each in ['8','6']:
                                    if zz[0]==each:
                                        aml_swog_mutations['+'+each]+=cell_count
                                        aml_swog_offsets['+'+each].append((variation_start,variation_end))
                                
                            ## all monosomies                            
                            elif z=='-':
                                monosomy_set.add(variation_string)
                                aml_swog_offsets['monosomies'].append((variation_start,variation_end))
                               
                                for each in ['Y','7','5']:
                                    if zz[0]==each:
                                        aml_swog_mutations['-'+each]+=cell_count
                                        aml_swog_offsets['-'+each].append((variation_start,variation_end))
                            
                            ## all chromosome 16 abnormalities
                            if '16' in zz[0]:                                                 
                                if (z=='inv'):
                                    aml_swog_mutations['inv(16)']+=cell_count
                                    aml_swog_offsets['inv(16)'].append((variation_start,variation_end))
                                elif (z=='t' and '16;16' in zz[0]):
                                    aml_swog_mutations['t(16;16)']+=cell_count
                                    aml_swog_offsets['t(16;16)'].append((variation_start,variation_end))
                                elif (z=='del' and '16' in zz[0] and 'q'==zz[1]):
                                    aml_swog_mutations['del(16q)']+=cell_count
                                    aml_swog_offsets['del(16q)'].append((variation_start,variation_end))

                            ## translocations
                            if z=='t':
                                for each in ['15;17','t(6;9)','t(9;22)','t(8;21)']:
                                    if zz[0]==each:
                                        aml_swog_mutations[each]+=cell_count
                                        aml_swog_offsets[each].append((variation_start,variation_end))
                              
                                              
                            ## del 5q, del 7q, cel 12p
                            elif z=='del':
                                for each in ['5','7']:
                                    if zz[0]==each and 'q' in zz[1]:
                                        aml_swog_mutations['del('+each+'q)']+=cell_count
                                        aml_swog_offsets['del('+each+'q)'].append((variation_start,variation_end))
                               
                                if zz[0]=='12' and 'p' in zz[1]:
                                    aml_swog_mutations['del(12p)']+=cell_count
                                    aml_swog_offsets['del(12p)'].append((variation_start,variation_end))

                            ## any 17p, 21q, 20q, 11q, 9q, 3q  - we want to capture things like t(3;3) but NOT -13
                            if 'q' in zz[1]:
                                for each in ['3','9','11','20','21']:
                                    if each in zz[0].split(';'):
                                        aml_swog_mutations[each+'q']+=cell_count
                                        aml_swog_offsets[each+'q'].append((variation_start,variation_end))
                            elif 'p' in zz[1]:
                                if '17' in zz[0].split(';'):
                                    aml_swog_mutations['17p']+=cell_count
                                    aml_swog_offsets['17p'].append((variation_start,variation_end))

                                                                  
                           
                    ## catch any other formatting abnormalities/parsing errors
                    except:
                        x[global_strings.WARNING]='PARSING ERROR'

            ## there are no abnormalities - add up the "normal" cells
            else:
                aml_swog_mutations['normal']+=cell_count
                aml_swog_offsets['normal'].append((karyotype_string.find('4'),karyotype_string.find(']')))

         ## catch trouble with cell counts etc       
        except:
            warning=True; x[global_strings.WARNING]='PARSING ERROR'       
    print aml_swog_offsets
    aml_swog_mutations['mutations']=len(abnormality_set)    
    aml_swog_mutations['monosomies']=len(monosomy_set)
    aml_swog_mutations['trisomies']=len(trisomy_set)
    ## Assign SWOG risk categories based on important mutations
    ###############################################################################################################################################
    swog_dictionary={global_strings.NAME:global_strings.SWOG,global_strings.TABLE:global_strings.AML_CYTOGENETICS,global_strings.VALUE:global_strings.UNKNOWN,global_strings.CONFIDENCE:1.0,
                     global_strings.STARTSTOPS:[],global_strings.VERSION:__version__}
    ## not all swog risk categories return a list of character offsets, since some classifications rely on the ABSENCE of some given evidence
    
    # any kind of abnormality that is not specifically outlined in SWOG criteria -> MISCELLANEOUS                  
    if len(abnormality_set)>=1:
        swog_dictionary[global_strings.VALUE]=global_strings.MISCELLANEOUS

    # any INTERMEDIATE abnormality will trump the miscellaneous categorization
    if aml_swog_mutations['-Y']>=3:
        swog_dictionary[global_strings.VALUE] = global_strings.INTERMEDIATE
        swog_dictionary[global_strings.STARTSTOPS]=[[{global_strings.START:a[0]},{global_strings.STOP,a[1]}] for a in aml_swog_offsets['-Y']] 
    for each in ['+8','+6']:
        if aml_swog_mutations[each]>=2:
            swog_dictionary[global_strings.VALUE] = global_strings.INTERMEDIATE
            swog_dictionary[global_strings.STARTSTOPS]=[[{global_strings.START:a[0]},{global_strings.STOP,a[1]}] for a in aml_swog_offsets[each]]
    if aml_swog_mutations['del(12p)']:
        swog_dictionary[global_strings.VALUE] = global_strings.INTERMEDIATE
        swog_dictionary[global_strings.STARTSTOPS]=[[{global_strings.START:a[0]},{global_strings.STOP,a[1]}] for a in aml_swog_offsets[each]]        
                                                    
    # INTERMEDIATE due to NORMAL karyotype will trump miscellaneous
    if (len(abnormality_set)==0 and warning==False and aml_swog_mutations['normal']>=10) :
        swog_dictionary[global_strings.VALUE] = global_strings.INTERMEDIATE
        swog_dictionary[global_strings.STARTSTOPS]=[[{global_strings.START:a[0]},{global_strings.STOP,a[1]}] for a in aml_swog_offsets['normal']] 
    
    # UNFAVORABLE mutations will trump any previous risk categorization (misc or intermediate)
    if len(abnormality_set)>=3:
        swog_dictionary[global_strings.VALUE] = global_strings.UNFAVORABLE        
    for each in ['-7','-5']:                                                                                   
        if aml_swog_mutations[each]>=3:
            swog_dictionary[global_strings.VALUE] = global_strings.UNFAVORABLE
            swog_dictionary[global_strings.STARTSTOPS]=[[{global_strings.START:a[0]},{global_strings.STOP,a[1]}] for a in aml_swog_offsets[each]] 
    for each in ['3q','9q','11q','17p','20q','21q','del(7q)','del(5q)','t(6;9)','t(9;22)']:
        if aml_swog_mutations[each]:
            swog_dictionary[global_strings.VALUE] = global_strings.UNFAVORABLE
            swog_dictionary[global_strings.STARTSTOPS]=[[{global_strings.START:a[0]},{global_strings.STOP,a[1]}] for a in aml_swog_offsets[each]] 

    # FAVORABLE mutations will trump any previous risk categorization (misc, intermediate, or unfavorable)
    for each in ['inv(16)','t(16;16)','del(16q)','t(8;21)','t(15;17)']:
        if aml_swog_mutations[each]:
            swog_dictionary[global_strings.VALUE] = global_strings.FAVORABLE
            swog_dictionary[global_strings.STARTSTOPS]=[[{global_strings.START:a[0]},{global_strings.STOP,a[1]}] for a in aml_swog_offsets[each]]
            
    if aml_swog_mutations['t(18;21)'] and aml_swog_mutations['del(9q)']<1 and len(abnormality_set)<3:
        swog_dictionary[global_strings.VALUE] = global_strings.FAVORABLE
        swog_dictionary[global_strings.STARTSTOPS]=[[{global_strings.START:a[0]},{global_strings.STOP,a[1]}] for a in aml_swog_offsets['t(18;21)']] 

    #if the patient had fewer than 10 cells sampled, and no parsing errors encountering a cell count, then they are "INSUFFICIENT"
    try:
        if  sum([int(x[global_strings.CELL_COUNT]) for x in  cell_list])<10:                      
            swog_dictionary[global_strings.VALUE] = global_strings.INSUFFICIENT
    except:
        print 'cannot sum cells due to parsing error'  
    if warning==True:
        swog_dictionary[global_strings.VALUE] = global_strings.UNKNOWN
    
    return_dictionary_list.append(swog_dictionary)

##############################test return dictionary ########################################
    
    for each_variation in aml_swog_mutations:
       
        start_stops=set(aml_swog_offsets[each_variation])
        return_dictionary_list.append({global_strings.NAME:each_variation,global_strings.VALUE:aml_swog_mutations[each_variation],global_strings.CONFIDENCE:1.0,
                     global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:x[0],global_strings.STOP:x[1]} for x in start_stops]})
    return cell_list,return_dictionary_list,return_errors
