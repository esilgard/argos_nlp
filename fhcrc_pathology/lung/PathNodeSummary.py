#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from PathNodes import PathNodes

class PathNodeSummary(PathNodes):
    __version__='PathNodeSummary1.0'    
    def __init__(self):        
        self.regex='.*SUMMARY CANCER DATA:.*?([\w\d ]+) nodes:[ ]*Nodes with carcinoma:[ ]*([\d]+)[/ ]*Total nodes examined:[ ]*([\d]+).*'
        self.node_name='PathNodeSummary'
        self.confidence=.95
        self.site_nodes=1
        self.pos_nodes=2
        self.num_nodes=3
       
