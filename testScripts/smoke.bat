@echo off
python ..\nlp_engine.py -f sampleData\transfer2.nlp.tsv  -g lung -t pathology -o transfer2.nlp.json

if exist transfer2.nlp.json goto outputJsonOK
echo Smoke test fail, commit rejected. No output json file found in target directory
exit 1

:outputJsonOK
if exist sampleData\transfer2\CN-14-99991.txt goto validateJSON
echo Smoke test fail, commit rejected. Reference file CN-14-99991.txt not found in directory sampleData\transfer2
exit 3

:validateJSON
start python testScripts\schema_validation.py "..\schema.json" "transfer2.nlp.json"
if errorlevel 1 goto exitOne
goto refFileOK

:refFileOK
del transfer2.nlp.json
rmdir /S /Q sampleData\transfer2

exit 0

:exitOne
exit 1