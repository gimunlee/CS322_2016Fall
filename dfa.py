__name__="dfa"

import __main__
DEBUG=__main__.DEBUG #debug flag is migrated

states=[]
symbols=[]
delta={}
initState=""
finalStates=[]

# flags for input files.
flags={"State":False,
        "Input symbol":False,
        "State transition function":False,
        "Initial state":False,
        "Final state":False} 

# functions to read a line of input files for each kind.
def stateReader(line):
  states.extend([q for q in line.split(',') if q!='']) # accumulate possible states except ''
def inputSymbolReader(line):
  symbols.extend([s for s in line.split(',') if s!='']) # accumultate possible input symbols except ''
def transitionFuncReader(line):
  if line!='': # accumulate mapping except blank line
    l=line.split(',')
    delta[(l[0],l[1])]=l[2]
def initStateReader(line):
  if line!='': # assign initial state
    global initState
    initState=line
def finalStateReader(line): # accumulate final states
  finalStates.extend([f for f in line.split(',') if f!=''])
# registering each line reader for each flag
lineReader={None:lambda line: None,
  "State":stateReader,
  "Input symbol":inputSymbolReader,
  "State transition function":transitionFuncReader,
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
  f=open(dfaPath,'r')

  lines=f.read().splitlines()
  currentFlag=None # current reading flag
  for line in lines :
    if countOnFlags() >= len(flags) : # all info read
      break
    if line in flags : # this line is a new flag
      flags[currentFlag]=True
      currentFlag=line
    else : # this line is info
      lineReader[currentFlag](line)
  f.close()
  if DEBUG:
    print("init : %s"%initState)
    print("fina : %s"%finalStates)
    print("delta : %s"%delta)
    print("symbols : %s"%symbols)
    print("states : %s"%states)
def isFinal(state): # predicate for check final states
  return state in finalStates