fhcrc_pathology
===============

this repository contains scripts and classes for parsing HIDRA pathology reports

path_parser.py is the primary document parser
-This takes as input a tab delimited text file 
(this requires the FillerOrderNo, SetId, and Observation Value from the HIDRA OBX table and the SpecimenSource and MRN field from the OBR table)

-The field names listed above are expected as headers in the first line of the input file - their order within the file does not matter as long as they correctly reference the given columns and are an exact string match to the variables in the global_strings.py module

-path_parser.py returns a dictionary of mrns mapped to pathology accession numbers (FillerOrderNo), mapped to section headers
the section header is a four tuple which consists of (section_order,section_name,initial_character_offset,relevant_specimen_ids) 
and section headers are mapped to unique row numbers, mapped to text

-process.py will call whatever classes and modules are listed in the general and disease specific data dictionaries (data_dictionary.txt)
and return a dictionary of "report" objects, containing field names, values, confidence levels, algorithm version names, and a list of character offsets

-Algorithms inherit from one of the general classes (i.e. OneFieldPerSpecimen, OneFieldPerReport, OneFieldPerReportML, SecondaryField)
-SecondaryFields are only instantiated when another field value is found (for example "Metastasis" only gets called if there is an instance of "Histology")

-OneFieldPerReportML is a machine learning (relying on scipy, numpy, and scikit learn) version of OneFieldPerReport and it relys on trained language models which are found in the 'models' directory. Within the models directory, each ML aglorithm has a directory by its name.  Within this directory there is a pickled language model file(s) (named for the algorithm and variables in feature selection e.g. svm_model_window7skip2.pkl is a pickled language model file for an svm that uses a window of 7 tokens on either side of appropriate keywords with two skipgrams)and a text file called feature_mapping.txt, which maps lexical features to integers used by a support vector machine.
*Note: these language models are not a part of the public repository because they contain features extracted from raw text files and therefore may contain PHI

-disease group directories (e.g. 'brain' and 'head_neck') house disease specific metadata and other resources which can be used for general algorithms and/or disease specific algorithms that may override or import in addition to general algorithms
