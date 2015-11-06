#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from OneFieldPerReportML import OneFieldPerReportML
import global_strings as dict_keys
from sklearn.externals import joblib
import os
path= os.path.dirname(os.path.realpath(__file__))+'\\'

class Her2FISH(OneFieldPerReportML):
    __version__='Her2FISH_Decoder1.0'
    
    def __init__(self):
        self.field_name='Her2FISH'        
        self.table=dict_keys.TEST_TABLE
        self.confidence = .9885        
        self.model = joblib.load(path+"models/Her2FISH/svm_model_window7skip2.pkl")
        self.features_in_model = 184974
        self.feature_mapping = dict((x.split('\t')[0],int(x.strip().split('\t')[1])) for x in open(path+"models/Her2FISH/feature_mapping.txt",'r').readlines())
        self.class_label_mapping = {0:'NO_HER2NEU',1:'Equivocal',2:'Positive',3:'Negative',4:'Heterogeneous',5:'Insufficient'}
        self.keyword_patterns = {'HER2':'her[\\\/\-]?2','HER':'^her','CERB':'^c[\-]?erb','FISH':'^(f|c)[\-]?ish','STUDIES':'studies','FLUORESCENCE':'fluorescen','NEU':'neu$','GENE':'(onco)?gene$'}
        self.window = 7
       
    

