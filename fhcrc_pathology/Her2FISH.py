'''author@esilgard'''
#
# Copyright (c) 2013-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

from .OneFieldPerReportML import OneFieldPerReportML
from . import global_strings as gb
from sklearn.externals import joblib
import os
PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class Her2FISH(OneFieldPerReportML):
    '''
    extract Her2neu test results by FISH method using an svm model
    '''
    __version__ = 'Her2FISH1.0'
    def __init__(self):
        super(Her2FISH, self).__init__()
        self.field_name = 'Her2FISH'
        self.table = gb.TEST_TABLE
        self.confidence = .9885
        ## pickled model and feature/label mappings
        self.model = joblib.load(PATH + "models/Her2FISH/svm_model_window7skip2.pkl")
        self.feature_mapping = dict((x.split('\t')[0], int(x.strip().split('\t')[1])) for x in \
                               open(PATH + "models/Her2FISH/feature_mapping.txt", 'r').readlines())
        self.class_label_mapping = {0: 'NO_HER2NEU', 1: 'Equivocal', 2: 'Positive', 3: 'Negative',\
                                    4: 'Heterogeneous', 5: 'Insufficient'}
        self.keyword_patterns = {'HER2': r'her[\\\/\-]?2', 'HER': r'^her', 'CERB': r'^c[\-]?erb',\
                            'FISH': r'^(f|c)[\-]?ish', 'STUDIES': r'studies',\
                            'FLUORESCENCE': r'fluorescen', 'NEU': r'neu$', 'GENE': r'(onco)?gene$'}
        self.window = 7
