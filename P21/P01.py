#-*- coding: utf-8 -*-

DEBUG=False # flag for debug printing.

import sys
sys.path.append("./")

dfaFilePath=""
inputFilePath=""
outputFilePath=""
# flag for path of dfa file
if '--dfa' in sys.argv : dfaFilePath=sys.argv[sys.argv.index('--dfa')+1] 
else :  print("The path of DFA description file not found"); quit(-1)

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

import dfa
# read DFA from file
dfa.read(dfaFilePath)

outputFile=open(outputFilePath,'w')
inputFile=open(inputFilePath,'r')
for line in inputFile.readlines() :
  if DEBUG : print("================"); sys.stdout.write(line)
  if line[:3] == 'end' : break
  currentState=dfa.initState
  for char in line :
    # end of line
    if char == '\n' : 
      if DEBUG :
        if dfa.isFinal(currentState) : print("네")
        else : print("아니오")
      if dfa.isFinal(currentState) : outputFile.write("네\n")
      else : outputFile.write("아니오\n")
      break
    # character in line
    if (currentState,char) in dfa.delta :
      # transition exists
      if DEBUG : print("%3s to %3s by %s"%(currentState,dfa.delta[currentState,char],char))
      currentState=dfa.delta[currentState,char]
    else :
      if DEBUG : print("no transition")
      if DEBUG :
        # if dfa.isFinal(currentState) : print("네")
        # else : print("아니오")
        print("아니오")
      # if dfa.isFinal(currentState) : outputFile.write("네\n")
      # else : outputFile.write("아니오\n")
      # break
      outputFile.write("아니오\n")
      break
outputFile.close()
inputFile.close()

# removing last new line 
outputFile=open(outputFilePath,'r')
buffer=outputFile.read()
outputFile.close()

outputFile=open(outputFilePath,'w')
outputFile.write(buffer[:-1])
outputFile.close()