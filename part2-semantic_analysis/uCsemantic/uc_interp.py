# uC Lexical and Syntatic Analysis #

#####################################################################################
#                                                                                   #
#                                  LEXER                                            #
#                                                                                   #
#####################################################################################

import ply.lex as lex

class UCLexer():
    """ A lexer for the uC language. After building it, set the
        input text with input(), and call token() to get new
        tokens.
    """
    def __init__(self, error_func):
        """ Create a new Lexer.
            An error function. Will be called with an error
            message, line and column as arguments, in case of
            an error during lexing.
        """
        self.error_func = error_func
        self.filename = ''

        # Keeps track of the last token returned from self.token()
        self.last_token = None


    def build(self, **kwargs):
        """ Builds the lexer from the specification. Must be
            called after the lexer object is created.

            This method exists separately, because the PLY
            manual warns against calling lex.lex inside __init__
        """
        self.lexer = lex.lex(object=self, **kwargs)


    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1


    def input(self, text: str):
        """ Função que adiciona os códigos de entrada ao lexer
        """
        self.lexer.input(text)


    def token(self)-> lex.LexToken:
        """ Retorna uma instancia de LexToken no seguinte modelo:
        LexToken(tipo, caracter, linha, coluna relativa a linha)
        sendo possível de se acessar de forma independente por:
        LexToken.type, LexToken.value, LexToken.lineno, and LexToken.lexpos
        """
        self.last_token = self.lexer.token()
        return self.last_token


    def find_tok_column(self, token: lex.LexToken)-> int:
        """ Find the column of the token in its line. Essa é a coluna real em
            relação ao arquivo
        """
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.error_func(msg, location[0], location[1])
        self.lexer.skip(1)


    def _make_tok_location(self, token):
        return (token.lineno, self.find_tok_column(token))

    # keywords
    reserved = {
        'void'      :   'VOID',
        'char'      :   'CHAR',
        'int'       :   'INT',
        'float'     :   'FLOAT',
        'if'        :   'IF',
        'else'      :   'ELSE',
        'print'     :   'PRINT',
        'while'     :   'WHILE',
        'for'       :   'FOR',
        'break'     :   'BREAK',
        'assert'    :   'ASSERT',
        'read'      :   'READ',
        'return'    :   'RETURN'
    }

    tokens = [
        # literals
        'ID', 'STRING', 
        # constant
        'INT_CONST','FLOAT_CONST', 'CHAR_CONST',
        # binary exp operators * / % + - < <= > >= == != && ||
        'TIMES', 'DIV', 'MOD', 'PLUS', 'MINUS', 'LT', 'LTE', 
        'GT', 'GTE', 'EQ', 'NEQ', 'AND', 'OR', 'NOT', 'EQUALS',
        # unary exp operators ++ --
        'PLUSPLUS', 'MINUSMINUS',
        # delimiters ( ) { } [ ] ; ,
        'RPAREN', 'LPAREN', 'RBRACE', 'LBRACE', 'RBRACKET', 'LBRACKET', 'SEMI', 'COMMA',
        # assignment operators *= /= %= += -=
        'TIMESEQ', 'DIVEQ', 'MODEQ', 'PLUSEQ', 'MINUSEQ',
        # pointer and address '*' and '&'
        'ADDR' 
    ] + list(reserved.values())

    # binary exp operators
    t_EQUALS         = r'='
    t_TIMES         = r'\*'
    t_DIV           = r'/'
    t_MOD           = r'%'
    t_PLUS          = r'\+'
    t_MINUS         = r'-'
    t_LT            = r'<'
    t_LTE           = r'<='
    t_GT            = r'>'
    t_GTE           = r'>='
    t_EQ            = r'=='
    t_NEQ           = r'!='
    t_AND           = r'&&'
    t_OR            = r'\|\|'
    t_NOT           = r'!'

    # unary exp operators
    t_PLUSPLUS      = r'\+\+'
    t_MINUSMINUS    = r'--'

    # delimiters
    t_RPAREN        = r'\)'
    t_LPAREN        = r'\('
    t_RBRACE        = r'\}'
    t_LBRACE        = r'\{'
    t_RBRACKET      = r'\]'
    t_LBRACKET      = r'\['
    t_SEMI          = r';'
    t_COMMA         = r','

    # assignment operators
    t_TIMESEQ       = r'\*='
    t_DIVEQ         = r'/='
    t_MODEQ         = r'%='
    t_PLUSEQ        = r'\+='
    t_MINUSEQ       = r'-='

    # address
    t_ADDR          = r'&' 

    # literals
    def t_ID(self, t):
        r'[a-zA-Z_][0-9a-zA-Z_]*'
        t.type = self.reserved.get(t.value,'ID')  
        return t

    def t_STRING(self, t):
        r'(\".*?\"|\'.*?\')'
        t.value = str(t.value)
        return t
    
    def t_CHAR_CONST(self, t):
        r'\'.?\''
        t.value = str(t.value)
        return t

    def t_FLOAT_CONST(self, t):
        r'([0-9]*?\.[0-9]+)|([0-9]+\.)'
        t.value = float(t.value)
        return t

    def t_INT_CONST(self, t):
        r'0|[1-9][0-9]*'
        t.value = int(t.value)
        return t

    # ignore 
    t_ignore        = ' \t' # ignora 

    # Newlines
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_comment(self, t):
        # r'/\*(.|\n)*?\*/'
        # r'\/[\/]+.*'
        r'(\/\*(\*(?!\/)|[^*])*\*\/)|(\/[\/]+.*)'
        t.lexer.lineno += t.value.count('\n')

    def t_error(self, t):
        msg = "Illegal character %s" % repr(t.value[0])
        self._error(msg, t)

    # Scanner (used only for test)
    def scan(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

#if __name__ == '__main__':

#    import sys

def print_error(msg, x, y):
    print("Lexical error: %s at %d:%d" % (msg, x, y))

#m = UCLexer(print_error)
#m.build()  # Build the lexer
#m.scan(open(sys.argv[1]).read())  # print tokens

#####################################################################################
#                                                                                   #
#                                  PARSER                                           #
#                                                                                   #
#####################################################################################

import ply.yacc as yacc

import uc_ast


class ParseError(Exception): pass

class UCParser():
    tokens = UCLexer.tokens
    parser = None
    

    def __init__(self):
        self.lexer = UCLexer(print_error)
        self.lexer.build()
        self.parser = yacc.yacc(module=self)


    def _token_coord(self, p, token_idx, set_col=False):
        last_cr = p.lexer.lexer.lexdata.rfind('\n', 0, p.lexpos(token_idx))
        if last_cr < 0:
            last_cr = -1
        column = (p.lexpos(token_idx) - (last_cr))
        return uc_ast.Coord(p.lineno(token_idx), 1 if set_col else column)


    def _build_declarations(self, spec, decls):
        """ Builds a list of declarations all sharing the given specifiers.
        """
        declarations = []

        for decl in decls:
            assert decl['decl'] is not None
            declaration = uc_ast.Decl(
                    name=None,
                    type=decl['decl'],
                    init=decl.get('init'),
                    coord=decl['decl'].coord)

            fixed_decl = self._fix_decl_name_type(declaration, spec)
            declarations.append(fixed_decl)

        return declarations
    

    def _fix_decl_name_type(self, decl, typename):
        """ Fixes a declaration. Modifies decl.
        """
        # Reach the underlying basic type
        type = decl
        while not isinstance(type, uc_ast.VarDecl):
            type = type.type

        decl.name = type.declname

        # The typename is a list of types. If any type in this
        # list isn't an Type, it must be the only
        # type in the list.
        # If all the types are basic, they're collected in the
        # Type holder.
        for tn in typename:
            if not isinstance(tn, uc_ast.Type):
                if len(typename) > 1:
                    self._parse_error(
                        "Invalid multiple types specified", tn.coord)
                else:
                    type.type = tn
                    return decl

        if not typename:
            # Functions default to returning int
            if not isinstance(decl.type, uc_ast.FuncDecl):
                self._parse_error("Missing type in declaration", decl.coord)
            type.type = uc_ast.Type(['int'], coord=decl.coord)
        else:
            # At this point, we know that typename is a list of Type
            # nodes. Concatenate all the names into a single list.
            type.type = uc_ast.Type(
                [typename.names[0]],
                coord=typename.coord)
        return decl
    

    def _type_modify_decl(self, decl, modifier):
        """ Tacks a type modifier on a declarator, and returns
            the modified declarator.
            Note: the declarator and modifier may be modified
        """
        modifier_head = modifier
        modifier_tail = modifier

        # The modifier may be a nested list. Reach its tail.
        while modifier_tail.type:
            modifier_tail = modifier_tail.type

        # If the decl is a basic type, just tack the modifier onto it
        if isinstance(decl, uc_ast.VarDecl):
            modifier_tail.type = decl
            return modifier
        else:
            # Otherwise, the decl is a list of modifiers. Reach
            # its tail and splice the modifier onto the tail,
            # pointing to the underlying basic type.
            decl_tail = decl

            while not isinstance(decl_tail.type, uc_ast.VarDecl):
                decl_tail = decl_tail.type

            modifier_tail.type = decl_tail.type
            decl_tail.type = modifier_head
            return decl


    def _build_function_definition(self, spec, decl, param_decls, body):
        """ assistence to make a function definition"""

        declaration = self._build_declarations(
            spec=spec,
            decls=[dict(decl=decl, init=None)],
        )[0]

        return uc_ast.FuncDef(
            spec,
            declaration,
            param_decls,
            body,
            decl.coord)


    def parse(self, text, filename='', debug=False):
        """ Parses uC code and returns an AST.
            text:
                A string containing the uC source code
            filename:
                Name of the file being parsed (for meaningful
                error messages)
        """
        return self.parser.parse(input=text, lexer=self.lexer, debug=debug)


    def _parse_error(self, msg, coord):
        raise ParseError("%s: %s" % (coord, msg))
    
    # ----------------------- GRAMMAR RULES - THE CORE PROGRAM PART --------------------------
    
    def p_program(self, p): 
        """ program  : global_declaration_list
        """
        p[0] = uc_ast.Program(p[1], self._token_coord(p,1))


    def p_global_declaration_list(self, p):
        """ global_declaration_list : global_declaration
                                    | global_declaration_list global_declaration
        """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]


    def p_global_declaration(self, p):
        """ global_declaration : function_definition """
        p[0] = p[1]


    def p_global_declaration_1(self,p):
        """ global_declaration : declaration """
        p[0] = uc_ast.GlobalDecl(p[1]) 


    def p_function_definition_1(self, p):
        """ function_definition : declarator declaration_list_emp compound_statement
        """
        spec = dict(type=[uc_ast.Type(['void'],
                    coord= self._token_coord(p,1))],
                    function=[])
        
        p[0] = self._build_function_definition(spec= spec,
                                               decl= p[1],
                                               param_decls= p[2],
                                               body = p[3])
       

    def p_function_definition_2(self, p): 
        """ function_definition : type_specifier declarator declaration_list_emp compound_statement
        """
        p[0] = self._build_function_definition(spec= p[1],
                                               decl= p[2],
                                               param_decls= p[3],
                                               body= p[4])


    def p_type_specifier(self, p):
        """ type_specifier : VOID
                           | CHAR
                           | INT
                           | FLOAT
        """
        p[0] = uc_ast.Type([p[1]], self._token_coord(p,1))


    def p_declaration_list(self, p): 
        """ declaration_list : declaration
                             | declaration_list declaration
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2]


    def p_declaration_list_emp(self, p):
        """ declaration_list_emp : declaration_list
                                 | empty
        """
        p[0] = p[1]
    

    def p_decl_body(self, p):
        """ decl_body : type_specifier init_declarator_list_emp """
        spec = p[1]
        decls = None
        if p[2] is not None:
            decls = self._build_declarations(spec= spec,
                                             decls= p[2])
        p[0] = decls


    def p_declaration(self, p):
        """ declaration : decl_body SEMI
        """
        p[0] = p[1]
   

    def p_init_declarator_list(self, p):
        """ init_declarator_list : init_declarator
                                 | init_declarator_list COMMA init_declarator
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    

    def p_init_declarator_list_emp(self, p):
        """ init_declarator_list_emp : init_declarator_list
                                     | empty
        """
        p[0] = p[1]
    

    def p_init_declarator(self, p):
        """ init_declarator : declarator
                            | declarator EQUALS initializer
        """
        if len(p) == 2:
            p[0] = dict(decl= p[1], init= None)
        else:
            p[0] = dict(decl= p[1], init= p[3])
    

    def p_declarator(self, p):
        """ declarator : direct_declarator """
        p[0] = p[1]

    def p_declarator1(self, p):
        """ declarator : pointer direct_declarator """
        p[0] = self._type_modify_decl(p[2], p[1])

    #adding pointer to try pass 7th test
    def p_pointer(self, p):
        """ pointer : TIMES
                    | TIMES pointer
        """
        coord = self._token_coord(p, 1)
        n_type = uc_ast.PtrDecl(type= None,
                                coord= coord)
        if len(p) == 2:
            p[0] = n_type
        else:
            t_type = p[2]
            while t_type.type is not None:
                t_type = t_type.type
            t_type.type = n_type
            
            p[0] = p[2]

    def p_direct_declarator_1(self, p): 
        """ direct_declarator : identifier """
        p[0] = uc_ast.VarDecl(declname= p[1],
                              type= None,
                              coord= self._token_coord(p,1))


    def p_direct_declarator_2(self, p): 
        """ direct_declarator : LPAREN declarator RPAREN """
        p[0] = p[2]


    def p_direct_declarator_3(self, p):
        """ direct_declarator : direct_declarator LBRACKET constant_expression_emp RBRACKET """
        array = uc_ast.ArrayDecl(type= None,
                                 dim= p[3] if len(p) > 4 else None,
                                 coord= p[1].coord)
        p[0] = self._type_modify_decl(p[1], array)


    def p_direct_declarator_4(self, p):
        """ direct_declarator : direct_declarator LPAREN parameter_list RPAREN
                              | direct_declarator LPAREN identifier_list_emp RPAREN
        """
        fun = uc_ast.FuncDecl(args= p[3],
                              type= None,
                              coord= p[1].coord)
        p[0] = self._type_modify_decl(p[1], fun)


    def p_parameter_list(self, p):
        """ parameter_list : parameter_declaration
                           | parameter_list COMMA parameter_declaration
        """
        if len(p) == 2:
            p[0] = uc_ast.ParamList([p[1]], p[1].coord)
        else:
            p[1].params.append(p[3])
            p[0] = p[1]
    

    def p_parameter_declaration(self, p):
        """ parameter_declaration : type_specifier declarator
        """
        p[0] = self._build_declarations(spec= p[1],
                                        decls= [dict(decl= p[2])])[0]


    def p_identifier_list(self, p):  
        """ identifier_list : identifier
                            | identifier_list COMMA identifier
        """
        if len(p) == 4:
            p[1].params.append(p[3])
            p[0] = p[1]
        else:
            p[0] = uc_ast.ParamList([p[1]], p[1].coord)
    

    def p_identifier_list_emp(self, p):
        """ identifier_list_emp : identifier_list
                                | empty
        """
        p[0] = p[1]


    def p_constant_expression(self, p): 
        """ constant_expression : binary_expression
        """
        p[0] = p[1]
    

    def p_constant_expression_emp(self, p):
        """ constant_expression_emp : empty
                                    | constant_expression
        """
        p[0] = p[1]
 

    def p_binary_expression(self, p): 
        """ binary_expression : cast_expression
                              | binary_expression TIMES binary_expression
                              | binary_expression DIV binary_expression
                              | binary_expression MOD binary_expression
                              | binary_expression PLUS binary_expression
                              | binary_expression MINUS binary_expression
                              | binary_expression LT binary_expression
                              | binary_expression LTE binary_expression
                              | binary_expression GT binary_expression
                              | binary_expression GTE binary_expression
                              | binary_expression EQ binary_expression
                              | binary_expression NEQ binary_expression
                              | binary_expression AND binary_expression
                              | binary_expression OR binary_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else: 
            p[0] = uc_ast.BinaryOp(p[2], p[1], p[3], p[1].coord)


    def p_cast_expression_1(self, p): 
        """ cast_expression : unary_expression """
        p[0] = p[1]


    def p_cast_expression_2(self, p): 
        """ cast_expression : LPAREN type_specifier RPAREN cast_expression """
        p[0] = uc_ast.Cast(p[2], p[4], self._token_coord(p, 1)) 
    

    def p_unary_expression_1(self, p):
        """ unary_expression : postfix_expression """
        p[0] = p[1]


    def p_unary_expression_2(self, p): 
        """ unary_expression : PLUSPLUS unary_expression
                             | MINUSMINUS unary_expression
                             | unary_operator cast_expression
        """
        p[0] = uc_ast.UnaryOp(p[1], p[2], p[2].coord)
    
    
    def p_postfix_expression_1(self,p):
        """ postfix_expression : primary_expression """
        p[0] = p[1]


    def p_postfix_expression_2(self,p): 
        """ postfix_expression : postfix_expression LBRACKET expression RBRACKET """
        p[0] = uc_ast.ArrayRef(p[1], p[3], p[1].coord)


    def p_postfix_expression_3(self,p):
        """ postfix_expression : postfix_expression LPAREN argument_expression RPAREN
                               | postfix_expression LPAREN RPAREN 
        """
        p[0] = uc_ast.FuncCall(p[1], p[3] if len(p) == 5 else None, p[1].coord)
    

    def p_postfix_expression_4(self,p):
        """ postfix_expression : postfix_expression PLUSPLUS
                               | postfix_expression MINUSMINUS
        """
        p[0] = uc_ast.UnaryOp('p' + p[2], p[1], p[1].coord)


    def p_primary_expression(self, p):
        """ primary_expression : identifier
                               | constant
                               | string
                               | LPAREN expression RPAREN
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]


    def p_identifier(self, p): 
        """ identifier : ID """
        p[0] = uc_ast.ID(p[1], self._token_coord(p,1))


    def p_constant_1(self, p):
        """ constant : INT_CONST """
        p[0] = uc_ast.Constant('int', p[1], self._token_coord(p, 1))


    def p_constant_2(self, p): 
        """ constant : CHAR_CONST """
        p[0] = uc_ast.Constant('char', p[1], self._token_coord(p, 1))


    def p_constant_3(self, p):
        """ constant : FLOAT_CONST """
        p[0] = uc_ast.Constant('float', p[1], self._token_coord(p, 1))
    

    def p_string(self, p):
        """ string : STRING """
        p[0] = uc_ast.Constant('string', p[1], self._token_coord(p, 1))


    def p_expression(self, p): 
        """ expression : assignment_expression
                       | expression COMMA assignment_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1], uc_ast.ExprList):
                p[1] = uc_ast.ExprList([p[1]], p[1].coord)
            p[1].exprs.append(p[3])
            p[0] = p[1]

    def p_argument_expression(self, p):
        """ argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1], uc_ast.ExprList):
                p[1] = uc_ast.ExprList([p[1]], p[1].coord)
            
            p[1].exprs.append(p[3])
            p[0] = p[1]
    

    def p_assignment_expression(self, p):
        """ assignment_expression : binary_expression
                                  | unary_expression assignment_operator assignment_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = uc_ast.Assignment(p[2], p[1], p[3], p[1].coord)
    

    def p_assignment_operator(self, p):
        """ assignment_operator : EQUALS
                                | TIMESEQ
                                | DIVEQ
                                | MODEQ
                                | PLUSEQ
                                | MINUSEQ
        """
        p[0] = p[1]


    def p_unary_operator(self, p):
        """ unary_operator : ADDR
                           | TIMES
                           | PLUS
                           | MINUS
                           | NOT
        """
        p[0] = p[1]
    

    def p_initializer_1(self, p):
        """ initializer : assignment_expression """
        p[0] = p[1]
     

    def p_initializer_2(self, p):
        """ initializer : LBRACE initializer_list RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        """
        if p[2] is None:
            p[0] = uc_ast.InitList([], self._token_coord(p, 1))
        else:
            p[0] = p[2]


    def p_initializer_list(self, p):
        """ initializer_list : initializer
                             | initializer_list COMMA initializer
        """
        if len(p) == 2:
            p[0] = uc_ast.InitList([p[1]], p[1].coord)
        else:
            p[1].exprs.append(p[3])
            p[0] = p[1]


    def p_block_item(self, p):
        """ block_item : declaration
                       | statement
        """
        p[0] = p[1] if isinstance(p[1], list) else [p[1]]
    

    def p_block_item_list(self, p):
        """ block_item_list : block_item
                            | block_item_list block_item
        """
        if len(p) == 2 or p[2] is None:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2]


    def p_block_item_list_emp(self, p):
        """ block_item_list_emp : empty
                                | block_item_list
        """
        p[0] = p[1]


    def p_compound_statement(self, p):
        """ compound_statement : LBRACE block_item_list_emp RBRACE
        """
        p[0] = uc_ast.Compound(block_items= p[2],
                               coord= self._token_coord(p, 1, set_col= True))


    def p_statement(self, p):
        """ statement : expression_statement
                      | compound_statement
                      | selection_statement
                      | iteration_statement
                      | jump_statement
                      | assert_statement
                      | print_statement
                      | read_statement
        """
        p[0] = p[1]


    def p_expression_statement(self, p):
        """ expression_statement : expression SEMI """
        if p[1] is None:
            p[0] = uc_ast.EmptyStatement(self._token_coord(p, 2))
        else:
            p[0] = p[1]


    def p_selection_statement(self, p): #TODO
        """ selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        """
        if len(p) == 6:
            p[0] = uc_ast.If(p[3], p[5], None, self._token_coord(p, 1))
        else:
            p[0] = uc_ast.If(p[3], p[5], p[7], self._token_coord(p, 1))


    def p_iteration_statement_1(self, p): 
        """ iteration_statement : WHILE LPAREN expression RPAREN statement """
        p[0] = uc_ast.While(p[3], p[5], self._token_coord(p, 1))


    def p_iteration_statement_2(self, p): 
        """ iteration_statement : FOR LPAREN expression_emp SEMI expression_emp SEMI expression_emp RPAREN statement """
        p[0] = uc_ast.For(p[3], p[5], p[7], p[9], self._token_coord(p, 1))


    def p_iteration_statement_3(self, p): 
        """ iteration_statement : FOR LPAREN declaration expression_emp SEMI expression_emp RPAREN statement """
        p[0] = uc_ast.For(uc_ast.DeclList(p[3], self._token_coord(p, 1)), p[4], p[6], p[8], self._token_coord(p, 1))


    def p_expression_emp(self, p):
        """ expression_emp : empty
                           | expression
        """
        p[0] = p[1]


    def p_jump_statement_1(self, p): 
        """ jump_statement : BREAK SEMI """
        p[0] = uc_ast.Break(self._token_coord(p, 1))
    

    def p_jump_statement_2(self, p): 
        """ jump_statement : RETURN expression_emp SEMI """ 
        if len(p) == 4:
            p[0] = uc_ast.Return(p[2], self._token_coord(p, 1))
        else:
            p[0] = uc_ast.Return(None, self._token_coord(p, 1))


    def p_assert_statement(self, p):
        """ assert_statement : ASSERT expression SEMI """
        p[0] = uc_ast.Assert(p[2], self._token_coord(p, 1))
 

    def p_print_statement(self, p): 
        """ print_statement : PRINT LPAREN  expression_emp RPAREN SEMI """
        p[0] = uc_ast.Print(p[3], self._token_coord(p, 1))


    def p_read_statement(self, p):
        """ read_statement : READ LPAREN argument_expression RPAREN SEMI """
        p[0] = uc_ast.Read(p[3], self._token_coord(p, 1))


    def p_empty(self, p):
        'empty :'
        p[0] = None


    def p_error(self, p):
        print(f"Syntax error at {p.value!r}")

    # to avoid ambiguit
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NEQ'),
        ('left', 'GT', 'GTE', 'LT', 'LTE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIV', 'MOD')
    )

# if __name__ == "__main__":

#     parser = UCParser()
#     print(parser.parse('int a = 0;', "parser"))d