#ISCN Diagnosis:  46,XY[20]
#ISCN Diagnosis:  46,XY[7]
#ISCN Diagnosis:  46,XY[1]
#ISCN Diagnosis:  45,XY,-7,der(10)t(7;10)(p11;p11.1),del(10)(p11.2p13),der(13)t(7;13)(q22;p11.1)[4]/46,XY[36]
#ISCN Diagnosis:  47,XX,+8,inv(16)(p13q22)[19]/46,XX[1]
#ISCN Diagnosis:  47,XY,+8[20]
#ISCN Diagnosis:  No growth or insufficient growth
#ISCN Diagnosis:  46,XY,-7,+mar[5]/46,XY[15]
#ISCN Diagnosis:  48,XY,+1,del(5)(q13q33),del(12)(q24.1),del(16)(q21),add(17)(p13),+22[4]/48, sl,i(21)(q10)[8]/47,sl,i(21)(q10),-22[9]
#ISCN Diagnosis:  46,XX,t(6;9)(p23;q34)[3]/46,sl,t(6;15)(p23;q21)[5]/47,sdl,+13[10]/46,XX[2]
#ISCN Diagnosis:  46,XY[18]//46,XX[2]
#ISCN Diagnosis:  46,XY,del(20)(q11.2q13.1)[6]/46,XY[1]

#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import re


'''author@esilgard'''
'''December 2014'''
__version__='iscn_parser1.0'

def get(text):
    '''
    parse ISCN cytogenetic information from a short string of text containing only information
    about the genetic variation/karyotype in the ISCN format
    refer to http://www.cydas.org/Docs/ISCNAnalyser/Analysis.html for ISCN formatting guidelines
    return a normal cell count (this could be 0) and
    a list of abnormal cell types that include the number of cells and a dictionary of any genetic abnormalities    
    '''
    return_list=[]    
    seperate_cell_types=text.strip('"').split('/')
    cell_type_order=0
    
    for each_cell_type in seperate_cell_types:        
        d={}
        d['Abnormalities']=[]
        cell_count=re.match('.*\[([\d]+)\].*',each_cell_type)
        
        if cell_count:
            try:
                d['CellCount']=cell_count.group(1)
                each_cell_type=each_cell_type[:each_cell_type.find('['+cell_count.group(1))]                
            except:
                d['Warning']='PARSING ERROR'
            cell_description=each_cell_type.split(',')
            d['ChromosomeNumber']=cell_description[0].strip()
            d['Chromosome']=cell_description[1].strip()         
            d['CellTypeOrder']=cell_type_order
            d['Warning']=None
            

            ## if the length of the cell_description is greater than 2, then there are one or more abnormalities
            if len(cell_description)>2:
                d['Abnormalities']=cell_description[2:]
                if d['Chromosome'] == 'sl':
                    d['Chromosome']=return_list[0]['Chromosome']
                    d['Abnormalities']+=return_list[0]['Abnormalities']
                   
                elif d['Chromosome'] == 'sdl':
                    d['Chromosome']=return_list[1]['Chromosome']
                    d['Abnormalities']+=return_list[1]['Abnormalities']
                ## catch the specific cell line references like sdl1 or sdl2 ##
                elif 'sdl' in d['Chromosome']:
                    try:
                        d['Chromosome']=return_list[int(d['Chromosome'][-1])]['Chromosome']
                        d['Abnormalities']+=return_list[int(d['Chromosome'][-1])]['Abnormalities']
                    except:
                        d['Warning']='PARSING ERROR'
                        
                
                ## further parse abnormalities into dictionaries of type of mutation:chromosome specifics (number, location) ##
                for i in range(len(d['Abnormalities'])):                   
                    if type(d['Abnormalities'][i])==str:
                        loss_gain=re.match('([+-])([\d\w]+)',d['Abnormalities'][i])
                        abnormal_chromosome=re.match('(.*)[(]([\d;XY]+)[)](.*)',d['Abnormalities'][i])                       
                        if loss_gain:
                            d['Abnormalities'][i]={loss_gain.group(1):(loss_gain.group(2),None)}
                        elif abnormal_chromosome:
                            d['Abnormalities'][i]={abnormal_chromosome.group(1):(abnormal_chromosome.group(2),abnormal_chromosome.group(3))}
                        else:                          
                           d['Warming']='PARSING ERROR'                   
                               
        else:
            d['Warning']='PARSING ERROR'
       
        return_list.append(d)
        cell_type_order+=1
            
    return return_list,None,list
