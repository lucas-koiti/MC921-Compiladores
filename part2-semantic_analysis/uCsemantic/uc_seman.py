# uc Semantic Analysis #

import uc_ast

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

class uCType(Symbol):

    '''
    Class that represents a type in the uC language.  Types 
    are declared as singleton instances of this type.
    '''
    def __init__(self, typename,
                 binary_ops=None, unary_ops=None,
                 rel_ops=None, assign_ops=None):
        
        super().__init__(typename, self)   # TODO look if it works, uCtype its like a BuiltIn, so its also a symbol.
       
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
    def __init__(self, name, type):
            super().__init__(name, type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
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
        self.insert(IntType)
        self.insert(FloatType)
        self.insert(CharType)
        self.insert(ArrayType)
        self.insert(BoolType)
        self.insert(StringType)
        self.insert(PtrType)
        self.insert(VoidType)

    def insert(self, symbol):
        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False):
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
#TODO
# class SemanticAnalyzer(NodeVisitor):
# class Interpreter(NodeVisitor):
