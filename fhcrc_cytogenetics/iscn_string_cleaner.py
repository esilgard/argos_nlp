'''author@esilgard'''
#
# Copyright (c) 2015-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#
import re
import global_strings as gb

__version__ = 'iscn_string_cleaner1.0'

def get(original_text, karyo_offset):
    '''
    clean up the scca or uw string that contains the ISCN karyotype info
    look for common formatting inconsistenies in the karyotype or
    common free text interpretations
    return the cleaned string and a dictionary (if applicable) of the swog risk interpretation
    '''
    text = original_text
    interpretation = re.match(r'.*(insufficient).*', text, re.IGNORECASE)
    if not interpretation:
        interpretation = re.match(r'.{,16}:[ ]+(normal).*', text, re.IGNORECASE)
        if interpretation:
            if 'nuc' not in text and 'FISH' not in text:
                swog = gb.INTERMEDIATE
            else:
                swog = gb.UNKNOWN
    else:
        swog = gb.INSUFFICIENT
    if interpretation:
        interpretation_str = interpretation.group(1)
        return [{gb.NAME:gb.SWOG, gb.TABLE:gb.CYTOGENETICS, gb.VALUE:swog, gb.CONFIDENCE:.95,
                 gb.STARTSTOPS:[{gb.START:text.find(interpretation_str), \
                 gb.STOP:text.find(interpretation_str) + len(interpretation.group(1))}], \
                 gb.VERSION:__version__}, {gb.NAME:gb.KARYOTYPE_STRING, gb.VALUE:text, \
                 gb.CONFIDENCE:.95, gb.VERSION:__version__, gb.STARTSTOPS:[{gb.START:0}, \
                {gb.STOP:len(text)}]}], text

    ## cut off FISH results in SCCA strings
    if 'nuc' in text:
        text = text[:text.find('nuc')]
    if 'NUC' in text:
        text = text[:text.find('NUC')]
    ## account for strings with typo ":" (instead of ";") in the context of digit;digit
    if re.search(r'[\d]:[\d]', text):
        typo = re.match(r'.*([\d]:[\d]).*', text).group(1)
        fix = re.sub(r':', r';', typo)
        text = re.sub(typo, fix, text)

    ## get all text before the final cell count
    text = text[:text.rfind(']') + 1]
    colon_index = text.find(':') + 1
    karyo_offset += colon_index  + len(text[colon_index:]) - len(text[colon_index:].lstrip())

    karyotype_string = text[colon_index:].strip()
    ## !this will mess up char offsets! currently
    karyotype_string = karyotype_string.replace('//', '/')
    karyotype_string = karyotype_string.strip('"')
    karyotype_string = karyotype_string.strip('/')

    if 'ish' in karyotype_string or 'rror' in karyotype_string:
        return [{gb.NAME:gb.SWOG, gb.TABLE:gb.CYTOGENETICS, gb.VALUE:gb.UNKNOWN, \
        gb.CONFIDENCE:0.0, gb.STARTSTOPS:[], gb.VERSION:__version__}, \
        {gb.NAME:gb.KARYOTYPE_STRING, gb.VALUE:original_text, gb.CONFIDENCE:0.0, \
        gb.VERSION:__version__, gb.STARTSTOPS:[{gb.START:0}, {gb.STOP:len(original_text)}]}], text

    else:
        return None, karyotype_string, karyo_offset
		
