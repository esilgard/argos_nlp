#
# Copyright (c) 2013-2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''
    written November 2014    
'''
__version__='PathSite1.0'

import os
import re
path= os.path.dirname(os.path.realpath(__file__))
dirs=path.split('\\')


def get(dictionary):
    '''
    extract the PathSite (location of tumor)from normal cased text of the pathology report
    return a dictionary of
        {"name":"PathSite",
        "value":datetime object/or None,
        "algorithmVersion": __version__,
        "confidence": confidence_value,
        "startStops":[{"startPosition":start_pos1,"stopPosition":stop_pos1},{"startPosition....])
    '''
    return_dictionary={"name":"PathSide","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}

    
    ## a list of sites and their standardized forms from the disease relevent sites file##
    
    disease_group_sites=[]
    disease_group_standardizations={}
    try:
        for line in open(path+'/'+dirs[-1]+'_sites.txt','r').readlines():
            site_list=line.split(';')
            for h in site_list:
                h=h.strip().lower()
                disease_group_standardizations[h]=site_list[0].strip()
                disease_group_sites.append(h)                
        disease_group_sites=sorted(disease_group_sites,key=lambda x: len(x),reverse=True)
       
    except: return ({'errorType':'Exception','errorString':'ERROR: could not access '+dirs[-1]+' site file at '+path+'/'+dirs[-1]+'_sites.txt -- PathSite not completed'},Exception)
   
    ## a list of general sites and their standardized forms from a general sites file ##
    general_sites=[]
    general_standardizations={}
    try:
        for line in open('/'.join(dirs[:-1])+'/general_sites.txt','r').readlines():
            site_list=line.split(';')
            for h in site_list:
                h=h.strip().lower()
                general_standardizations[h]=site_list[0].strip()
                general_sites.append(h)
        general_sites=sorted(general_sites,key=lambda x: len(x),reverse=True)        
    except: return ({'errorType':'Exception','errorString':'ERROR: could not access general site file at '+'/'.join(dirs[:-1])+'/general_sites.txt -- PathSite not completed'},Exception)


    ignore_section=sorted([(x,y) for z in sorted(dictionary.keys(), key=lambda c: c[0]) for x,y in dictionary[z].items()],key=lambda b:int(b[0]))
    full_text='\n'.join([a[1] for a in ignore_section])    
    
    def get_site(site_list,standardizations):
        site=set([])
        chars_up_to_this_point=0
        for section in sorted(dictionary):
            for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):
                if 'CYTOLOGIC IMPRESSION' in section[1] or 'DIAGNOSIS' in section[1] or 'Specimen' in section[1] or 'SPECIMEN' in section[1]:                    
                    text=results.lower()
                    text=re.sub('[.,:;\\\/\-\)\(]',' ',text)                     
                    for each_site in site_list:                        
                        for each_match in re.finditer('.*( |^)'+each_site+'( |$).*',text):
                            if standardizations[each_site] not in site:
                                site.add(standardizations[each_site])                            
                            return_dictionary["startStops"].append({'startPosition':each_match.start(2)+chars_up_to_this_point,'stopPosition':each_match.end(2)+chars_up_to_this_point})
                chars_up_to_this_point+=len(results)+1
        return site
    site=get_site(disease_group_sites,disease_group_standardizations)
    if not site:    site=get_site(general_sites,general_standardizations)    
    return_dictionary['value']=';'.join(site)                
    return (return_dictionary,dict)
