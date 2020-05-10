# uc Semantic Analysis #

from uc_ast import *
from uc_parser import UCParser

###################################
#           AST visitor           #
###################################

class NodeVisitor(object):

    _method_cache = None

    def visit(self, node):
        """ Visit a node.
        """

        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c in node:
            self.visit(c)

####################################################
#                     SYMBOLS                      #
####################################################

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class uCType(object):

    '''
    Class that represents a type in the uC language.  Types 
    are declared as singleton instances of this type.
    '''
    def __init__(self, typename,
                 binary_ops=None, unary_ops=None,
                 rel_ops=None, assign_ops=None):
        
        #super().__init__(typename)   # TODO look if it works, uCtype its like a BuiltIn, so its also a symbol.
       
        self.typename = typename
        self.unary_ops = unary_ops or set()
        self.binary_ops = binary_ops or set()
        self.rel_ops = rel_ops or set()
        self.assign_ops = assign_ops or set()

IntType = uCType("int",
                 unary_ops   = {"-", "+", "--", "++", "p--", "p++", "*", "&"},
                 binary_ops  = {"+", "-", "*", "/", "%"},
                 rel_ops     = {"==", "!=", "<", ">", "<=", ">="},
                 assign_ops  = {"=", "+=", "-=", "*=", "/=", "%="}
                 )

FloatType = uCType("float",
                 unary_ops   = {"-", "+", "*", "&"},
                 binary_ops  = {"+", "-", "*", "/", "%"},
                 rel_ops     = {"==", "!=", "<", ">", "<=", ">="},
                 assign_ops  = {"=", "+=", "-=", "*=", "/=", "%="}
                 )

CharType = uCType("char",
                 unary_ops   = {"*", "&"},
                 rel_ops     = {"==", "!=", "&&", "||"}
                 )

ArrayType = uCType("array",
                 unary_ops   = {"*", "&"},
                 rel_ops     = {"==", "!="}
                 )

BoolType = uCType("bool",
                 unary_ops   = {"*", "&", "!"},
                 rel_ops     = {"==", "!=", "&&", "||"}
                 )
            
StringType = uCType("string",
                 rel_ops     = {"==", "!="}
                 )

PtrType = uCType("ptr",
                 unary_ops   = {"*", "&"},
                 rel_ops     = {"==", "!="}
                 )

VoidType = uCType("void",
                 unary_ops   = {"*", "&"},
                 rel_ops     = {"==", "!="}
                 )

