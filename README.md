# argos_nlp
=================================================================================================

This is the primary directory for the Fred Hutch natural language processing engine for the parsing of clinical documents and the classification and automated extraction of clinical data elements
----------------------------------------------------------------------------------------------------------------
- command_line_flags.txt 
	a tab delimited text file containing command line flags and their descriptions in the format:
	flag<tab>required/not_required<tab>short_description<tab>long_description
	
	required flags
	~~~~~~~~~~~~~~~~
	* -t = type of report (e.g. 'pathology' or 'cytogenetics')
	* -f = path to the input file
	* -o = name of the output file (this will right to the runtime directory)
	* -g = disease group ('all' will prompt the engine to classify the disease group if the report type == pathology)
	
	optional flags
	~~~~~~~~~~~~~~
	* -ml = machine learning flag, this defaults to 'n' which means the engine will not require the language models needed to run the machine learning algorithms
	* -a = algorithm flag, this defaults to 'y', which means the engine will run appropriate algorithms. If input parameter == 'n', then the engine will simply output text and tsv files.

- global_strings.py
	a set of string variables used in various scripts in this directory

- make_text_output_directory.py
	a python script to create a directory for output text files (the directory location is expected 
	to match the input file name location)

- metadata.json
	a json document that houses all the relevant metadata for all document types, tables, fields, etc. This data is used to parse output and population dropdown fields in the user interface

- metadata.py
	a script to create a dictionary/json object that lists relevant metadata for the batch run 
	(potential fields values, etc)
	this document and disease group specific metadata (full version read in from metadata.json) 
	will be used to population dropdowns in the front end/abstraction LabKey interface

- nlp_engine.py
	the primary script for the natural language processing engine.  This requires a set of flagged command line arguments
	as well as the command_line_flag file which gives their mappings, and input document(s)

- output_results.py
	output the final JSON object to the location specified by the command line -o flag

- version
	a text file with the version number which is automatically updated by the post commit hook script

- schema.json
	a json schema that dictates the appropriate output format for the engine (currently validation is an offline process)
	
- fhcrc_pathology
	directory of modules for processing pathology reports
