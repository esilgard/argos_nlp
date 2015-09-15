#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from PathStage import PathStage

class PathStageN(PathStage):
    __version__='PathStageN1.0'
    
    def __init__(self):
        self.stage_name='PathStageN'
        self.regex=r'.*(pN[0123][abc]?).*'
        self.confidence=.9
