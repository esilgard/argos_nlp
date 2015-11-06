#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

__author__='esilgard'

import re, sys
import global_strings
#from sklearn import svm
import numpy as np
from scipy.sparse import dok_matrix

class OneFieldPerReportML(object):
    '''
        extract the value of a field which has one unambiguous value per report using a scikit learn ML model        
    ''' 
    __version__='OneFieldPerReportML1.0'
    
    def __init__(self):
        self.field_name='Default'
        self.keyword_patterns= {} 
        self.return_dictionary = {}
        self.confidence='0.0'
        self.table='Default'
     
    def get_version(self):
        return self.__version__

    def tokenize_and_vectorize(self,full_text):
        '''
        rudimentry tokenization and a hardcoded skip(2)gram model - the window around the keyword is variable
        '''
        text=re.sub('[.,:;\"\'\(\)\*]',' ',full_text.lower()) 
        tokens=text.split()
        vector=set([])       
        word=False
        for v in range(len(tokens)):
            current=tokens[v] 
            for kw,pattern in self.keyword_patterns.items():               
                if re.search(pattern,current):                    
                    word=True;vector.add(kw)
                    ## place holder for character offset addition...
                    ## might be helpful to at least highlight the original keywords in the text?
                    pre=v-self.window                         
                    while v>pre>=0:                                   
                        #unigrams
                        vector.add(kw+'pre_window='+tokens[pre])
                        if  v-1>pre:
                            #bigrams
                            vector.add(kw+'pre_window='+tokens[pre]+'_'+tokens[pre+1])
                            if v-2>pre:
                                #one skipgram
                                vector.add(kw+'pre_window='+tokens[pre]+'_'+tokens[pre+2])
                                if v-3>pre:
                                    #two skipgram
                                    vector.add(kw+'pre_window='+tokens[pre]+'_'+tokens[pre+3])  
                        pre+=1
                    post=v+1
                    while post<min(len(text),v+self.window):                                   
                        #unigrams                               
                        vector.add(kw+'post_window='+tokens[post])
                        if  post<len(text)-1:
                            #bigrams
                            vector.add(kw+'post_window='+tokens[post]+'_'+tokens[post+1])
                            if post<len(text)-2:
                                #one skipgram
                                vector.add(kw+'post_window='+tokens[post]+'_'+tokens[post+2])
                                if post<len(text)-3:
                                    #one skipgram
                                    vector.add(kw+'post_window='+tokens[post]+'_'+tokens[post+3])
                        post+=1
                   
        if word==False:
            vector.add('NO_keyword_IN_TEXT')
        return vector
            
        
    def get(self, disease_group,dictionary):        
                             
        full_text=dictionary[(-1,'FullText',0,None)]           
        self.return_dictionary={global_strings.NAME:self.field_name,global_strings.VALUE:None,global_strings.CONFIDENCE:'%.2f' % 0.0,
                                global_strings.KEY:global_strings.ALL,  global_strings.VERSION:self.get_version(),
                                global_strings.STARTSTOPS:[],global_strings.TABLE:self.table}
        ## tokenize and turn into a sparse vector of binary features 
        feature_vector = self.tokenize_and_vectorize(full_text)
        ## map string features to svm integers according to the feature mapping in the model
        feature_array = [self.feature_mapping.get(f) for f in feature_vector if f in self.feature_mapping]
        ## scipy dictionary of keys type sparse array is easily confertable to a sparse column matrix                                            
        X = dok_matrix((1, self.features_in_model),dtype = np.float64)
        for f in feature_array:
            X[0,f]=1
        ## convert dictionary of keys into a sparse column matrix (sparse features)
        X.tocsc()
        class_label = self.model.predict(X)[0]        
        if class_label:               
            self.return_dictionary[global_strings.VALUE]=self.class_label_mapping[class_label]
            self.return_dictionary[global_strings.CONFIDENCE]=('%.2f' % self.confidence)
        return ([self.return_dictionary],list)
        
       
