'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

__version__ = 'PathClassifier1.0'
import os, re
PATH = os.path.dirname(os.path.realpath(__file__)) + '/'
RESOURCES = {'behavior.txt': .1, 'node_sites.txt': .2, 'other_findings.txt': .2, \
             'procedures.txt': .2, 'sites.txt': .1, 'subsite.txt': .2, 'histologies.txt': .9, \
             'keywords.txt': .9}
DZ_GROUPS = ['brain', 'breast', 'GI', 'GU', 'gyn', 'heme', 'lung', 'sarcoma', 'skin', \
             'male_cancers', 'other', 'head&neck']
KEYWORD_D = {}
for disease in DZ_GROUPS:
    KEYWORD_D[disease] = {}
    for files in RESOURCES:
        for line in open(PATH + disease + '/' + files, 'r').readlines():
            for token in line.strip().split(';'):
                KEYWORD_D[disease].update({token.lower(): RESOURCES[files]})

def classify(text):
    ''' use keyword lists to classify pathology report by disease group '''
    votes = dict.fromkeys(DZ_GROUPS, 0)
    for disease in votes:
        for word in KEYWORD_D[disease]:
            for each in word.split(';'):
                a = re.findall(r'([\W])' + each + r'([\W])', text, re.IGNORECASE)
                votes[disease] += len(a) * KEYWORD_D[disease][word]
    ordered_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    if ordered_votes[0][1] == 0:
        return 'other', 0.0
    else:
        return ordered_votes[0][0], ordered_votes[0][1]/float(sum([x[1] for x in ordered_votes]))
