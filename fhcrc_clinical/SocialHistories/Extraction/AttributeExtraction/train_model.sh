#!/usr/bin/env bash
echo "HELLO TEST"
java -cp $1 edu.stanford.nlp.ie.crf.CRFClassifier -prop $2
