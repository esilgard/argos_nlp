#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import re,global_strings


'''author@esilgard'''
'''December 2014'''
__version__='iscn_string_cleaner1.0'


def get(text):
    '''
    clean up the scca or uw string that contains the ISCN karyotype info
    '''
    #if 't(1;12;16;17)(p22;q13;p13;q12)' in text: print text
    ## cut off FISH results in SCCA strings
    if 'nuc' in text:
        text=text[:text.find('nuc')]
    if 'NUC' in text:
        text=text[:text.find('NUC')]
    ## account for strings with typo ":" (instead of ";") in the context of digit;digit
    if re.search('[\d]:[\d]',text):       
        typo=re.match('.*([\d]:[\d]).*',text).group(1)       
        fix=re.sub(':',';',typo)
        text=re.sub(typo,fix,text)       
    #if 't(1;12;16;17)(p22;q13;p13;q12)' in text: print text   
    ## get all text before the final cell count 
    text=text[:text.rfind(']')+1] 
    karyotype_string=text[text.find(':')+1:].strip()   
    karyotype_string=karyotype_string.replace('//','/')    
    karyotype_string=karyotype_string.strip('"')   
    karyotype_string=karyotype_string.strip('/')
    #if 't(1;12;16;17)(p22;q13;p13;q12)' in text: print text
    if 'ish' in karyotype_string or 'rror' in karyotype_string:        
        return ''
        print 'PARSING ERROR'
    else:
        return karyotype_string

        
