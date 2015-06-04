#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''
__version__='find_stages_intersection1.0'

# take the intersection of staging results from the purely rules
# based program and the Naive Bayes multinomial event model
## NO ERROR HANDLING YET - RETURNS ARE HARDCODED
def get_intersection(rules,bayes):
    print 'rules',rules
    print 'bayes',bayes
    return_errors=None
    return_dictionary={"name":"PrognosticStage","value":None,"confidence":0.0,"algorithmVersion":__version__,"startStops":[]}                       
    rule_stage=rules[0]
    rule_confidence=float(rules[1])
    ## is bayes returning unknowns right now?
    bayes_stage=bayes[0]
    bayes_confidence=float(bayes[1])

    #else:
    #    bayes_stage='UNKNOWN'
    #    bayes_confidence=0.0        
    if bayes_stage==rule_stage:
        return_dictionary['value']=bayes_stage
        return_dictionary['confidence']=(rule_confidence+bayes_confidence)/2                                
    else:
        return_dictionary['value']='UNKNOWN'
        return_dictionary['confidence']=0.0
    print 'intersection',return_dictionary['value'],return_dictionary['confidence']    
    return return_dictionary,return_errors,dict
