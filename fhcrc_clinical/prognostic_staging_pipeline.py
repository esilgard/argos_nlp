## prognostic staging pipeline ##
## all intermediate results written to file
import os
import find_stages,make_lung_stage_vectors,find_stages_NB_multinomial,find_stages_intersection
path=os.path.basename


prior_model_file='C:\Users\esilgard\Desktop\Lung/MASTER_NB_ME_prior_model.txt'
prob_of_word_model_file='C:\Users\esilgard\Desktop\Lung/MASTER_NB_ME_prob_of_word_model.txt'
smoothed_model_file='C:\Users\esilgard\Desktop\Lung/MASTER_NB_ME_smoothed_model.txt'
notes_file='C:/users/esilgard/desktop/Lung/LungClinicalNotes.txt'
output_file='C:/users/esilgard/desktop/Lung/MASTER_pipeline_output.txt'


## returns a dictionary of {mrn:stage}
rules_output=find_stages.get(notes_file)
bayes_vectors=make_lung_stage_vectors.get(notes_file)
bayes_output=find_stages_NB_multinomial.classify_stage_match_vectors(bayes_vectors,prior_model_file,prob_of_word_model_file,smoothed_model_file)

intersection=find_stages_intersection.get_intersection(rules_output,bayes_output,output_file)

