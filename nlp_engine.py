## test command line parsing ##
import sys



## path to file containing flags and descriptions ##
## in the format -char<tab>description<tab>verbose_description(for help and error messages) ##
try:
    command_line_flag_file='command_line_flags.txt'
except:
    print '\nFATAL ERROR: command line flag file not found.  program aborted.';sys.exit()

## set of required flags for program to run successfully ##
required_flags=set([])

## dictionary of flag:tuple(flag description,verbose flag description) ##
command_line_flags={}
for line in open(command_line_flag_file,'r').readlines():
    line=line.strip().split('\t')
    if line[1]=='required': required_flags.add(line[0])
    command_line_flags[line[0]]=(line[2],line[3])

## dictionary of actual flags:argument values ##
arguments={}

args=sys.argv[1:]


for index in range(0,len(args)-1,2):
    
    if args[index] in command_line_flags:
        arguments[args[index]]=args[index+1]
    else:
        print 'nonfatal error:  unrecognized flag: '+args[index]+' this flag will be excluded from the arguments\n\
        refer to '+command_line_flag_file+' for a complete list and description of command line flags\n'
    
missing_flags=required_flags-set(arguments.keys())
if len(missing_flags)>0:
    for each_flag in missing_flags:
        print 'ERROR: missing required flag: "'+each_flag+'" '+command_line_flags[each_flag][1]
    print '\nFATAL ERROR: cannot proceed without all required flags. program aborted.';sys.exit()
else:
    print arguments
