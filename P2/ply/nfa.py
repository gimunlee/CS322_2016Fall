__name__="nfa"

import __main__
DEBUG=__main__.DEBUG #debug flag is migrated

FORMEALY=False

DEAD_STATE = 'dead_state'
DEAD_STATE_SET = frozenset([DEAD_STATE])

EPSILON = 'EPSILON'

states=set()
symbols=set()
delta={}
initState=""
finalStates=set()
eclosures=[]
partitions=[]

def reset() :
  global states, symbols, delta, initState, finalStates, eclosures
  states=set()
  symbols=set()
  delta={}
  initState=""
  finalStates=set()
  eclosures=[]
  partitions=[]

# Output description of m-dfa
def toString() :
  outputs=[]
  outputs.append("State")
  outputs.append(','.join(states))

  outputs.append('Input symbol')
  outputs.append(','.join(symbols))

  outputs.append('State transition function')
  tempStatesQueue=[initState]
  i=0
  while i<len(states) :
    tempState = tempStatesQueue[i]
    if FORMEALY :
      outputs.append("##"+tempState)
      outputs.append("State transition function")
    for c in symbols :
      if(tempState,c) in delta :
        outputs.append(','.join([tempState,c,delta[(tempState,c)]]))
        if not(delta[(tempState,c)] in tempStatesQueue) :
          tempStatesQueue.append(delta[(tempState,c)])
    if FORMEALY :
      outputs.append("Output function")
      for c in symbols :
        if(tempState,c) in delta :
          outputs.append(tempState+","+c+",")
    i+=1

  # for q in states :
  #   for c in symbols :
  #     if (q,c) in delta :
  #       outputs.append(','.join([q,c,delta[(q,c)]]))

  # for d in delta :
  #   outputs.append( ','.join([d[0],d[1],delta[d]]) )

  outputs.append('Initial state')
  outputs.append(initState)

  outputs.append("Final state")
  outputs.append(','.join(finalStates))
  return '\n'.join(outputs)

#for debugging
def printNfa(prompt="NFA") :
  print("==%s=="%prompt)
  print("init : %s"%initState)
  print("fina : %s"%finalStates)
  print("delta : %s"%delta)
  print("symbols : %s"%symbols)
  print("states : %s"%states)
  print("==%s=="%('='*len(prompt)))
def printDelta() :
  print("=-=-=-=-=-=- delta -=-=-=-=-=-=")
  for q in sorted(list(states)) :
    for s in sorted(list(symbols)) :
      if (q,s) in delta :
        print("%s(%s) => %s"%(q,s,delta[(q,s)]))

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

# read nfa from string
def readString(nfaStr):
  lines=nfaStr.splitlines()
  currentFlag=None # current reading flag
  for line in lines :
    if countOnFlags() >= len(flags) : # all info read
      break
    if line in flags : # this line is a new flag
      flags[currentFlag]=True
      currentFlag=line
    else : # this line is info
      lineReader[currentFlag](line)
  if DEBUG: printNfa('Read e-NFA')
# read nfa from file
def read(nfaPath):
  f=open(nfaPath,'r')

  readString(f.read())

