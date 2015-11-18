#
# Copyright (c) 2013-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
''' author@esilgard '''
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys, json

def get(nlp_engine_path, arguments):
    '''
    read in full json metadata dictionary from resource file
    return metadata dictionary of relavent fields for the given
    document and disease group
    '''
    ## path to file containing the metadata dictionary (in json format) ##
    try:
        meta_data_file = open(nlp_engine_path + 'metadata.json', 'r')
        groupings_file = open(nlp_engine_path + 'grouping.json', 'r')
        try:
            metadata_d = json.load(meta_data_file)
            meta_data_file.close()
            grouping_d = json.load(groupings_file)
            groupings_file.close()
        except RuntimeError:
            sys.stderr.write('FATAL ERROR: json could not load metadata dictionary \
                    file or the UI groupings file, potential formatting error')
            sys.exit(1)
    except IOError:
        sys.stderr.write('FATAL ERROR: either metadata dictionary or groupings file not found')
        sys.exit(1)
    ## only output the appropriate metadata for the given document type
    metadata_d = metadata_d.get(arguments.get('-t'))

    return metadata_d, grouping_d
