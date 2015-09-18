#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from PathStage import PathStage

class PathStageT(PathStage):    
    __version__='PathStageT1.0' 	
    def __init__(self):
        self.stage_name='PathStageT'
        self.regex=r'.*((pT|yT)[012345][abc]?).*'
        self.confidence=("%.2f" % .98)
		
		
	
