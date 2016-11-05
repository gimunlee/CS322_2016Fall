#-*- coding: utf-8 -*-
# print(int("10",16))
DEBUG=False # flag for debug printing.
# print(hex(ord('ㄷ')))
import sys
sys.path.append("../")

codeToJamo={
    'cho':['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'],
    'jung':['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'],
    'jong':['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
    }
def jamoCode(position,jamo) :
    return codeToJamo[position].index(jamo)
doubleJaums={
    'ㄳ':('ㄱ','ㅅ'),'ㅄ':('ㅂ','ㅅ'),
    'ㄵ':('ㄴ','ㅈ'),'ㄶ':('ㄴ','ㅎ'),
    'ㄺ':('ㄹ','ㄱ'),'ㄻ':('ㄹ','ㅁ'),'ㄼ':('ㄹ','ㅂ'),'ㄽ':('ㄹ','ㅅ'),'ㄾ':('ㄹ','ㅌ'),'ㄿ':('ㄹ','ㅌ'),'ㄿ':('ㄹ','ㅍ'),'ㅀ':('ㄹ','ㅎ')
}
# print(codeToJamo['cho'].index('ㄴ'))

# detailStack.append detailStack.pop()
stack=[]
def pushStack(stackEntry) :
    global stack
    if len(stack)>8 :
        stack=stack[1:]+[stackEntry]
    else :
        stack.append(stackEntry)
def cleanStackExcept(exc) :
    global stack
    cleanCount=len(stack)-exc
    if cleanCount>0 :
        stack=stack[cleanCount:]
# for i in range(10) :
#     pushStack(i)
# cleanStackExcept()
# print(stack)

# cho= 6
# jung= 13
# jong= 4
# # for cho in range(10) :
# print(chr(0xac00 + (cho*21 + jung) * 28 + jong))
def hangulCodepoints(t) :
    #triple of cho, jung, jong
    # print(type(t))
    # if type(t) is int :
    #     return t
    if (type(t) is list) or (type(t) is tuple):
        return {'mo':lambda:t[1],
        'cho':lambda:ord(codeToJamo['cho'][t[1][0]]),
        'jung':lambda:0xac00+t[1][0]*21*28+t[1][1]*28,
        'jong':lambda:0xac00+t[1][0]*21*28+t[1][1]*28+t[1][2]
        }[t[0]]()
def strFromCodepoints(cps) :
    return "".join([chr(x) for x in map(hangulCodepoint,cps)])
# print(strFromCodepoints([(6,13,4),(7,13,4),(8,13,4)]))

mealyFilePath=""
inputFilePath=""

# flag for path of hangulMealy machine file
if '--hangulMealy' in sys.argv : mealyFilePath=sys.argv[sys.argv.index('--hangulMealy')+1]
else : print("The path of the hangulMealy machine description file not found"); quit(-1) 

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

import hangulMealy
# read hangulMealy machine from file
hangulMealy.read(mealyFilePath)

outputLine=[]
def lambTranslate(args) :
    def new() :
        global outputLine
        cleanStackExcept(1)
        {'cho':lambda:outputLine.append(['cho',tuple([jamoCode('cho',args[2])])]),
        'mo':lambda:outputLine.append(['mo',ord(args[2])])
        }[args[1]]()
        if len(outputLine)>=2 and not outputLine[-2][-1] is 'completed':
            outputLine[-2].append('completed')
    def newWithPrevJong() :
        global outputLine
        global stack
        cleanStackExcept(2)
        outputLine[-1].append('completed')
        prevJong=codeToJamo['jong'][outputLine[-1][1][2]]
        if prevJong in codeToJamo['cho'] :
            outputLine[-1][0]='jung'
            outputLine[-1][1]=outputLine[-1][1][:-1]
            newChoCode=jamoCode('cho',prevJong)
        else :
            outputLine[-1][1]=outputLine[-1][1][:-1] + tuple([jamoCode('jong',doubleJaums[prevJong][0])])
            newChoCode=jamoCode('cho',doubleJaums[prevJong][1])
        stack=[tuple([('s','v',stack[0][0][2])]), tuple([('v',stack[1][0][1],stack[1][0][2]),('cho',tuple([newChoCode]))])]
        outputLine.append(['jung',(newChoCode,jamoCode('jung',args[1]))])
        if len(outputLine)>=2 and not outputLine[-2][-1] is 'completed':
            outputLine[-2].append('completed')
    def cat() :
        global outputLine
        outputLine[-1][1]=outputLine[-1][1] + tuple([jamoCode(args[1],args[2])])
        outputLine[-1][0]=args[1]
    def toDouble() :
        global outputLine
        if args[1] is 'jung' :
            cleanStackExcept(1)
        ind={'jung':1,'jong':2}
        outputLine[-1][1]=outputLine[-1][1][:-1] + tuple([jamoCode(args[1],args[2])])
    def space() :
        global outputLine
        outputLine.append(('space'))
            
    {'new':new,'cat':cat,
    'new with prev jong':newWithPrevJong,
    'to double':toDouble}[args[0]]()

def printEntry(entry) :
    for gulza in entry :
        def mo(target) :
            print(chr(target))
        def cho(target) :
            print(chr(codeToJamo[target[0]]))
        def jung() :
            pass
        codepoint={'mo':lambda:target,
        'cho':lambda:target[0],
        'jung':lambda:target}
inputFile=open(inputFilePath,'r',-1,'utf-8')
for line in inputFile.readlines() :
    if DEBUG : print("========="); sys.stdout.write(line)
    outputLine = []
    currentState=hangulMealy.initState
    stack=[]
    for char in line :
        if char == '\n' :
            break
        if char == '<' :
            if len(outputLine) is 0 :
                continue
            if outputLine[-1][-1] is 'completed' :
                currentState=hangulMealy.initState
                outputLine.pop()
                cleanStackExcept(0)
            elif len(stack) is 1 :
                currentState=stack.pop()[0][1]
                outputLine.pop()
                cleanStackExcept(0)
            else :
                entry = stack.pop()
                currentState=entry[0][0]
                outputLine[-1]=list(entry[1])
                # print("new outputLine" + str(outputLine))
            continue
        if (currentState, char) in hangulMealy.delta :
            #transition exists
            stackEntry=((currentState,hangulMealy.delta[currentState,char],char),None)
            if len(outputLine)>0 :
                stackEntry=(stackEntry[0],tuple(outputLine[-1][:]))
            # print("pushing entry " + str(stackEntry))
            pushStack(stackEntry)
            lambTranslate(hangulMealy.lamb[currentState,char])
            # if (currentState,char) in hangulMealy.lamb :
            #     outputLine = outputLine+hangulMealy.lamb[currentState,char]
            if DEBUG :
                print("%3s to %3s by %s"%(currentState,hangulMealy.delta[currentState,char],char),end=' ')
                print(stack)
            currentState=hangulMealy.delta[currentState,char]
        else :
            # no transition

            outputLine=["No path exists!"]
            break
    if DEBUG : print(outputLine)
    # for ent in outputLine :
    #     print(ent)
    print("(입력) $ ",end='')
    print(line[:-1], end="")
    if not line[-1] is '\n' : print(line[-1],end='')
    print('',end='\n(출력) $ ')
    for c in outputLine :
        if c is ('space') :
            print(' ',end='')
        else :
            print(chr(hangulCodepoints(c)),end='')
    print()
    # print(outputLine)
inputFile.close()