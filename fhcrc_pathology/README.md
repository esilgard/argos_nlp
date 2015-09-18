fhcrc_pathology
===============

this repository contains a handful of scripts for parsing HIDRA pathology reports

path_parser.py is the primary parser
this takes as input a tab delimited text file 
(this requires the FillerOrderNo, SetId, and Observation Value from the HIDRA OBX table and the SpecimenSource and MRN field from the OBR table)
The field names listed above are expected as headers in the first line of the input file - their order with the file does not matter as long as they correctly reference the given columns
path_parser.py returns a dictionary of mrns mapped to pathology accession numbers (FillerOrderNo), mapped to section headers
the section header is a four tuple which consists of (section_order,section_name,initial_character_offset,relevant_specimen_ids) 
and section headers are mapped to unique row numbers, mapped to text

process_pathology will call whatever classes and modules are listed in the general and disease specific data dictionaries
and return a dictionary of "report" objects, containing field names, values, confidence levels, algorithm version names, and a list of character offsets

