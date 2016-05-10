#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import re,global_strings

'''author@esilgard'''
__version__='iscn_string_cleaner1.0'


def get(original_text):
    '''
    clean up the scca or uw string that contains the ISCN karyotype info
    look for common formatting inconsistenies in the karyotype or
    common free text interpretations
    return the cleaned string and a dictionary (if applicable) of the swog risk interpretation
    '''
    text=original_text
    interpretation=re.match('.*(insufficient).*',text,re.IGNORECASE)
    if not interpretation:
        interpretation=re.match('.{,16}:[ ]+(normal).*',text,re.IGNORECASE)
        if interpretation:            
            if 'nuc' not in text and 'FISH' not in text: swog=global_strings.INTERMEDIATE
            else: swog=global_strings.UNKNOWN
    else:
        swog=global_strings.INSUFFICIENT
    if interpretation:
        interpretation_str=interpretation.group(1)
        #print text,interpretation_str,text.find(interpretation_str),text.find(interpretation_str)+len(interpretation_str)
        return [{global_strings.NAME:global_strings.SWOG,global_strings.TABLE:global_strings.AML_CYTOGENETICS,global_strings.VALUE:swog,global_strings.CONFIDENCE:.95,
                global_strings.STARTSTOPS:[{global_strings.START:text.find(interpretation_str),global_strings.STOP:text.find(interpretation_str)+len(interpretation.group(1))}],global_strings.VERSION:__version__},
                {global_strings.NAME:global_strings.KARYOTYPE_STRING,global_strings.VALUE:text,global_strings.CONFIDENCE:9.5,
                 global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:0},{global_strings.STOP:len(text)}]}],text
        
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
   
    ## get all text before the final cell count 
    text=text[:text.rfind(']')+1] 
    karyotype_string=text[text.find(':')+1:].strip()   
    karyotype_string=karyotype_string.replace('//','/')    
    karyotype_string=karyotype_string.strip('"')   
    karyotype_string=karyotype_string.strip('/')
  
    if 'ish' in karyotype_string or 'rror' in karyotype_string:        
        return [{global_strings.NAME:global_strings.SWOG,global_strings.TABLE:global_strings.AML_CYTOGENETICS,global_strings.VALUE:global_strings.UNKNOWN,global_strings.CONFIDENCE:0.0,
                global_strings.STARTSTOPS:[],global_strings.VERSION:__version__},
                {global_strings.NAME:global_strings.KARYOTYPE_STRING,global_strings.VALUE:original_text,global_strings.CONFIDENCE:0.0,
                 global_strings.VERSION:__version__,global_strings.STARTSTOPS:[{global_strings.START:0},{global_strings.STOP:len(original_text)}]}],text
        
    else:
        return None,karyotype_string

        
