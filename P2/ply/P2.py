#-*- coding: utf-8 -*-
DEBUG = False

######################
# Table of Contents
# 1. Lexer Code
# 2. Yacc Code
# 3. Program using Scanner and Parser
# 3.0. Command line arguments supporting
# 3.1. Parsing/Generating AST
# 3.2. Constructing e-NFA from AST
# 3.3. Generating e-NFA description string
# 3.4. e-NFA to m-DFA
#####################

###############################################
# Lexer code
###############################################
tokens = (
    'CHAR',
    'STAR', 'LPAREN', 'RPAREN','UNION',
    )

t_STAR      = r'\*'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_UNION     = r'\+'

def t_CHAR(t): #The only Terminal
    r'[a-zA-Z0-9_,.`~!@#$%^&;:/]'
    # nfaSymbols.add(t.value)
    t.value = str(t.value)
    return t
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
def t_error(t):
    print("Illegal character '%s'"%t.value[0])
    t.lexer.skip(1)

import ply.lex as lex
lex.lex() # Scanner generated

########################################################
# Yacc code
############
# Constructs AST. Each node of the tree is a tuple, of which the first element is its own value and the second/third element is children.
######################################################## 
# precedence = (
#     # ('left', 'concat'),
#     ('left', 'LPAREN', 'RPAREN'),
#     ('left', 'CHAR'),
#     ('left', 'UNION'),
#     ('right', 'STAR'),
#     )

start = 'expr'
#expr for union
def p_expr_chunk(p):
    'expr : chunk'
    p[0] = p[1]
def p_expr_union(p):
    'expr : expr UNION chunk'
    p[0] = ('union', p[1], p[3])
#chunk for concatenation
def p_chunk_term(p):
    'chunk : term'
    p[0] = p[1]
def p_chunk_concat(p):
    'chunk : chunk term'
    p[0] = ('concat', p[1], p[2])
#term for single character, star, or group
def p_term_char(p):
    'term : CHAR'
    p[0] = (p[1],)
def p_term_star(p):
    'term : term STAR'
    p[0]=('star', p[1])
def p_term_group(p):
    'term : LPAREN expr RPAREN'
    p[0] = p[2]
#epsilon for empty string
def p_term_epsilon(p):
    'term : LPAREN RPAREN'
    p[0] = ('EE',)
# def p_epsilon_parens(p):
#     'epsilon : LPAREN RPAREN'
#     p[0]='Empty String'
# def p_expr_epsilon(p):
#     'expr : epsilon'
#     p[0] = p[1]
# def p_expr_union_right_epsilon(p):
#     'expr : expr UNION epsilon'
#     p[0] = p[1]

def p_error(p):
    print("Syntax error at '%s'"%p)

import ply.yacc as yacc
yacc.yacc() # Parser generated

###############################################
# Program using the Scanner and Parser
######
# Support command line arguments

import sys
sys.path.append("./")

def quitWithHelp(causeStr="") :
  print(causeStr)
  print("="*10)
  print("Running Policy of P2 : python P2.py --re [RE file path] --mdfa [m-dfa output file path]")
  print("    Given output file path is for e-nfa")
  print("    Generated m-dfa will output to \"mdfa[outputFilePath]\" ")
  quit(-1)

reFilePath=""
mDfaFilePath=""
# flag for path of re and mdfa file
if '--re' in sys.argv : reFilePath=sys.argv[sys.argv.index('--re')+1]
else : quitWithHelp("The path of regular expression file not found") 
if '--mdfa' in sys.argv : mDfaFilePath=sys.argv[sys.argv.index('--mdfa')+1]
else : quitWithHelp('The path for output m-DFA description file not found')

# flag for debug printing option. 0 for off, 1 for on
if '--debug' in sys.argv :
  if sys.argv[sys.argv.index('--debug')+1] == '1' : DEBUG=True
  else : DEBUG=False

##########################################
## Initiate Parsing
try:
    reFile = open(reFilePath,'r')
    s = reFile.readline()
    reFile.close()
    # s = input('expression : ')
    if s == '\n' or s == '':
        raise EOFError
