''' author @ esilgard '''
#
# Copyright (c) 2014-2016 Fred Hutchinson Cancer Research Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from datetime import datetime
__version__ = 'make_datetime1.0'

def get(date_tuple, format_string):
    '''
       takes a tuple of (year,month,day) and a datetime format string
       returns python date object
     '''
    ## verify expected format before attempting to parse
    if isinstance(date_tuple, tuple) and len(date_tuple) == 3:
        if len(date_tuple[1]) == 1:
            month = '0' + date_tuple[1]
        else:
            month = date_tuple[1]
        if len(date_tuple[2]) == 1:
            day = '0' + date_tuple[2]
        else:
            day = date_tuple[2]
        a = datetime.strptime((date_tuple[0] + ',' + month + ',' + day), format_string)
        date_obj = a.date()
        return str(date_obj)
    else:
        return None
