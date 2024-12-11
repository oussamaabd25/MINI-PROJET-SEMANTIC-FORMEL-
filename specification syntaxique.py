import ply.lex as lex
import ply.yacc as yacc

tokens = (
    "STARTUML", "ENDUML", "COLON", "RIGHT_ARROW_1", "RIGHT_ARROW_2", 
    "ACTOR", "ID", "AS", "USECASE", "STRING",
    "PACKAGE", "LBRACE", "RBRACE", "INHERIT", "STEREO", 
    "INCLUDES", "EXTENDS", "ACTOR_TXT", "USE_CASE_TXT", "EOL"
)

reserved = {
    "actor": "ACTOR", 
    "as": "AS", 
    "usecase": "USECASE", 
    "package": "PACKAGE", 
    "includes": "INCLUDES", 
    "extends": "EXTENDS"
}

t_STARTUML = "@startuml"
t_ENDUML = "@enduml"
t_COLON = ":"
t_RIGHT_ARROW_1 = "-+>"
t_RIGHT_ARROW_2 = r"\.+>"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_INHERIT = r"<\|--"
t_EOL = r"\n"

def t_STRING(t): 
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

def t_STEREO(t):
    r"<< [a-zA-Z_][a-zA-Z_0-9] *>>"
    t.value = t.value[3:-3]
    return t

def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    if t.value in reserved.keys():
        t.type = reserved[t.value]
    return t

def t_ACTOR_TXT(t):
    ":[^ :\n][^\n:]*:"
    t.value = t.value[1:-1]
    return t

def t_USE_CASE_TXT(t):
    r"\([^ \(\n][^\n:]*\)"
    t.value = t.value[1:-1]
    return t

t_ignore = " \t"

def t_error(t):
    raise ValueError(f"Unexpected symbol {t}")

lexer = lex.lex()

class UseCaseDiagram:
    def __init__(self):
        self.actors = []
        self.use_cases = []
        self.relations = []
        self.packages = []

def p_diagram(p):
    '''diagram : STARTUML diagram_content ENDUML'''
    p[0] = p[2]

def p_diagram_content(p):
    '''diagram_content : diagram_elements
                       | empty'''
    p[0] = UseCaseDiagram()
    if p[1]:
        p[0] = p[1]

def p_diagram_elements(p):
    '''diagram_elements : diagram_elements diagram_element
                        | diagram_element'''
    if len(p) == 3:
        diagram = p[1]
        element = p[2]
        
        if hasattr(element, 'actor'):
            diagram.actors.append(element.actor)
        elif hasattr(element, 'use_case'):
            diagram.use_cases.append(element.use_case)
        elif hasattr(element, 'relation'):
            diagram.relations.append(element.relation)
        elif hasattr(element, 'package'):
            diagram.packages.append(element.package)
        
        p[0] = diagram
    else:
        p[0] = UseCaseDiagram()
        element = p[1]
        
        if hasattr(element, 'actor'):
            p[0].actors.append(element.actor)
        elif hasattr(element, 'use_case'):
            p[0].use_cases.append(element.use_case)
        elif hasattr(element, 'relation'):
            p[0].relations.append(element.relation)
        elif hasattr(element, 'package'):
            p[0].packages.append(element.package)

def p_diagram_element(p):
    '''diagram_element : actor_definition
                       | use_case_definition
                       | relation
                       | package_definition'''
    p[0] = p[1]

def p_actor_definition(p):
    '''actor_definition : ACTOR ID
                        | ACTOR ID AS ACTOR_TXT'''
    class ActorElement:
        def __init__(self, name, text=None):
            self.actor = {'name': name, 'text': text}
    
    if len(p) == 3:
        p[0] = ActorElement(p[2])
    else:
        p[0] = ActorElement(p[2], p[4])

def p_use_case_definition(p):
    '''use_case_definition : USECASE ID
                            | USECASE ID AS USE_CASE_TXT'''
    class UseCaseElement:
        def __init__(self, name, text=None):
            self.use_case = {'name': name, 'text': text}
    
    if len(p) == 3:
        p[0] = UseCaseElement(p[2])
    else:
        p[0] = UseCaseElement(p[2], p[4])

def p_relation(p):
    '''relation : ID RIGHT_ARROW_1 ID
                | ID RIGHT_ARROW_2 ID
                | ID INCLUDES ID
                | ID EXTENDS ID
                | ID INHERIT ID'''
    class RelationElement:
        def __init__(self, source, target, relation_type):
            self.relation = {'source': source, 'target': target, 'type': relation_type}
    
    if p[2] == '-+>' or p[2] == '.+>':
        p[0] = RelationElement(p[1], p[3], 'communication')
    elif p[2] == 'includes':
        p[0] = RelationElement(p[1], p[3], 'includes')
    elif p[2] == 'extends':
        p[0] = RelationElement(p[1], p[3], 'extends')
    elif p[2] == '<|--':
        p[0] = RelationElement(p[1], p[3], 'inheritance')

def p_package_definition(p):
    '''package_definition : PACKAGE ID LBRACE diagram_content RBRACE'''
    class PackageElement:
        def __init__(self, name, content):
            self.package = {'name': name, 'content': content}
    
    p[0] = PackageElement(p[2], p[4])

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        raise ValueError(f"Syntax error at '{p.value}'")
    else:
        raise ValueError("Syntax error at EOF")

parser = yacc.yacc()

def parse_plantuml(data):
    """
    Parse PlantUML use case diagram specification
    
    Args:
        data (str): PlantUML diagram specification
    
    Returns:
        UseCaseDiagram: Parsed diagram structure
    """
    try:
        return parser.parse(data)
    except Exception as e:
        print(f"Parsing error: {e}")
        return None

if __name__ == '__main__':
   
    with open('usecase.plantuml', 'r') as f:
        spec = f.read()
    
    diagram = parse_plantuml(spec)
    
    if diagram:
        print("Actors:", diagram.actors)
        print("Use Cases:", diagram.use_cases)
        print("Relations:", diagram.relations)
        print("Packages:", diagram.packages)