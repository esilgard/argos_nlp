#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='PathClassifier1.0'
import os,re
path = os.path.dirname(os.path.realpath(__file__))+'/'
resources={'behavior.txt':.1,'node_sites.txt':.2,'other_findings.txt':.2,'procedures.txt':.2,'sites.txt':.1,'subsite.txt':.2,'histologies.txt':.9,'keywords.txt':.9}
dz_groups=['brain','breast','GI','GU','gyn','heme','lung','sarcoma','skin','male_cancers','other','head&neck']
keyword_d={}
for disease in dz_groups:
    keyword_d[disease]={}
    for files in resources:
        for line in open(path+disease+'/'+files,'r').readlines():
            for token in line.strip().split(';'):
                keyword_d[disease].update({token.lower():resources[files]})
                  
def classify(text):    
    votes=dict.fromkeys(dz_groups,0)
    for disease in votes:
        for word in keyword_d[disease]:
            for each in word.split(';'):                
                a=re.findall('([\W])'+each+'([\W])',text,re.IGNORECASE)
                #if a:print disease,'--',each,len(a)
                votes[disease]+=len(a)*keyword_d[disease][word]

    ordered_votes= sorted(votes.items(),key=lambda x:x[1], reverse=True)
    if ordered_votes[0][1] == 0:
        return 'other',0.0
    else:
        
        return ordered_votes[0][0],ordered_votes[0][1]/float(sum([x[1] for x in ordered_votes]))
