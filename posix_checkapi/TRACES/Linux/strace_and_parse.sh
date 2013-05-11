#!/bin/sh

# Usage:
# strace_and_parse.sh <trace_output_name> <program name> [program arguments]
# use by passing the output file first, followed by the command and its 
# arguments

strace -v -f -s1024 -o $@
python parser.py $1 strace

# could add:
# - make sure the trace output file has extension .strace so that the parser 
#   recognizes which parsing method to use automatically. Then the second
#   argument of parser.py can be removed