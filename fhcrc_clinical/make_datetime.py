#
# Copyright (c) 2014-2015 Fred Hutchinson Cancer Research Center
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

''' author @ esilgard '''
__version__='make_datetime1.0'
from datetime import datetime

'''
   takes a tuple of (year,month,day) and a datetime format string
   returns python datetime object (in string form for serializable JSON jump)
'''

## for dates - acceptable incoming format: tuple_date eg(2015,1,5) or (2015,Jan,05)
def get_date(date_tuple,format_string):
    ## verify expected format before attempting to parse
    if type(date_tuple)==tuple and len(date_tuple)==3:
        if len(date_tuple[1])==1:
            month='0'+date_tuple[1]
        else:   month=date_tuple[1]
        if len(date_tuple[2])==1:
            day='0'+date_tuple[2]
        else:   day=date_tuple[2]
        date_tuple=datetime.strptime(date_tuple[0]+','+month+','+day,format_string) 
        return date_tuple
    else:
        return 'NA'


## for dates with times - expected incoming format:  tuple_date eg(2015,1,5), tuple_time eg (20:15)
## ******** right now we're not dealing with AM_PM - so these times are sort of useless ********
def get_datetime(date_tuple,time_list,format_string):
    
    ## verify expected format before attempting to parse
    if type(date_tuple)==tuple and len(date_tuple)==3 and type(time_list)==list:
        if len(date_tuple[1])==1:
            month='0'+date_tuple[1]
        else:   month=date_tuple[1]
        if len(date_tuple[2])==1:
            day='0'+date_tuple[2]
        else:   day=date_tuple[2]
        if len(time_list[0])==1:
            time_list[0]='0'+time_list[0]
        
        date_tuple=datetime.strptime(date_tuple[0]+','+month+','+day+','+','.join(time_list),format_string)
        return date_tuple
    else:
        return 'NA'
