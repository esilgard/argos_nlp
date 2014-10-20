#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''October 2014'''


import re

## mapping of grade numbers to words ##

grades={'high':'high','low':'low','intermediate':'intermediate',
        ' 3 ':'high',' 1 ':'low',' 2 ':'intermediate',' iii ':'high',
        ' i ':'low',' ii ':'intermediate'}
histos=['carcinoma','cancer','sclc']


def get(dictionary):
    grade=[]
    text='    '.join([y for x in dictionary.keys() if 'COMMENT' in x or 'FINAL' in x or 'IMPRESSION' in x for x,y in sorted(dictionary[x].items())])
    
    index=text.find('grade')
    window=text[max(0,index-45):min(index+45,len(text))]
    
    for g,n in grades.items():
        if re.match('.{,7}'+g+'.{,3}grade.{,7}',window): return n
        if re.search('[\W]'+g+'[\W]',window):
            if 'grade:' in window: return n
            for h in histos:
                if h in window:return n
            
      
    m=re.match('.*([123])[/of ]{1,6}3.{,20}fn[c]?l[c]?c.*',text)
    
    if m: return grades[' '+m.group(1)+' ']
    else: m=re.match('.*fn[c]?l[c]?c .{,20}([123])[/of ]{1,6}3.*',text)
    if m: return grades[' '+m.group(1)+' ']
    else: m=re.match('.*fn[c]?l[c]?c .{,20}grade.{,5}([123]).*',text)
    if m: return grades[' '+m.group(1)+' ']
    else:    return None
