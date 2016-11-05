#-*- coding: utf-8 -*-

DEBUG=False # flag for debug printing.

import sys
sys.path.append("./")

nfaFilePath=""
inputFilePath=""
outputFilePath=""
# flag for path of nfa file
if '--nfa' in sys.argv : nfaFilePath=sys.argv[sys.argv.index('--nfa')+1] 
else :  print("The path of NFA description file not found"); quit(-1)

# flags for paths of input and output files
if '--input' in sys.argv : inputFilePath=sys.argv[sys.argv.index('--input')+1]
else : print("The path of input file not found"); quit(-1)
if '--output' in sys.argv : outputFilePath=sys.argv[sys.argv.index('--output')+1]
else : print("The path of output file not found"); quit(-1)

# flag for debug printing option. 0 for off, 1 for on
if '--debug' in sys.argv :
  if sys.argv[sys.argv.index('--debug')+1] == '1' :
    DEBUG=True
  else :
    DEBUG=False

import nfa
# read nfa from file
nfa.read(nfaFilePath)

outputFile=open(outputFilePath,'w')
inputFile=open(inputFilePath,'r')
outputFile.close()
inputFile.close()

# removing last new line 
outputFile=open(outputFilePath,'r')
buffer=outputFile.read()
outputFile.close()

outputFile=open(outputFilePath,'w')
outputFile.write(buffer[:-1])
outputFile.close()

nfa.groupEClosures()