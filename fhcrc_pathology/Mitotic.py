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

class Mitotic(OneFieldPerReportML):
    '''
    extract Mitotic Rate/Count using an svm model
    '''
    __version__ = 'Mitotic1.0'
    def __init__(self):
        super(Mitotic, self).__init__()
        self.field_name = 'Mitotic'
        self.table = gb.TEST_TABLE
        self.confidence = .98
        ## pickled model and feature/label mappings
        self.model = joblib.load(PATH + "models"+os.path.sep+"Mitotic"+os.path.sep+"svm_model_window7skip2.pkl")
        self.features_in_model = 184974
        self.feature_mapping = dict((x.split('\t')[0], int(x.strip().split('\t')[1])) for x in \
                               open(PATH + "models"+os.path.sep+"Mitotic"+os.path.sep+"feature_mapping.txt", 'r').readlines())
        self.class_label_mapping = {0: '0', 1: '1', 2: '2', 3: '3'}
        self.keyword_patterns = {'MITOTIC': r'mito((tic)|(s))', 'COUNT':r'^(count|activity)'}
        self.window = 7
