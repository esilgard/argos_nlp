#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''
    written November 2014  , updates:
    December 2014 - added table_name to return dictionary  
'''
__version__='PathSite1.0'

import os
import re
path= os.path.dirname(os.path.realpath(__file__))
dirs=path.split('\\')


def get(disease_group,dictionary):   
    '''
    return a list of dictionaries of each PathSite (location of tumor) per specimen (for the PathFinding table) and overall Site (for the Pathology table)
    from normal cased text of the pathology report

    return dictionary example:
        {"name":"PathSite",
        "value":datetime object/or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "table":table_name,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
      
    ## a list of sites and their standardized forms from the disease relevent sites file##
    def make_lists(disease_group):
        sites=[]
        standardizations={}       
        for line in open(path+'/'+disease_group+'sites.txt','r').readlines():
            site_list=line.split(';')
            for h in site_list:
                h=h.strip().lower()
                standardizations[h]=site_list[0].strip()
                sites.append(h)                
        sites=sorted(sites,key=lambda x: len(x),reverse=True)
       
        return sites,standardizations  
    
###############################################################################################################
    
###############################################################################################################    
    def get_site(site_list,standardizations,specimen):        
        specimen_site_list=[]
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
                    text=re.sub('[.,:;\\\/\-]',' ',text)                     
                    for each_site in site_list:
                        for each_match in re.finditer('.*( |^)'+each_site+'( |$).*',text,re.DOTALL):                               
                            if standardizations[each_site] not in specimen_site_list:                                    
                                specimen_site_list.append(standardizations[each_site])                                    
                            specimen_start_stops_list.append({'startPosition':each_match.start(2)+line_onset,'stopPosition':each_match.end(2)+line_onset})
                                
        if specimen_site_list:            
            return {"name":"PathFindSite","recordKey":specimen,"table":"PathologyFinding","value":';'.join(set(specimen_site_list)),"confidence":("%.2f" % .85),
                                          "algorithmVersion":__version__,"startStops":specimen_start_stops_list}
        else: return None
                                      
#####################################################################################################################
    
    try:
        disease_group_sites,disease_group_standardizations=make_lists(disease_group+'/')
        general_sites,general_standardizations=make_lists('')
    except: return ([{'errorType':'Exception','errorString':'ERROR: could not access site file -- PathSite not completed'}],Exception)
    
    full_text=dictionary[(-1,'FullText',0,None)]
    return_dictionary_list=[]    
    site_list=[]
    start_stops_list=[]
    
    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():
        
        for specimen,description in specimen_dictionary.items():           
            specimen_site_dictionary=get_site(disease_group_sites,disease_group_standardizations,specimen)
            if not specimen_site_dictionary:               
                specimen_site_dictionary=get_site(general_sites,general_standardizations,specimen)    
            if specimen_site_dictionary:
                return_dictionary_list.append(specimen_site_dictionary)
                site_list+=(specimen_site_dictionary["value"].split(';'))
                start_stops_list+=(specimen_site_dictionary["startStops"])

    if site_list:
        
        return_dictionary_list.append({"name":"PathSite","table":"Pathology","value":';'.join(set(site_list)),"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":start_stops_list})

    ## if there were no specimens, or no specimen headers in the text - look at the text overall ##
    else:
        overall_site_dictionary=get_site(general_sites,general_standardizations,'')
        if overall_site_dictionary:
            return_dictionary_list.append({"name":"PathSite","table":"Pathology","value":overall_site_dictionary["value"],"confidence":0.75,"algorithmVersion":__version__,
                       "startStops":overall_site_dictionary["startStops"]})
    
    return (return_dictionary_list,list)
