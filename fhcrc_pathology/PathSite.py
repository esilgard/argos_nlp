#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
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
import global_strings
import PathFindNumNodes
path= os.path.dirname(os.path.realpath(__file__))
dirs=path.split('\\')




    
def get(disease_group,dictionary):   
    '''
    return a list of dictionaries of each PathSite (location of tumor) per specimen (for the PathFinding table) and overall Site (for the Pathology table)
    from normal cased text of the pathology report    
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
        numNodes=None
        numNodesPos=None
        nodes_start_stops=[]
        for section in dictionary:
            section_specimen=section[3]
            line_onset=section[2]
            header=section[1]            
            if section_specimen is not None and specimen in section_specimen and ('SPECIMEN' in header or 'DESCRIPTION' in header or 'IMPRESSION' in header or 'Specimen' in header):               
                text= dictionary[section].items()[0][1]                
                ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                ## these can contain confusing general statements about the cancer and/or patients in general ##
                if re.search('[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',text):pass               
                else:
                    text=text.lower()
                    text=re.sub('[,:;\\\/\-]',' ',text); text=re.sub('[.] ', '  ',text)      ## this should keep decimal places and throw out periods                    
                    for each_site in site_list:                        
                        for each_match in re.finditer('^.*( |^|\")'+each_site+'( |$|\").*',text,re.DOTALL):                            
                            if standardizations[each_site] not in specimen_site_list:                                    
                                specimen_site_list.append(standardizations[each_site])
                            if 'Lymph' in standardizations[each_site]:
                                numNodes,numNodesPos=PathFindNumNodes.get(section,text)
                            specimen_start_stops_list.append({global_strings.START:each_match.start(2)+line_onset,global_strings.STOP:each_match.end(2)+line_onset})                                
        if specimen_site_list:            
            return {global_strings.NAME:"PathFindSite",global_strings.KEY:specimen,global_strings.TABLE:global_strings.FINDING_TABLE,global_strings.VALUE:';'.join(set(specimen_site_list)),
                    global_strings.CONFIDENCE:("%.2f" % .85), global_strings.VERSION:__version__,global_strings.STARTSTOPS:specimen_start_stops_list},numNodes,numNodesPos
        else: return None,None,None
                                  
###################################################################################################################
    
    try:
        disease_group_sites,disease_group_standardizations=make_lists(disease_group+'/')
        general_sites,general_standardizations=make_lists('')
    except: return ([{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'ERROR: could not access site file -- PathSite not completed'}],Exception)
    
    full_text=dictionary[(-1,'FullText',0,None)]
    return_dictionary_list=[]    
    site_list=[]
    start_stops_list=[]

       
    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():        
        for specimen,description in specimen_dictionary.items():            
            specimen_site_dictionary,numNodes,numNodesPos=get_site(disease_group_sites,disease_group_standardizations,specimen)            
            if not specimen_site_dictionary:               
                specimen_site_dictionary,numNodes,numNodesPos=get_site(general_sites,general_standardizations,specimen)    
            if specimen_site_dictionary:
                return_dictionary_list.append(specimen_site_dictionary)
                if numNodes and numNodesPos:                    
                    return_dictionary_list.append(numNodes)
                    return_dictionary_list.append(numNodesPos)

                site_list+=(specimen_site_dictionary[global_strings.VALUE].split(';'))
                start_stops_list+=(specimen_site_dictionary[global_strings.STARTSTOPS])    
    if site_list:        
        return_dictionary_list.append({global_strings.NAME:"PathSite",global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:';'.join(set(site_list)),
                                       global_strings.CONFIDENCE:0.75,global_strings.VERSION:__version__,global_strings.STARTSTOPS:start_stops_list})

    ## if there were no specimens, or no specimen headers in the text - look at the text overall - first for disease specific, then for general sites ##
    else:
        ## disease specific sites throughout the whole report ##
        overall_site_dictionary,numNodes,numNodesPos=get_site(disease_group_sites,disease_group_standardizations,'')        
        if overall_site_dictionary:            
            return_dictionary_list.append({global_strings.NAME:"PathSite",global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:overall_site_dictionary[global_strings.VALUE],
                    global_strings.CONFIDENCE:0.75,global_strings.VERSION:__version__, global_strings.STARTSTOPS:overall_site_dictionary[global_strings.STARTSTOPS]})
            if numNodes and numNodesPos:                    
                return_dictionary_list.append(numNodes)
                return_dictionary_list.append(numNodesPos)
        else:
            ## general sites throughout the whole report ##
            overall_site_dictionary,numNodes,numNodesPos=get_site(general_sites,general_standardizations,'')
            if overall_site_dictionary:            
                return_dictionary_list.append({global_strings.NAME:"PathSite",global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:overall_site_dictionary[global_strings.VALUE],
                    global_strings.CONFIDENCE:0.75,global_strings.VERSION:__version__, global_strings.STARTSTOPS:overall_site_dictionary[global_strings.STARTSTOPS]})
                if numNodes and numNodesPos:                    
                    return_dictionary_list.append(numNodes)
                    return_dictionary_list.append(numNodesPos)
    return (return_dictionary_list,list)