except EOFError:
    print('Bye')
    exit(-1)
ast = yacc.parse(s)

##########################################
## Construct E-NFA 
nfaStates=set()
nfaSymbols=set()
EPSILON = 'EE' # 'EE' for epsilon transition
nfaDelta={}

def constructENfa(ast):
    def concat(node) :
        child = (constructENfa(node[1]), constructENfa(node[2]))
        iState, fState = newState(), newState()
        addTransition(iState, EPSILON, child[0][0])
        addTransition(child[0][1],EPSILON,child[1][0])
        addTransition(child[0][1],EPSILON,child[1][0])
        addTransition(child[1][1],EPSILON,fState)
        return (iState, fState)
    def star(node) :
        child = constructENfa(node[1])
        iState, fState = newState(), newState()
        addTransition(iState,EPSILON,child[0])
        addTransition(iState,EPSILON,fState)
        addTransition(child[1],EPSILON,fState)
        addTransition(child[1],EPSILON,child[0])
        return (iState, fState)
    def union(node) :
        child = (constructENfa(node[1]), constructENfa(node[2]))
        iState, fState = newState(), newState()
        addTransition(iState,EPSILON,child[0][0])
        addTransition(iState,EPSILON,child[1][0])
        addTransition(child[0][1],EPSILON,fState)
        addTransition(child[1][1],EPSILON,fState)
        return  (iState, fState)
    def char(node) :
        global nfaSymbols
        if node[0] is EPSILON :
            iState=newState()
            fState=iState
        else :
            nfaSymbols.add(node[0])
            iState, fState = newState(), newState()
            addTransition(iState,node[0],fState)
        return (iState,fState)
    handler={'concat':concat,
            'star':star,
            'union':union}
    if ast[0] in handler :
        return handler[ast[0]](ast)
    else :
        return char(ast)

# Helpers for construction E-NFA
def newState():
    newOne = 'Q%d'%len(nfaStates)
    nfaStates.add(newOne)
    return newOne
def resetNfa():
    global nfaStates, nfaSymbols, nfaDelta
    nfaStates=set()
    nfaSymbols=set()
    nfaDelta={}
    nfa.reset()
    if DEBUG : print('NFA RESET')
def addTransition(fromState, iSymbol, toState):
    if (fromState, iSymbol) in nfaDelta.keys() :
        nfaDelta[(fromState,iSymbol)]=nfaDelta[(fromState,iSymbol)].union(frozenset([toState]))
    else :
        nfaDelta[(fromState,iSymbol)]=frozenset([toState])

if DEBUG: print('AST %s'%str(ast))
returnedStates = constructENfa(ast)
if DEBUG:  print(returnedStates)

##########################################
# Generating strings for E-NFA description
def generateENFAString() :
    # outputFilePath = './outputENfa.txt'
    outputStr=''

    outputStr+='State\n'
    statesTuple = tuple(nfaStates)
    for i in range(len(statesTuple)) :
        outputStr+= '%s,'%statesTuple[i]
    outputStr= outputStr[:-1] + '\n'

    outputStr+='Input symbol\n'
    symbolsTuple = tuple(nfaSymbols)
    for i in range(len(symbolsTuple)) :
        outputStr+='%s,'%symbolsTuple[i]
    outputStr= outputStr[:-1] + '\n'

    outputStr+= 'State transition function\n'
    for key in nfaDelta.keys() :
        for q2 in nfaDelta[key] :
            outputStr+='%s,%s,%s\n'%(key[0],key[1],q2)

    outputStr+='Initial state\n'
    outputStr+=returnedStates[0] + '\n'
    if DEBUG: print(returnedStates[0])

    outputStr+='Final state\n'
    outputStr+=returnedStates[1] + '\n'

    if DEBUG:
        print('Chars : %s'%nfaSymbols)
        print('Delta : %s'%nfaDelta)

    return outputStr

##########
# Call P2-1
import nfa
nfa.readString(generateENFAString())
nfa.convert()
mDfaFile=open(mDfaFilePath,'w')
mDfaFile.write(nfa.toString())
mDfaFile.close()
if DEBUG: print(nfa.toString())