import ply.lex as lex


reserved = {
    'actor': 'ACTOR',
    'as': 'AS',
    'usecase': 'USECASE',
    'package': 'PACKAGE',
    'includes': 'INCLUDES',
    'extends': 'EXTENDS',
    '@startuml': 'STARTUML',
    '@enduml': 'ENDUML'
}


tokens = [
    'COLON',
    'RIGHT_ARROW_A',
    'RIGHT_ARROW_B',
    'LBRACE',
    'RBRACE',
    'INHERIT',
    'EOL',
    'STRING',
    'STEREO',
    'ACTOR_TEXT',
    'USE_CASE_TEXT',
    'ID'
] + list(reserved.values())


t_COLON = r':'
t_RIGHT_ARROW_A = r'--?>'
t_RIGHT_ARROW_B = r'\.>?'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_INHERIT = r'<\|--'

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value.strip('"')  
    return t

def t_STEREO(t):
    r'<<[^>]+>>'
    t.value = t.value.strip('<<>>')  
    return t

def t_ACTOR_TEXT(t):
    r':[a-zA-Z_][a-zA-Z0-9_]*:'
    t.value = t.value.strip(':')  
    return t

def t_USE_CASE_TEXT(t):
    r'\([a-zA-Z_][a-zA-Z0-9_]*\)'
    t.value = t.value.strip('()')  
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID') 
    return t


def t_EOL(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t


t_ignore = ' \t'


def t_error(t):
    print(f"Caractère illégal '{t.value[0]}' à la ligne {t.lineno}")
    t.lexer.skip(1)


lexer = lex.lex()