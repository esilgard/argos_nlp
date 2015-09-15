#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='OtherFinding1.0'

import re
import os
import global_strings
path= os.path.dirname(os.path.realpath(__file__))+'/'


#############################################################################################################################################################

#############################################################################################################################################################

def get(disease_group,dictionary):
    '''
    extract the general findings from the lower cased text of the pathology report       
    return a list of dictionaries of each PathFindOther (per specimen) and overall PathOther (for the entire report)
    '''
   
    ## a general list of other findings
    findings=[]
    findings_standardizations={}
    try:
        for line in open(path+'/'+'other_findings.txt','r').readlines():
            find=line.split(';')
            for f in find:
                f=f.strip().lower()
                findings_standardizations[f]=find[0].strip()
                findings.append(f)
        findings=sorted(findings,key=lambda x: len(x),reverse=True)        
    except: return ([{global_strings.ERR_TYPE:'Exception',global_strings.ERR_STR:'ERROR: could not access general findings file at '+path+'/'+'other_findings.txt -- PathHistology not completed'}],Exception)

    ## loop through relevant sections findings
    def get_spec_histo(specimen,string_list,standardizations):        
        specimen_finding_set=set([])
        specimen_start_stops_set=set([])
        for section in sorted(dictionary):                
            section_specimen=section[3]                
            line_onset=section[2]
            header=section[1]          
            if ('IMPRESSION' in header or 'FINAL DIAGNOSIS' in header or 'COMMENT' in header) and 'CLINICAL' not in header:                
                for index,results in sorted(dictionary[section].items(),key=lambda x: int(x[0])):                 
                    ## meant to weed out references to literature/papers - picking up publication info like this: 2001;30:1-14. ##
                    ## these can contain confusing general statements about the cancer and/or patients in general ##
                    if re.search('[\d]{4}[;,][ ]*[\d]{1,4}:[\d\-]{1,6}',results):pass 
                    elif specimen in section_specimen:                        
                        text=results.lower()
                        text=re.sub('[.,:;\\\/\-]',' ',text)
                        for each_string in string_list:                            
                            finding,onset,offset=find_histology(text,each_string)                           
                            if finding:                           
                                specimen_start_stops_set.add((line_onset+onset,line_onset+offset))                                
                                specimen_finding_set.add(standardizations[finding])                            
       
        return specimen_finding_set,specimen_start_stops_set
##############################################################################################################################################################        
    return_dictionary_list=[]
    finding_set=set([])
    finding_start_stops_set=set([])   
    ## loop through explicitly labeled specimens to look for corresponding finding in relevant sections
    for specimen_dictionary in dictionary[(0,'SpecimenSource',0,None)].values():
        
        for specimen,description in specimen_dictionary.items():
            spec_finding_set,spec_finding_start_stops_set=get_spec_histo(specimen,findings,findings_standardizations)
            confidence=.7
            if not spec_finding_set:
                specimen='UNK'
                confidence=.6
                spec_finding_set,spec_finding_start_stops_set=get_spec_histo('',findings,findings_standardizations)
            if spec_finding_set:                
                return_dictionary_list.append({global_strings.NAME:"PathFindOther",global_strings.KEY:specimen,global_strings.TABLE:global_strings.FINDING_TABLE,
                    global_strings.VALUE:';'.join(spec_finding_set),global_strings.CONFIDENCE:("%.2f" % confidence),global_strings.VERSION:__version__,
                    global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in spec_finding_start_stops_set]})
                
                finding_set=finding_set.union(spec_finding_set)                
                finding_start_stops_set=finding_start_stops_set.union(spec_finding_start_stops_set)
                
    ## aggregate histologies of individual specimens for overall finding
    if finding_set:
        
        return_dictionary_list.append({global_strings.NAME:"PathFindingOther",global_strings.KEY:"ALL",global_strings.TABLE:global_strings.PATHOLOGY_TABLE,global_strings.VALUE:';'.join(finding_set),
            global_strings.CONFIDENCE:("%.2f" % (sum([float(x.get(global_strings.CONFIDENCE)) for x in return_dictionary_list])/len(return_dictionary_list))),
            global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:char[0],global_strings.STOP:char[1]} for char in finding_start_stops_set]})     
    
    return (return_dictionary_list,list)        
                
            
## check for the presence of a non-negated string ##
def find_histology(short_text,finding):
   
    if re.search(r'([\W]|^)'+finding+r'([\W]|$)',short_text):        
        if not re.search(r'( not | no |negative |free of |against |(hx|history) of | to rule out|preclud)[\w ]{,50}'+finding+r'([\W]|$)',short_text) and \
           not re.search(r'([\W]|^)'+finding+r'[\w ]{,40}( unlikely| not (likely|identif)| negative)',short_text):                
            return (finding,short_text.find(finding),short_text.find(finding)+len(finding))
    return None,None,None
                      
