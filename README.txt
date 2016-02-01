--author@esilgard--

This is the primary directory for the HIDRA (Hutch Integraded Data Repository and Archive) natural language processing engine for the parsing of clinical documents and the 
classification and automated extraction of clinical data elements

command_line_flags.txt 
	a tab delimited text file containing command line flags and their descriptions in the format:
	flag<tab>required/not_required<tab>short_description<tab>long_description

global_strings.py
	a set of string variables used in various scripts in this directory

nlp_engine.py
	the primary script for the natural language processing engine.  it requires a set of flagged command line arguments, as well as the command_line_flag file which gives their mappings, and input document(s)

fhcrc_pathology
	directory of modules for processing pathology reports

make_text_output_directory.py
	a python script to create a directory for output text files (the directory location is expected to match the input file name location)

output_results.py
	output the final JSON object to the location specified by the command line -o flag
	
version
	a text file with the version number which is automatically updated by the pre commit hook script

metadata.py
	a script to create a dictionary/json object that lists relevant metadata for the batch run (potential fields values, etc)
	this document and disease group specific metadata (full version read in from metadata.json) will be used to population dropdowns in the front end/abstraction interface

metadata.json
	a json document that houses all the relevant metadata for all document types, tables, fields, etc. This data is used to parse output and population dropdown fields in the user interface

schema.json
	a json schema that dictates the appropriate output format for the engine (currently validation is an offline process)