# Converting e-nfa to m-dfa. Subset construction with e-closures and minimization
def convert() :
  global states, initState, finalStates, delta, symbols, eclosures
  eClosures={}
  def eClose(q) : # ECLOSE from single NFA state
    queue=[q]
    closure = set()
    closure.add(q)

    queueIndex=0
    while queueIndex < len(queue) :
      state = queue[queueIndex]
      if (state,EPSILON) in delta :
        for q2 in delta[(state,EPSILON)] :
          if not(q2 in closure) :
            queue.append(q2)
            closure.add(q2)
      queueIndex+=1
    return frozenset(closure)
  for q in states :
    eClosures[q]=eClose(q)
  if DEBUG: print("EClosures : %s"%str(eClosures))

  #Subset construction with e-closures
  newInitState = eClosures[initState]
  newStates = [newInitState]
  newFinalStates = set()
  newDelta = {}
  statesMap = {}

  pIndex = 0
  while pIndex < len(newStates) :
    P = newStates[pIndex]
    for s in symbols :
      Q = set()
      for p in P :
        if (p,s) in delta :
          Q.update(delta[(p,s)])
      newQ = Q.copy()
      for q in Q :
        newQ.update(eClosures[q])

      newState = frozenset(newQ)
      if not(newState in newStates) : newStates.append(newState) # Enlist newly recognized State
      newDelta[(P,s)] = newState
    
    if len(finalStates.intersection(P)) > 0 :
      if DEBUG: print(P)
      newFinalStates.add(P) # Enlist as a final State

    # Numbering new states from subset construction
    if P == frozenset() : statesMap[P]=DEAD_STATE 
    else : statesMap[P]="qd%d"%pIndex

    pIndex+=1

  # Overwriting
  initState = statesMap[newInitState]
  states = set(map(statesMap.get,newStates))
  finalStates = set(map(statesMap.get,newFinalStates))
  delta={}
  for newQ in newStates :
    for s in symbols :
      if (newQ, s) in newDelta :
        delta[(statesMap[newQ],s)]=statesMap[newDelta[(newQ,s)]]
  
  if DEBUG : printNfa('converted DFA')

  minimize() # Minimizing DFA

  if DEBUG : printNfa('minimized DFA')

def isFinal(state): # predicate for check final states
  return state in finalStates
def minimize() :
  global partitions
  global states, delta, initState, finalStates, symbols, eclosures
  symbolsTuple=tuple(symbols)

  partitions=[]
  
  #Initial partition.
  partitions.append(frozenset(finalStates))
  if DEAD_STATE in states : partitions.append(DEAD_STATE_SET)
  partitions.append(frozenset(states.difference(finalStates).difference(DEAD_STATE_SET)))

  def indexAmongPartitions(q) :
    global partitions
    for part in partitions :
      if q in part :
        return partitions.index(part)
  def indexesAmongPartitions(q) :
    global partitions, delta, symbols
    symbolsTuple = tuple(symbols)
    tempList=[]
    for s in symbolsTuple :
      tempList.append( indexAmongPartitions(delta[(q,s)]) )
    return tuple(tempList)

  #Repeat until any more distinguishable partition not appears
  distinguished=True
  while distinguished :
    distinguished=False
    newPartitions=set()
    for part in partitions :
      if len(part) ==0 :
        continue
      partList=list(part)
      partList.sort(key=indexesAmongPartitions)

      tempPart=set()
      tempPart.add(partList[0])
      tempIndexes=indexesAmongPartitions(partList[0])
      for state in partList[1:] :
        if tempIndexes == indexesAmongPartitions(state) : # Existing indexes. not distinguishable yet
          tempPart.add(state)
        else : # distinguishable indexes found.
          distinguished=True
          newPartitions.add(frozenset(tempPart)) # enlist distinguishable
          tempPart.clear()
          tempPart.add(state)
          tempIndexes=indexesAmongPartitions(state)
      newPartitions.add(frozenset(tempPart)) # preserve last partition
    partitions=list(newPartitions)
  if DEBUG:  print(partitions)

  # Numbering remained partitions
  partitionsMap={}
  for i in range(len(partitions)) :
    if partitions[i]==DEAD_STATE_SET : partitionsMap[partitions[i]]=DEAD_STATE
    else : partitionsMap[partitions[i]]="qm%d"%i
  
  newInitState = initState
  newFinalStates = set()
  newStates = set()
  newDelta = {}
  for part in partitions :
    if partitionsMap[part] == DEAD_STATE : continue # constructing new delta, except dead state
    newStates.add(partitionsMap[part])
    if initState in part : newInitState = partitionsMap[part]
    if len(finalStates.intersection(part))>0 :
      newFinalStates.add(partitionsMap[part])

    q=list(part)[0]
    for s in symbols :
      if (q, s) in delta :
        q2 = delta[(q,s)]
        if q2 == DEAD_STATE : continue #except dead state
        for part2 in partitions :
          if q2 in part2 : newDelta[(partitionsMap[part],s)] = partitionsMap[part2]

  initState, finalStates, states, delta = newInitState, newFinalStates, newStates, newDelta