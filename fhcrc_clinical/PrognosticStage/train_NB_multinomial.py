#multinomial Naive Bayes Training

import sys
import math
import numpy as np

pOfClass = {}                       #dictionary to store the p(classes)
numOfClass = {}                     #dictionary of class: number of total words in class
wordGivenClass = {}                 #double dictionary of {class:{word: p(word|class}}
smoothed = {}                       #dictionary of unseen (smoothed) probabilities per class
vocab = set()                       #set of all the words in the vocabulary
delta = float(.00001)                         #used for smoothing
prior_delta=float(0)
classProb={}                        #dictionary of the probability of vocabulary words that are NOT in the document, given a class
classes=set()                       #just the set of the classes
training_vectors={}                 #store the training vectors (with their labels as keys) for the training output_file
'''get the training data from the input file and load dictionaries of probabilities (Global Variables)
   processes traing file in the format:
   label    class   feature1    value1   feature2   value2...'''
def get_training():
    with open('C:/users/esilgard/desktop/Lung/ALLVectors.txt','r') as f:
        docs=0
        numOfWord = {}
        vocab_add=vocab.add
        for lines in f:
            docs+=1
            vectors=lines.split()
            label = vectors[0]
            class1 = vectors[1]
            pOfClass[class1] = pOfClass.get(class1,0)+1 
            wordGivenClass[class1]=wordGivenClass.get(class1,{})
            training_vectors[label]=[]
            append=training_vectors[label].append
            append(class1)
            for i in range(2,len(vectors),2):                   
                word=vectors[i]
                try:
                    count=int(vectors[i+1])
                except:
                    print vectors, sys.exit()
                append([word,count])
                vocab_add(word)
                numOfWord[class1] = numOfWord.get(class1,0)+int(count )
                (wordGivenClass[class1])[word] = (wordGivenClass[class1]).get(word,0)+int(count)

    '''divide dictionary values by counts so that they store probabilities and add in delta smoothing'''
    training_acc={}
    classes=pOfClass.keys()
    #print pOfClass
    total=sum([v for k,v in pOfClass.items()])
    for c in classes:
        numOfClass[c]=pOfClass[c]
        pOfClass[c]=(pOfClass[c]+(delta/float(3*delta+docs)))/total
        wordGivenClass[c].update((k,(v+delta)/float(len(vocab)*delta+numOfWord[c])) for (k,v) in wordGivenClass[c].items() )
        training_acc[c]={}
        smoothed[c]=delta/(len(vocab)*delta+numOfWord[c])
        for cc in classes:
            (training_acc[c])[cc]=0
    #print pOfClass       
    return classes,training_acc

'''normalize log10 values before they're brought back into probability space in order to solve underflow problem'''
def normalize(x):
    a = np.logaddexp.reduce(x)
    return np.exp(x - a)

              
   
'''iterate through the training_vectors dictionary (label:list of lists [f1,v1],[f2,v2]....)
and output the probabilities of class given the features in the documents'''
def output_training(classes,o,acc):
    math_log=math.log10
    for tr in training_vectors:
        
        cl=training_vectors[tr].pop(0)
        
        cProbs=[]
        cProbs_append=cProbs.append       
        for c in classes:
            num=0.0
            for w,f in training_vectors[tr]:
                if w in wordGivenClass[c]:
                    try:
                        num+=math_log(wordGivenClass[c][w])*f
                    except:
                        print wordGivenClass[c][w]
                else:
                    num+=math_log(smoothed[c])*f
                                                    
            cProbs_append(num+math_log(pOfClass[c]))        
        cProbs=normalize(cProbs)        
        cProbDict=dict(zip(classes,cProbs))       
        op=[(k,v) for (k,v) in sorted(cProbDict.items(),key=lambda x: x[1],reverse=True)]
        
        (acc[cl])[op[0][0]]=(acc[cl].get(op[0][0],0))+1
        o.write(tr+'\t'+cl)
        for index in range(len(op)):
            o.write('\t'+op[index][0]+'\t'+str(op[index][1])+'\t')
        o.write('\n')
    return acc

'''output the model based on the training data'''
def output_model(classes):
    math_log=math.log10
    with open('C:/users/esilgard/desktop/Lung/MASTER_NB_ME_prior_model.txt','w') as f:        
        
        for c in classes:
            f.write(c+'\t'+ str(pOfClass[c])+'\t'+str(math_log(pOfClass[c]))+'\n')
    with open('C:/users/esilgard/desktop/Lung/MASTER_NB_ME_smoothed_model.txt','w') as g:
        for c in classes:
            g.write(c+'\t'+ str(smoothed[c])+'\t'+str(math_log(smoothed[c]))+'\n')
    with open('C:/users/esilgard/desktop/Lung/MASTER_NB_ME_prob_of_word_model.txt','w') as h:
        for c in classes:            
            for word in sorted((wordGivenClass[c]).keys()):
                prob=(wordGivenClass[c])[word]
                h.write(word+'\t'+c+'\t'+str(prob)+'\t'+str(math_log(prob))+'\n')

  
'''output the accuracies from the training and testing accuracy dictionaries'''
def output_acc(classes,string,f,ac):
        
        f.write('Confusion matrix for the '+string+' data: '+'\n'+'row is the truth, column is the system output\n')
        f.write('\t')
        for c in classes:
            f.write(c+'\t')
        f.write('\n')
        count=0;a=0
        for c in classes:
            a+=(ac[c])[c]
            f.write(c+' '+'\t')            
            for l in classes:
                p=(ac[c])[l]
                count+=p
                f.write(str(p)+' '+'\t')
            f.write('\n')
        
        f.write('\n '+string+' accuracy = '+str(float(a)/count)+'\n\n')
            
            
def main():
    classes,training_acc=get_training()
    output_model(classes)
    
    with open('C:/users/esilgard/desktop/Lung/MASTER_NB_ME_output.txt','w') as o:        
        training_acc=output_training(classes,o,training_acc)
        
    with open('C:/users/esilgard/desktop/Lung/MASTER_NB_ME_accuracy.txt','w') as f:
        output_acc(classes,'training',f,training_acc)
        
    


main()
