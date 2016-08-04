@echo off
python nlp_engine.py -f sampleData\transfer2.nlp.tsv  -g lung -t pathology -o transfer2.nlp.json

if exist transfer2.nlp.json goto outputJsonOK
echo Smoke test fail, commit rejected. No output json file found in target directory
exit 1

:outputJsonOK
if exist sampleData\transfer2\CN-44-99991.txt goto refFileOK
echo Smoke test fail, commit rejected. Reference file CN-14-99991.txt not found in directory sampleData\transfer2
exit 3

:refFileOK
del transfer2.nlp.json
rmdir /S /Q sampleData\transfer2

exit 0
