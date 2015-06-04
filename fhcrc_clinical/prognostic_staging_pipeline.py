#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='prognostic_staging_pipeline1.0'

## prognostic staging pipeline ##
## all intermediate results written to file
import os
import find_stages,make_stage_vectors
import find_stages_NB_multinomial,find_stages_intersection
path=os.path.basename



def get(disease_group,note_list):   
        
    ## pulls in a list of tuples, which contain a tuple id and text note for the given mrn in the form [((mrn,service_date,updated_date),clinic note text),....]
    rules_output=find_stages.get(note_list)
    print 'rules output',rules_output
    bayes_vectors=make_stage_vectors.get(note_list)
    print len(bayes_vectors),'stage matches from bayes'
    ## better for now in 2.6 - because of the numpy std installation???
    bayes_output=find_stages_NB_multinomial.classify_stage_match_vectors(bayes_vectors, disease_group)    
    intersection=find_stages_intersection.get_intersection(rules_output,bayes_output)
    return intersection
