#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''last update October 2014'''
__version__='PathSide1.0'
import re

def get(dictionary):
    '''
    extract the PathSide (laterality)from normal cased text of the pathology report

    dictionary = {unique mrns:{unique accession_nums:{(section order, section heading, character onset of section):{row num/index:texts}}}}
    
    
    return a dictionary of
        {"name":"PathSide",
        "value":datetime object/or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"PathSide","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}

    standardizations={'rt':'Right','right':'Right','lt':'Left','left':'Left','bilateral':'Bilateral','midline':'Midline',
                      '1r':'Right','2r':'Right','3r':'Right','4r':'Right','5r':'Right','6r':'Right','7r':'Right','8r':'Right',
                      '9r':'Right','10r':'Right','11r':'Right','12r':'Right',
                      '1l':'Left','2l':'Left','3l':'Left','4l':'Left','5l':'Left','6l':'Left','7l':'Left','8l':'Left',
                      '9l':'Left','10l':'Left','11l':'Left','12l':'Left'}


    full_text=dictionary[(-1,'FullText',0)]
    side=set([])
    for section in sorted(dictionary):       
        onset=section[2]
        header=section[1]
        if 'CYTOLOGIC IMPRESSION' in header or 'DIAGNOSIS' in header or 'Specimen' in header or 'SPECIMEN' in header:            
            text='\n'.join(results.lower() for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])))
            
            text=re.sub('[.,:;\\\/\-\)\(]',' ',text) 
            match_list=['(rt|right)','([0-9]{1,2}[lr])','(lt|left)','(midline)','(bilateral)']
            for each_pattern in match_list:                       
                for each_match in re.finditer('.*( |^)'+each_pattern+'( |$).*',text,re.DOTALL):
                    side.add(standardizations[each_match.group(2)])
                    return_dictionary["startStops"].append({'startPosition':each_match.start(2)+onset,'stopPosition':each_match.end(2)+onset})                             
            
    return_dictionary['value']=';'.join(side)
    if ('Right' in side and 'Left' in side) or 'Bilateral' in side: return_dictionary['value']='Bilateral'
                
    return (return_dictionary,dict) 
