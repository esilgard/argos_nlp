#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='PathSite1.0'

import os
import re
import global_strings
path= os.path.dirname(os.path.realpath(__file__))

    
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
        specimen_site_set=set([])
        specimen_start_stops_set=set([])
    
        def find_site_match(text):            
            text=re.sub(r'[.,:;\\\/\-\)\(]',' ',text).lower()
            for each_site in site_list:  
                for each_match in re.finditer(r'^.*( |^)('+each_site+r')( |$).*',text,re.MULTILINE):                    
                    if not re.search(r'( not | no |negative |free of)[\w ]{,50}'+each_match.group(2),text,re.MULTILINE) and \
                       not re.search(each_match.group(2)+r'[\w ]{,40}( unlikely| not (likely|identif)| negative)',text,re.MULTILINE):                                           
                        specimen_site_set.add(standardizations[each_site])                        
                        ## only return char offsets for the regular path text (not the SpecimenSource text)
                        if line_onset:
                            specimen_start_stops_set.add((each_match.start(2)+line_onset,each_match.end(2)+line_onset))
                     
        for section in dictionary:
            section_specimen=section[3]
            line_onset=section[2]
            header=section[1]
            if section==(0,'SpecimenSource',0,None):          
                if dictionary[section][0].get(specimen):
                    find_site_match(dictionary[section][0].get(specimen))          
            elif ('SPECIMEN' in header or 'DESCRIPTION' in header or 'IMPRESSION' in header or 'Specimen' in header or 'DIAGNOSIS' in header) and 'CLINICAL' not in header:                  
                for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):
                    if specimen in section_specimen:                       
                        ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                        ## these can contain confusing general statements about the cancer and/or patients in general ##
                        if re.search(r'[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',index):pass
                        else:
                            find_site_match(results)                  
        if specimen_site_set:
            return {global_strings.NAME:"PathFindSite",global_strings.KEY:specimen,global_strings.TABLE:global_strings.FINDING_TABLE,global_strings.VALUE:';'.join(specimen_site_set),
                    global_strings.CONFIDENCE:("%.2f" % .85), global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in specimen_start_stops_set]}
        else: return None

                                  
###################################################################################################################   
    try:
        disease_group_sites,disease_group_standardizations=make_lists(disease_group+'/')
        general_sites,general_standardizations=make_lists('')
    except: return ([{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'ERROR: could not access site file -- PathSite not completed'}],Exception)
   
    return_dictionary_list=[]    
    site_set=set([])
    start_stops_set=set([])

    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():        
        for specimen,description in specimen_dictionary.items():
            specimen_site_dictionary=get_site(disease_group_sites,disease_group_standardizations,specimen)      
            if not specimen_site_dictionary:               
                specimen_site_dictionary=get_site(general_sites,general_standardizations,specimen)          
            if specimen_site_dictionary:
                return_dictionary_list.append(specimen_site_dictionary)                
                site_set.union(set(specimen_site_dictionary[global_strings.VALUE].split(';')))         
                for offsets in specimen_site_dictionary[global_strings.STARTSTOPS]:                    
                    start_stops_set.add((offsets[global_strings.START],offsets[global_strings.STOP]))

    if site_set:
        return_dictionary_list.append({global_strings.NAME:"PathSite",global_strings.KEY:specimen,global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:';'.join(site_set),
                                       global_strings.CONFIDENCE:("%.2f" % 0.75),global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in start_stops_set]})

    ## if there were no specimens, or no specimen headers in the text - look at the text overall - first for disease specific, then for general sites ##
    else:
        ## disease specific sites throughout the whole report ##
        overall_site_dictionary=get_site(disease_group_sites,disease_group_standardizations,'')        
        if overall_site_dictionary:            
            return_dictionary_list.append({global_strings.NAME:"PathSite",global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.KEY:'ALL',global_strings.VALUE:overall_site_dictionary[global_strings.VALUE],
                    global_strings.CONFIDENCE:("%.2f" % 0.75),global_strings.VERSION:__version__, global_strings.STARTSTOPS:overall_site_dictionary[global_strings.STARTSTOPS]})
           
        else:
            ## general sites throughout the whole report ##
            overall_site_dictionary=get_site(general_sites,general_standardizations,'')
            if overall_site_dictionary:            
                return_dictionary_list.append({global_strings.NAME:"PathSite",global_strings.KEY:'ALL',global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:overall_site_dictionary[global_strings.VALUE],
                    global_strings.CONFIDENCE:("%.2f" % 0.75),global_strings.VERSION:__version__, global_strings.STARTSTOPS:overall_site_dictionary[global_strings.STARTSTOPS]})
                
    return (return_dictionary_list,list)
