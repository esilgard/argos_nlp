#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from PathStage import PathStage

class PathStageSystem(PathStage):    
    __version__='PathStageSystem1.0' 	
    def __init__(self):
        self.stage_name='PathStageSystem'
        self.regex=r'.*(AJCC[ ,]+[0-9]{1,2})[ thsnd]+ed.*'   
		
		
	