class BuiltInType(Symbol):
    def __init__(self, name, type):
            super().__init__(name, type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

class VarSymbol(Symbol):
    def __init__(self, name, type):
            super().__init__(name, type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__

class ArraySymbol(Symbol):
    def __init__(self, name, type):
            super().__init__(name, type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__

class PtrSymbol(Symbol):
    def __init__(self, name, type):
            super().__init__(name, type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__

class FuncSymbol(Symbol):
    def __init__(self, name, params=None):
        super().__init__(name)
        # a list of formal parameters
        self.params = params if params is not None else []

    def __str__(self):
        return '<{class_name}(name={name}, parameters={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.params,
        )

    __repr__ = __str__

####################################################
#               SCOPED SYMBOL TABLE                #
####################################################

class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def _init_builtins(self):
        self.insert(BuiltInType("int", IntType))
        self.insert(BuiltInType("float", FloatType))
        self.insert(BuiltInType("char", CharType))
        self.insert(BuiltInType("array", ArrayType))
        self.insert(BuiltInType("bool", BoolType))
        self.insert(BuiltInType("string", StringType))
        self.insert(BuiltInType("ptr", PtrType))
        self.insert(BuiltInType("void", VoidType))

    def __str__(self):
            h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
            lines = ['\n', h1, '=' * len(h1)]
            for header_name, header_value in (
                ('Scope name', self.scope_name),
                ('Scope level', self.scope_level),
            ):
                lines.append('%-15s: %s' % (header_name, header_value))
            h2 = 'Scope (Scoped symbol table) contents'
            lines.extend([h2, '-' * len(h2)])
            lines.extend(
                ('%7s: %r' % (key, value))
                for key, value in self._symbols.items()
            )
            lines.append('\n')
            s = '\n'.join(lines)
            return s

    __repr__ = __str__

    def insert(self, symbol):
        print('Insert: %s' % symbol.name)
        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False):
        print('Lookup: %s. (Scope name: %s)' % (name, self.scope_name))
        # 'symbol' is either an instance of the Symbol class or None
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        # recursively go up the chain and lookup the name
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

####################################################
#                SEMANTIC ANALYSIS                #
####################################################

class SemanticAnalyzer(NodeVisitor):
    '''
    Program visitor class. This class uses the visitor pattern. You need to define methods
    of the form visit_NodeName() for each kind of AST node that you want to process.
    '''
    def __init__(self):
        self.current_scope = None

    def visit_Program(self,node): #TODO test if this works
        print('ENTER scope: global')
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope, # None
        )
        global_scope._init_builtins()
        self.current_scope = global_scope

        # 1. Visit all of the global declarations
        # 2. Record the associated symbol table
        for _decl in node.gdecls:
            self.visit(_decl)

        print(global_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: global')

    def visit_BinaryOp(self, node): #TODO test if this works
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        self.visit(node.left)
        left_type = node.left.names[-1]
        self.visit(node.right)
        right_type = node.right.names[-1]
        
        _line = f"{node.coord.line}:{node.coord.column} - "
        assert left_type == right_type, _line + f"Binary operator {node.op} does not match types"
        if node.op in (left_type.binary_ops or left_type.rel_ops):
            node.type = node.left.type

    def visit_Assignment(self, node): #TODO check if this works
        _line = f"{node.coord.line}:{node.coord.column} - "

        self.visit(node.rvalue)
        right_type = node.rvalue.type.names
        _var = node.lvalue
        self.visit(_var)
        ## 1. Make sure the location of the assignment is defined
        sym = self.current_scope.lookup(_var.name)
        assert sym, "Assigning to unknown symbol"
        ## Match lside e rside
        left_type = node.lvalue.type.names
        assert left_type == right_type, _line + f"Cannot assign {right_type} to {left_type}"

    def visit_Decl(self, node):
        _line = f"{node.coord.line}:{node.coord.column} - " #TODO fix line error
        name = node.name.name
        self.visit(node.name)
        _temp = self.current_scope.lookup(name)
        assert not _temp, f"{name} declared multiple times"
        
        # check if the declaration has an init value
        if node.init:
            # InitList is an array initialized
            if isinstance(node.init, InitList):
                # check if the array index is a int type
                assert not isinstance(node.type.dim, ID), f"ERROR: the index is not support by the language"  
                assert node.type.dim.type == "int", f"Array index must be of type int"
                # check if the init dimension is equal to the array size
                dim = len(node.init.exprs)     
                assert dim == node.type.dim.value, _line + f"Size mismatch on initialization"
                # check if there is a different type declared inside the array 
                for i in range(dim):
                    assert node.init.exprs[i].type == node.type.type.type.names[0], f"Array contain a different type from initialization"
            
            # Constant can derives from a VarDecl or a String (ArrayDecl)
            elif isinstance(node.init, Constant):    
                # Array
                if isinstance(node.type, VarDecl):
                    const_type = node.init.type
                    assert const_type == node.type.type.names[0], _line + f"Type not match"
                
                # String
                elif isinstance(node.type, ArrayDecl):
                    const_type = node.init.type
                    # a string is an array of char, here we check if the init string is in an variable of char
                    assert const_type == "string" and node.type.type.type.names[0] == "char", _line + f"Type not match"
                    # if there is a declared dimension, we check the string init size matches
                    if node.type.dim is not None:
                        assert node.type.dim.value == (len(node.init.value)-2), f"Size mismatch on initialization"
        
        self.visit(node.type)

    def visit_GlobalDecl(self, node):
        for i in node.decls:
            self.visit(i)
    
    def visit_VarDecl(self, node):
        var_name = node.declname.name
        type_symbol = self.current_scope.lookup(node.type.names[0])
        assert type_symbol is not None, f"Type not defined in language"
        var_symbol = VarSymbol(var_name, type_symbol) #TODO look how make it with arrays (ferra tip: use list of type)
        
        self.current_scope.insert(var_symbol)

    def visit_ArrayDecl(self, node):
        var_name = node.type.declname.name
        type_symbol = self.current_scope.lookup(node.type.type.names[0])
        assert type_symbol is not None, f"Type not defined in language" #TODO parser breaks, idk
        
        # look if the initialize index has type int (here the index is a variable) 
        if node.dim is not None:
            if isinstance(node.dim, ID):
                aux_type = self.current_scope.lookup(node.dim.name)
                assert aux_type.type.name == "int", f"Array index must be of type int"
            else:
                assert node.dim.type == "int", f"Array index must be of type int"
        # array decl can be an array or a string
        if type_symbol.name == "char":
            type_symbol = self.current_scope.lookup("string")
        else:    
            type_symbol = self.current_scope.lookup("array")
        var_symbol = VarSymbol(var_name, type_symbol)
        self.current_scope.insert(var_symbol)

def main():
    import sys
    text = open(sys.argv[1], 'r').read()

    parser = UCParser()
    tree = parser.parse(text)

    semantic_analyzer = SemanticAnalyzer()
    try:
        semantic_analyzer.visit(tree)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()