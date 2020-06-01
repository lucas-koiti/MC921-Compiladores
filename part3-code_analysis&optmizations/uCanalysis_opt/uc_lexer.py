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

    def t_CHAR_CONST(self, t):
        r'\'.?\''
        t.value = str(t.value)
        return t

    def t_STRING(self, t):
        r'(\".*?\"|\'.*?\')'
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

#import sys

def print_error(msg, x, y):
    print("Lexical error: %s at %d:%d" % (msg, x, y))

#m = UCLexer(print_error)
#m.build()  # Build the lexer
#m.scan(open(sys.argv[1]).read())  # print tokens

