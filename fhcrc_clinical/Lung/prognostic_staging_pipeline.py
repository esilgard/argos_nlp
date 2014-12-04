#
# Copyright (c) 2014 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
'''October 2014'''
__version__='prognostic_staging_pipeline1.0'

## prognostic staging pipeline ##
## all intermediate results written to file
import os
import find_stages,make_lung_stage_vectors
import find_stages_NB_multinomial,find_stages_intersection
path=os.path.basename


prior_model_file='H:/NLP/argos_nlp/fhcrc_clinical/Lung/MASTER_NB_ME_prior_model.txt'
prob_of_word_model_file='H:/NLP/argos_nlp/fhcrc_clinical/Lung/MASTER_NB_ME_prob_of_word_model.txt'
smoothed_model_file='H:/NLP/argos_nlp/fhcrc_clinical/Lung/MASTER_NB_ME_smoothed_model.txt'
notes_file='K:/CRI/STTR/Lung/lung_notes.txt'
output_file='K:/CRI/STTR/Lung/prognostic_stages_for_1174_lung_mrns2.txt'


rules_output,note_dictionary=find_stages.get(notes_file)
#print len(rules_output), 'stages from rules'
bayes_vectors=make_lung_stage_vectors.get(note_dictionary)
#print len(bayes_vectors),'stage matches from bayes'


## better for now in 2.6 - because of the numpy std installation
bayes_output=find_stages_NB_multinomial.classify_stage_match_vectors(bayes_vectors,prior_model_file,prob_of_word_model_file,smoothed_model_file)
#print len(bayes_output),'stages  from bayes'
intersection=find_stages_intersection.get_intersection(rules_output,bayes_output,output_file)

