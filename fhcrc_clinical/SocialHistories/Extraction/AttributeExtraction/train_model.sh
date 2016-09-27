#!/usr/bin/env bash
#echo "Param values that made it to the sh script:"
#echo "1 is: $1"
#echo "2 is: $2"
#echo "3 is: $3"
#echo "--------------------------------------------------------------------------------------------------"
export CLASSPATH=$3:$1
echo "Full classpath: $CLASSPATH"
java -cp $CLASSPATH edu.stanford.nlp.ie.crf.CRFClassifier -prop $2
