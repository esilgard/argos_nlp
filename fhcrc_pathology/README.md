fhcrc_pathology
===============

this repository contains scripts and classes for parsing HIDRA pathology reports

path_parser.py is the primary parser
this takes as input a tab delimited text file 
(this requires the FillerOrderNo, SetId, and Observation Value from the HIDRA OBX table and the SpecimenSource and MRN field from the OBR table)
The field names listed above are expected as headers in the first line of the input file - their order with the file does not matter as long as they correctly reference the given columns
path_parser.py returns a dictionary of mrns mapped to pathology accession numbers (FillerOrderNo), mapped to section headers
the section header is a four tuple which consists of (section_order,section_name,initial_character_offset,relevant_specimen_ids) 
and section headers are mapped to unique row numbers, mapped to text

process.py will call whatever classes and modules are listed in the general and disease specific data dictionaries (data_dictionary.txt)
and return a dictionary of "report" objects, containing field names, values, confidence levels, algorithm version names, and a list of character offsets

algorithms inherit from one of the general classes (i.e. OneFieldPerSpecimen, OneFieldPerReport, OneFieldPerReportML, SecondaryField)
SecondaryFields are only instantiated when another field value is found (for example "Metastasis" only gets called if there is an instance of "Histology")
OneFieldPerReportML is a machine learning (relying on scipy, numpy, and scikit learn) version of OneFieldPerReport and it relys on trained language models which are found in the 'models' directory. Within the models directory, each ML aglorithm has a directory by its name.  Within this directory there is a pickled language model file(s) (named for the algorithm and variables in feature selection e.g. svm_model_window7skip2.pkl is a pickled language model file for an svm that uses a window of 7 tokens on either side of appropriate keywords with two skipgrams)and a text file called feature_mapping.txt, which maps lexical features to integers used by a support vector machine.

disease group directories (e.g. 'brain' and 'head&neck') house disease specific metadata and other resources which can be used for general algorithms and/or disease specific algorithms that may override or import in addition to general algorithms