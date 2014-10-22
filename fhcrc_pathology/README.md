fhcrc_pathology
===============

this repository containts a handful of scripts for parsing amalga pathology reports

path_parser.py is the primary parser
	taking as input a tab delimited text file (ala the Amalga OBX table)	
	returning a dictionary of mrns mapped to pathology accession numbers, mapped to section headers, mapped to unique row numbers, mapped to text

path_parser_tester.py is the script that calls the path_parser module
	it expects one command line argument:  the path to the tab delimited text file that contains the pathology reports
	it will return any number of error messages for format or parsing errors
	or it will return a successful message upon completion (all printed to standard out)

