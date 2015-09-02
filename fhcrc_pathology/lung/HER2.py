#
# Copyright (c) 2015 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
#

'''author@esilgard'''

from OncoplexTesting import OncoplexTesting
print' importing oncoplex class'
class HER2(OncoplexTesting):
    __version__='HER21.0'
    print 1
    def __init__(self):
        print 2
        self.test_name='HER2'
        print 3
        self.regex='.*(HER2|ERBB2).*'
        print 4
