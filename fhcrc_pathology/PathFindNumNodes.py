#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='PathFindNumNodes1.0'
import re
import global_strings
def get(section,text):
   
    '''
    extract the PathFindNumNodes (number of lymph nodes examined) from the normal cased text of the pathology report   
    
    return a dictionary of of number, character offsets, etc
    '''
    
    PathFindumNodes={global_strings.NAME:"PathFindNumNodes",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,
                       global_strings.STARTSTOPS:[], global_strings.TABLE:global_strings.NODE_TABLE}
    PathFindPosNodes={global_strings.NAME:"PathFindPosNodes",global_strings.VALUE:None,global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,
                       global_strings.STARTSTOPS:[], global_strings.TABLE:global_strings.NODE_TABLE}

    number_words={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,
                  'thirteen':13,'fourteen':14,'fifteen':15}
    number_digits={'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'11':11,'12':12,'13':13,'14':14,'15':15}
    combo=dict(number_words,**number_digits)    
    number_list=sorted([a[0] for a in combo.items()], key=lambda x: combo[x],reverse=True)
    
    pos_total_patterns=['.*[(](lymph|node|[\d]{1,2}[rl]).{,15}('+'|'.join(number_list)+')[ ]*([/]|of|out of)[ ]*('+'|'.join(number_list)+').*',
                        '.*[(]('+'|'.join(number_list)+')[ ]*([/]|of|out of)[ ]*('+'|'.join(number_list)+').{,15}(lymph|node|[\d]{1,2}[rl]).*']

    just_total_patterns=['.*(lymph|node|[\d]{1,2}[rl]).{,15}('+'|'.join(number_words)+').*',
                        '.*('+'|'.join(number_words)+').{,15}(lymph|node|[\d]{1,2}[rl]).*']
    for each in pos_total_patterns:
        pos= re.match(each,text)
        if pos:
            pass
            #print 'NUM POS/NUM NODES ',pos.group(1),pos.group(2),pos.group(3)
    for each in just_total_patterns:
        num= re.match(each,text)
        if num:
            pass
            #print text
            #print 'JUST NUM NODES ',num.group(1),num.group(2)
    
    return None,None
