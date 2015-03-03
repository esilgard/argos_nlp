@echo off
python nlp_engine.py -f sampleData/smoke_test.nlp.tsv  -g lung -t pathology -o smoke_test.nlp.json

if exist smoke_test.nlp.json goto outputJsonOK
echo Smoke test fail, commit rejected. No output json file found in target directory
exit 1

:outputJsonOK
if exist sampleData\smoke_test\CN-14-99991.txt goto refFileOK
echo Smoke test fail, commit rejected. Reference file CN-14-99991.txt not found in directory sampleData\smoke_test
exit 3

:refFileOK
del smoke_test.nlp.json
rmdir /S /Q sampledata\smoke_test

exit 0
