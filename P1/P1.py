

DEBUG=False # flag for debug printing.

import sys
sys.path.append("../")

# cho= 6
# jung= 13
# jong= 4
# for cho in range(10) :
#     print(chr(0xac00 + (cho*21 + jung) * 28 + jong))

mealyFilePath=""
inputFilePath=""

# flag for path of mealy machine file
if '--mealy' in sys.argv : mealyFilePath=sys.argv[sys.argv.index('--mealy')+1]
else : print("The path of the mealy machine description file not found"); quit(-1) 

# flags for paths of input and output files
if '--input' in sys.argv : inputFilePath=sys.argv[sys.argv.index('--input')+1]
else : print("The path of input file not found"); quit(-1)
#if '--output' in sys.argv : outputFilePath=sys.argv[sys.argv.index('--output')+1]
#else : print("The path of output file not found"); quit(-1)

# flag for debug printing option. 0 for off, 1 for on
if '--debug' in sys.argv :
  if sys.argv[sys.argv.index('--debug')+1] == '1' :
    DEBUG=True
  else :
    DEBUG=False

import mealy
# read Mealy machine from file
mealy.read(mealyFilePath)

inputFile=open(inputFilePath,'r')
for line in inputFile.readlines() :
    if DEBUG : print("========="); sys.stdout.write(line)
    outputLine = ""
    currentState=mealy.initState
    for char in line :
        if char == '\n' :
            break
        if (currentState, char) in mealy.delta :
            #transition exists
            if DEBUG : print("%3s to %3s by %s"%(currentState,mealy.delta[currentState,char],char))
            if (currentState,char) in mealy.lamb :
                outputLine = outputLine+mealy.lamb[currentState,char]
            currentState=mealy.delta[currentState,char]
        else :
            # no transition
            ouputLine="No path exists!"
            break
    print(outputLine)
inputFile.close()