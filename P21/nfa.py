__name__="nfa"

import __main__
DEBUG=__main__.DEBUG #debug flag is migrated

states=set()
symbols=set()
delta={}
initState=""
finalStates=set()

# flags for input files.
flags={"State":False,
        "Input symbol":False,
        "State transition function":False,
        "Initial state":False,
        "Final state":False} 

# functions to read a line of input files for each kind.
def stateReader(line):
  states.update(set([q for q in line.split(',') if q!='']))
  # states.extend() # accumulate possible states except ''
def inputSymbolReader(line):
  symbols.update(set([s for s in line.split(',') if s!=''])) # accumultate possible input symbols except ''
def transitionFuncReader(line):
  if line!='': # accumulate mapping except blank line
    l=line.split(',')
    if (l[0],l[1]) in delta :
      delta[(l[0],l[1])].update(set([l[2]]))
    else :
      delta[(l[0],l[1])]=set([l[2]])
def initStateReader(line):
  if line!='': # assign initial state
    global initState
    initState=line
def finalStateReader(line): # accumulate final states
  finalStates.update(set([f for f in line.split(',') if f!='']))
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

# read nfa from file
def read(nfaPath):
  f=open(nfaPath,'r')

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

def groupEClosures():
  queue=[]
  queueIndex=0
  eclosures=[]

  #referencing. for efficiency.
  keys=delta.keys()

  closure=set()
  while len(queue) < len(states):
    if queueIndex == len(queue) : # End of BFS
      state=(states-set(queue)).pop()
      nCheckedClosures=0
      for tempClosure in reversed(eclosures) : # Search a closure that include 'state'
        if state in tempClosure :
          closure=tempClosure
          break
        nCheckedClosures+=1
      if nCheckedClosures==len(eclosures) : # If there isn't, enlist another closure
        closure=set([state])
        queue.append(state)
        eclosures.append(closure)
    else :
      state=queue[queueIndex]

    # closure : the closure running in BFS

    #Adding epsilon-ee from 'state'
    if (state,'E') in keys :
      #Check if epsilon-ee is forming a closure already
      for q in delta[(state,'E')] :
        nCheckedClosures=0
        for tempClosure in reversed(eclosures) :
          if q in tempClosure : # If it is, unite existing closure, then remove the older one.
            closure.update(tempClosure)
            eclosures.remove(tempClosure)
            nCheckedClosures = -1
            break
          nCheckedClosures+=1
        if nCheckedClosures==len(eclosures) : # If not, just add itslef
          closure.update(set([q])) 
      queue.extend(delta[(state,'E')])

    queueIndex+=1

  print("eclosures : %s"%eclosures)