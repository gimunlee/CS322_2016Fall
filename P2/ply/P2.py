DEBUG = False
tokens = (
    'CHAR',
    'DASH', 'STAR', 'LPAREN', 'RPAREN','UNION',
    )

t_DASH      = r'-'
t_STAR      = r'\*'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_UNION     = r'\+'

nfaStates=set()
nfaSymbols=set()
EPSILON = 'EE' # '-' for epsilon transition
nfaDelta={}
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

def t_CHAR(t): #The only Terminal
    r'[a-zA-Z0-9_,.`~!@#$%^&;:/]'
    nfaSymbols.add(t.value)
    t.value = str(t.value)
    return t
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
def t_error(t):
    print("Illegal character '%s'"%t.value[0])
    t.lexer.skip(1)

import ply.lex as lex
lex.lex()

precedence = (
    ('left', 'LPAREN', 'RPAREN'),
    ('left', 'CHAR'),
    ('left', 'UNION'),
    ('left', 'DASH'),
    ('left', 'STAR'),
    )

def p_expr_concat(p):
    'expr : expr expr'
    # p[0] = p[1] + ',' +  p[2]
    # p[0] = ('concat', p[1], p[2])
    iState, fState = newState(), newState()
    addTransition(iState, EPSILON, p[1][0])
    addTransition(p[1][1],EPSILON,p[2][0])
    addTransition(p[1][1],EPSILON,p[2][0])
    addTransition(p[2][1],EPSILON,fState)
    # nfaDelta[(p[1][1], EPSILON)] = p[2][0]
    # nfaDelta[(p[2][1], EPSILON)] = fState
    p[0] = (iState, fState)
def p_expr_char(p):
    'expr : CHAR'
    # p[0] = (p[1],)
    iState, fState = newState(), newState()
    addTransition(iState,p[1],fState)
    # nfaDelta[(iState,p[1])]=fState
    p[0] = (iState,fState)
def p_expr_dash(p):
    'expr : expr DASH expr'
    # p[0] = p[3]
    p[0] = ('-', p[1],p[3])
def p_expr_star(p):
    'expr : expr STAR'
    # p[0] = '[STAR]( %s )'%p[1]
    # p[0] = ('star',p[1])
    iState, fState = newState(), newState()
    addTransition(iState,EPSILON,p[1][0])
    addTransition(iState,EPSILON,fState)
    addTransition(p[1][1],EPSILON,fState)
    addTransition(p[1][1],EPSILON,p[1][0])
    # nfaDelta[(iState,EPSILON)] = p[1][0]
    # nfaDelta[(iState,EPSILON)] = fState
    # nfaDelta[(p[1][1],EPSILON)] = fState
    # nfaDelta[(p[1][1],EPSILON)] = p[1][0]
    p[0] = (iState, fState)
def p_expr_union(p):
    'expr : expr UNION expr'
    # p[0] = '(%s | %s)'%(p[1],p[3])
    # p[0] = ('union', p[1], p[3]
    iState, fState = newState(), newState()
    addTransition(iState,EPSILON,p[1][0])
    addTransition(iState,EPSILON,p[3][0])
    addTransition(p[1][1],EPSILON,fState)
    addTransition(p[3][1],EPSILON,fState)
    # nfaDelta[(iState,EPSILON)] = p[1][0]
    # nfaDelta[(iState,EPSILON)] = p[3][0]
    # nfaDelta[(p[1][1],EPSILON)] = fState
    # nfaDelta[(p[3][1],EPSILON)] = fState
    p[0] = (iState, fState)
def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]
def p_statement_expr(p):
    'statement : expr'

def p_error(p):
    print("Syntax error at '%s'"%p)

import ply.yacc as yacc
yacc.yacc()

while True:
    try:
        s = input('expression : ')
        if s == '\n' or s == '':
            raise EOFError
    except EOFError:
        print('Bye')
        break
    returnedStates = yacc.parse(s)
    if DEBUG:  print(returnedStates)

    outputFilePath = './outputENfa.txt'

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

    import nfa
    nfa.readString(outputStr)
    nfa.convert()
    outputFile=open(outputFilePath,'w')
    outputFile.write(nfa.toString())
    outputFile.close()
    if DEBUG: print(nfa.toString())

    resetNfa()