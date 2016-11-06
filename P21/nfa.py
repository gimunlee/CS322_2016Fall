__name__="nfa"

import __main__
DEBUG=__main__.DEBUG #debug flag is migrated

states=set()
symbols=set()
delta={}
initState=""
finalStates=set()
eclosures=[]

def printNfa() :
  print("== NFA ==")
  print("init : %s"%initState)
  print("fina : %s"%finalStates)
  print("delta : %s"%delta)
  print("symbols : %s"%symbols)
  print("states : %s"%states)
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
  if DEBUG: printNfa()
  groupEClosures()
  subsetConstruction()
  minimize()
def isFinal(state): # predicate for check final states
  return state in finalStates

def groupEClosures():
  global states, delta, initState, finalStates
  newDelta={}
  statesMap={}
  newStates=set()
  newInitState=""
  newFinalStates=set()

  queue=[]
  queueIndex=0

  #referencing. for efficiency.
  keys=delta.keys()

  closure=set()
  while len(queue) < len(states):
    if queueIndex == len(queue) : # End of BFS
      state=(states-set(queue)).pop() # Extract not queued state
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
        if q in closure :
          continue
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
          queue.append(q)

    queueIndex+=1

  if DEBUG :
    print("eclosures : %s"%eclosures)

  #Build new states after grouping epsilon closure
  i=0
  for i in range(len(eclosures)) :
    newState="qe%d"%i
    newStates.update(set([newState]))
    for q in eclosures[i] :
      statesMap[q]=newState
  if DEBUG :
    print("new States : %s"%newStates)
    print("new States map : %s"%statesMap)
  
  #Accumulate delta to newDelta
  for p in delta.keys() :
    q, s = p
    if s=='E' :
      continue
    for q2 in delta[(q,s)] :
      if not ((statesMap[q],s) in newDelta) :
        newDelta[(statesMap[q],s)]=set([statesMap[q2]])
      else :
        newDelta[(statesMap[q],s)].add(statesMap[q2])
  if DEBUG : print("new delta : %s"%newDelta)
  
  newInitState=statesMap[initState]
  for f in finalStates :
    newFinalStates.add(statesMap[f])
  if DEBUG :
    print("newInitState : %s"%newInitState)
    print("newFinalStates : %s"%newFinalStates)

  states, delta, initState, finalStates = newStates, newDelta, newInitState, newFinalStates
  if DEBUG : printNfa()
  
#Subset construction
def getAllSubsets(remainedStates) :
  if len(remainedStates)==0 :
    return set()
  if len(remainedStates)==1 :
    t=set()
    t.add(frozenset())
    # t.add(tuple())
    t.add(frozenset((remainedStates[0],)))
    return t
  tempSubsets=set()
  for subset in getAllSubsets(remainedStates[1:]) :
    tempSubsets.add(subset)
    tempSubsets.add(subset.union(frozenset((remainedStates[0],))))
  return tempSubsets
def subsetConstruction() :
  global states, delta, initState, finalStates
  newStates=set()
  newDelta={}
  newInitState=''
  newFinalStates=set()

  subsets = getAllSubsets(list(states))
  statesMap = {}
  reverseMap = {}##########
  i=0
  for subset in subsets :
    newState="qs%d"%i
    i+=1
    statesMap[subset]=newState
    reverseMap[newState]=subset

  if DEBUG : print("statesMap : %s"%statesMap)

  # if delta[(initState,'a')] == delta[(initState,'b')] :
  #   pass
  if DEBUG : print("temp Final states : %s"%finalStates)
  for subset in subsets :
    #Add as final states
    if len(subset.intersection(finalStates))>0 :
      newFinalStates.add(statesMap[subset])
    for s in symbols :
      subset2 = set()
      for q in subset :
        if (q,s) in delta :
          for q2 in delta[(q,s)] :
            subset2.add(q2)
      newDelta[(statesMap[subset],s)]=statesMap[frozenset(subset2)]
  states=list(statesMap.values())
  delta=newDelta
  initState=statesMap[frozenset([initState])]

  finalStates=set()

  queue=[initState]
  queueIndex=0
  newStates=set()
  newDelta={}
  while queueIndex<len(queue) :
    state = queue[queueIndex]
    if state in newFinalStates :
      finalStates.add(state)
    newStates.add(state)
    for s in symbols :
      if (state, s) in delta.keys() :
        q2 = delta[(state,s)]
        newDelta[(state,s)]=q2
        if not(q2 in newStates) :
          queue.append(q2)
    queueIndex+=1
  delta = newDelta
  states = newStates

  if DEBUG:
    printNfa()
    printDelta()

partitions=[]
def minimize() :
  global partitions
  symbolsTuple=tuple(symbols)
  print(symbolsTuple)
  
  partitions.append(frozenset(finalStates))
  partitions.append(frozenset(states.difference(finalStates)))

  def indexAmongPartitions(q) :
    global partitions
    for part in partitions :
      if q in part :
        return partitions.index(part)
    return -1
  def indexesAmongPartitions(q) :
    tempList=[]
    for s in symbolsTuple :
      tempList.append( indexAmongPartitions(delta[(q,s)]) )
    return tuple(tempList)
  global states, delta, iniState, finalStates
  
  if DEBUG :
    print("partitions : %s"%partitions)

  distinguished=True
  while distinguished :
    distinguished=False
    newPartitions=set()
    for part in partitions :
      partList=list(part)
      partList.sort(key=indexesAmongPartitions)

      tempPart=set()
      tempPart.add(partList[0])
      tempIndexes=indexesAmongPartitions(partList[0])
      for state in partList[1:] :
        if tempIndexes == indexesAmongPartitions(state) :
          tempPart.add(state)
        else :
          distinguished=True
          newPartitions.add(frozenset(tempPart))
          tempPart.clear()
          tempPart.add(state)
          tempIndexes=indexesAmongPartitions(state)
      newPartitions.add(frozenset(tempPart))
    partitions=list(newPartitions)
  for part in partitions :
    print(part)
  print("min_states : %d"%len(partitions))