#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''
    written October 2014, updates:
    December 2014 - added table_name to return dictionary - moved standardizations from celtral script into a disease specific dictionary
'''
__version__='PathSide1.0'
import re
import global_strings
def get(disease_group,dictionary):
   
    '''
    extract the PathSide (laterality)from normal cased text of the pathology report
    dictionary = {unique mrns:{unique accession_nums:{(section order, section heading, character onset of section):{row num/index:texts}}}}
    return a dictionary for laterality/side both for individual specimens (PathFindSide) and over all report (PathSide)
    '''
    
    standardizations={'rt':'Right','right':'Right','lt':'Left','left':'Left','bilateral':'Bilateral','midline':'Midline',
                      '1r':'Right','2r':'Right','3r':'Right','4r':'Right','5r':'Right','6r':'Right','7r':'Right','8r':'Right',
                      '9r':'Right','10r':'Right','11r':'Right','12r':'Right',
                      '1l':'Left','2l':'Left','3l':'Left','4l':'Left','5l':'Left','6l':'Left','7l':'Left','8l':'Left',
                      '9l':'Left','10l':'Left','11l':'Left','12l':'Left',
                      '1 r':'Right','2 r':'Right','3 r':'Right','4 r':'Right','5 r':'Right','6 r':'Right','7 r':'Right','8 r':'Right',
                      '9 r':'Right','10 r':'Right','11 r':'Right','12 r':'Right',
                      '1 l':'Left','2 l':'Left','3 l':'Left','4 l':'Left','5 l':'Left','6 l':'Left','7 l':'Left','8 l':'Left',
                      '9 l':'Left','10 l':'Left','11 l':'Left','12 l':'Left'}
    match_list=['(rt|right)','([0-9]{1,2}[ ]?[lr])','(lt|left)','(midline)','(bilateral)'] 

    def get_side(specimen):
       
        specimen_side_list=[]
        specimen_start_stops_list=[]       
        for section in dictionary:            
            section_specimen=section[3]            
            line_onset=section[2]
            header=section[1]            
            if section_specimen is not None and specimen in section_specimen and ('SPECIMEN' in header or 'DESCRIPTION' in header):
                text= dictionary[section].items()[0][1]                              
                ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                ## these can contain confusing general statements about the cancer and/or patients in general ##
                if re.search('[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',text):pass               
                else:
                    text=text.lower()
                    text=re.sub('[.,:;\\\/\-\'\"]',' ',text)
                    for each_pattern in match_list:                            
                        for each_match in re.finditer('.*( |^)'+each_pattern+'( |$).*',text,re.DOTALL):                           
                            if standardizations[each_match.group(2)] not in specimen_side_list:                                    
                                specimen_side_list.append(standardizations[each_match.group(2)])                                    
                            specimen_start_stops_list.append({global_strings.START:each_match.start(2)+line_onset,global_strings.STOP:each_match.end(2)+line_onset})
                       
        if specimen_side_list:
            if type(specimen_side_list)==str:   specimen_side_list=[specimen_side_list]
            if ('Right' in specimen_side_list and 'Left' in specimen_side_list) or 'Bilateral' in specimen_side_list: specimen_side_list=['Bilateral']           
            return {global_strings.NAME:"PathFindSide",global_strings.KEY:specimen,global_strings.TABLE:global_strings.FINDING_TABLE,global_strings.VALUE:';'.join(set(specimen_side_list)),
                    global_strings.CONFIDENCE:("%.2f" % .85), global_strings.VERSION:__version__, global_strings.STARTSTOPS:specimen_start_stops_list}
           
        else:           
            return None
##############################################################################################
    full_text=dictionary[(-1,'FullText',0,None)]
    return_dictionary_list=[]    
    side_list=[]
    start_stops_list=[]
    
    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():       
        for specimen,description in specimen_dictionary.items():            
            specimen_side_dictionary=get_side(specimen)            
            if specimen_side_dictionary:
                return_dictionary_list.append(specimen_side_dictionary)
                side_list.append(specimen_side_dictionary[global_strings.VALUE])
                start_stops_list+=specimen_side_dictionary[global_strings.STARTSTOPS]
    if side_list:        
        if type(side_list)==str:    side_list=[side_list]
        if ('Right' in side_list and 'Left' in side_list) or 'Bilateral' in side_list: side_list=['Bilateral']
        return_dictionary_list.append({global_strings.NAME:"PathSide",global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:';'.join(set(side_list)),
                                       global_strings.CONFIDENCE:0.0,global_strings.VERSION:__version__,global_strings.STARTSTOPS:start_stops_list})

    ## if there were no specimens, or no specimen headers in the text - look at the text overall ##
    else:
        overall_side_dictionary=get_side('')        
        if overall_side_dictionary:           
            if ('Right' in overall_side_dictionary[global_strings.VALUE] and 'Left' in overall_side_dictionary[global_strings.VALUE]) \
               or 'Bilateral' in overall_side_dictionary[global_strings.VALUE]: overall_side_dictionary[global_strings.VALUE]=['Bilateral']
            if type(overall_side_dictionary[global_strings.VALUE])==str:   overall_side_dictionary[global_strings.VALUE]=[overall_side_dictionary[global_strings.VALUE]]
            return_dictionary_list.append({global_strings.NAME:"PathSide",global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:';'.join(set(overall_side_dictionary[global_strings.VALUE])),
                                           global_strings.CONFIDENCE:0.75,global_strings.VERSION:__version__,global_strings.STARTSTOPS:overall_side_dictionary[global_strings.STARTSTOPS]})
            
    return (return_dictionary_list,list) 
