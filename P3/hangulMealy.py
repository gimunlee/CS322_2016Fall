#-*- coding: utf-8 -*-
if __name__!='__main__' :
  __name__="hangulMealy"

  import __main__
  DEBUG=__main__.DEBUG #debug flag is migrated
else :
  DEBUG=True

states=[]
inputSymbols=[]
delta={}
outputSymbols=[]
lamb={}
initState=""
finalStates=[]

# flags for input files.
flags={"State":False,
        "Input symbol":False,
        "State transition function":False,
        "Output symbol":False,
        "Output function":False,
        "Initial state":False,
        "Final state":False} 

# functions to read a line of input files for each kind.
def stateReader(line):
  states.extend([q for q in line.split(',') if q!='']) # accumulate possible states except ''
def inputSymbolReader(line):
  inputSymbols.extend([s for s in line.split(',') if s!='']) # accumultate possible input inputSymbols except ''
def transitionFuncReader(line):
  if line!='': # accumulate mapping except blank line
    l=line.split(',')
    delta[(l[0],l[1])]=l[2]
def outputSymbolReader(line):
  outputSymbols.extend([s for s in line.split(',') if s!='']) # accumulate possible input outputSymbols except ''
def outputFuncReader(line):
  if line!='': # accumulate mapping except blank line
    l=line.split(',')
    lamb[(l[0],l[1])]=l[2:]
def initStateReader(line):
  if line!='': # assign initial state
    global initState
    initState=line
def finalStateReader(line):
  if line!='':
    global finalStates
    finalStates.extend([q for q in line.split(',') if q!=''])
lineReader={None:lambda line: None,
  "State":stateReader,
  "Input symbol":inputSymbolReader,
  "State transition function":transitionFuncReader,
  "Output symbol":outputSymbolReader,
  "Output function":outputFuncReader,
  "Initial state":initStateReader,
  "Final state":finalStateReader}

# count of flags already read
def countOnFlags() :
  count=0
  for key in flags :
    if flags[key] :
      count+=1
  return count

# read DFA from file
def read(dfaPath):
  f=open(dfaPath,'r',-1,'utf-8')

  lines=f.read().splitlines()
  currentFlag=None # current reading flag
  for line in lines :
    if len(line)>0 and line[0]=='#' :
      continue
    if countOnFlags() >= len(flags) : # all info read
      break
    if line in flags : # this line is a new flag
      flags[currentFlag]=True
      currentFlag=line
    else : # this line is info
      lineReader[currentFlag](line)
  f.close()
  if DEBUG:
    pass
    # print("init : %s"%initState)
    # print("delta : %s"%delta)
    # print("inputSymbols : %s"%inputSymbols)
    # print("lambda : %s"%lamb)
    # print("outputSymbols : %s"%outputSymbols)
    # print("states : %s"%states)

    # for s in states :
    #   for isym in inputSymbols :
    #     print(lamb[s,isym])