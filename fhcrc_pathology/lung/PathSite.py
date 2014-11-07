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



    return_dictionary={"name":"PathSite","value":None,"confidence":0.0,"algorithmVersion":__version__,
                       "startStops":[]}
    return (return_dictionary,dict) 

