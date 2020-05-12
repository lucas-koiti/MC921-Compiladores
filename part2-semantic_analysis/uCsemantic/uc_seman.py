# uc Semantic Analysis #
import uc_ast
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
                 binary_ops  = {"+"},
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
            self.kind = "tipo" # TODO remember why i did this

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

class VarSymbol(Symbol):
    def __init__(self, name, type):
            super().__init__(name, type)
            # to identifies the array type
            self.kind = "var"

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__

class ArraySymbol(Symbol):
    def __init__(self, name, type, auxtype=None):
            super().__init__(name, type)
            self.auxtype = auxtype

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}, auxtype='{auxtype}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
            auxtype=self.auxtype
        )

    __repr__ = __str__

class PtrSymbol(Symbol):
    def __init__(self, name, type):
            super().__init__(name, type)
            self.kind = "ptr"

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__

class FuncSymbol(Symbol):
    def __init__(self, name, type, params=None):
        super().__init__(name, type)
        # a list of formal parameters
        self.params = params if params is not None else []
        self.kind = "func" #TODO remember why use this

    def __str__(self):
        return '<{class_name}(name={name},type={type}, params={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
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
        # define global scope
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope, # None
        )
        global_scope._init_builtins()
        self.current_scope = global_scope

        # Visit all of the global declarations
        for _decl in node.gdecls:
            self.visit(_decl)

        print(global_scope)
        
        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: global')
        print("Semantic Analysis Successfully - Have a Nice Day!")
    
    def visit_GlobalDecl(self, node):
        for i in node.decls:
            self.visit(i)

    def visit_Decl(self, node):
        # first, check all possible errors
        name = node.name.name
        self.visit(node.name)
        _temp = self.current_scope.lookup(name)
        assert not _temp, f"ERROR: {name} declared multiple times"
    
        # check if the declaration has an init value
        if node.init:
            # InitList is an array initialized
            if isinstance(node.init, uc_ast.InitList):
                if node.type.dim is not None:
                    # check if the array index is a int type
                    assert not isinstance(node.type.dim, uc_ast.ID), f"ERROR: the index is not support by the language"  
                    assert node.type.dim.type == "int", f"ERROR: Array index must be of type int"
                    # check if the init dimension is equal to the array size
                    dim = len(node.init.exprs)     
                    assert dim == node.type.dim.value, f"ERROR: Size mismatch on initialization"
                    # check if there is a different type declared inside the array 
                    for i in range(dim):
                        assert node.init.exprs[i].type == node.type.type.type.names[0], f"ERROR: Array contain a different type from initialization"
            
            # Constant can derives from a VarDecl or a String (ArrayDecl)
            elif isinstance(node.init, uc_ast.Constant):    
                # Array
                if isinstance(node.type, uc_ast.VarDecl):
                    const_type = node.init.type
                    assert const_type == node.type.type.names[0], f"ERROR: Type not match"
                
                # String
                elif isinstance(node.type, uc_ast.ArrayDecl):
                    const_type = node.init.type
                    # a string is an array of char, here we check if the init string is in an variable of char
                    assert const_type == "string" and node.type.type.type.names[0] == "char", f"ERROR: Type not match"
                    # if there is a declared dimension, we check the string init size matches
                    if node.type.dim is not None:
                        assert node.type.dim.value == (len(node.init.value)-2), f"ERROR: Size mismatch on initialization"

            # init value is a parameter variable
            elif isinstance(node.init, uc_ast.ID):
                _name = self.current_scope.lookup(node.init.name)
                assert _name != None, f"ERROR: {node.init.name} was not declared"
                _type = _name.type.name
                assert _type == node.type.type.names[0], f"ERROR: {_name.name} type not match"
            
            # init value derives from a binary operation
            elif isinstance(node.init, uc_ast.BinaryOp):
                self.visit(node.init)
                if isinstance(node.type, uc_ast.VarDecl):
                    assert node.init.type == node.type.type.names[0], f"ERROR: binary operation type not match"
                else:
                    _aux = node.type.type.type.names[0]
                    if _aux == "char": # here its an array, so we have a string
                        _aux = "string" 
                    assert node.init.type == _aux, f"ERROR: binary operation type not match"
            else: #possible error
                print("Dude, u'r missing something")

        # declare the symbol
        self.visit(node.type)

    def visit_VarDecl(self, node):
        var_name = node.declname.name
        type_symbol = self.current_scope.lookup(node.type.names[0])
        assert type_symbol is not None, f"TERROR: ype not defined in language"
        var_symbol = VarSymbol(var_name, type_symbol) #TODO look how make it with arrays (ferra tip: use list of type)
        
        self.current_scope.insert(var_symbol)

    def visit_ArrayDecl(self, node):
        var_name = node.type.declname.name
        type_symbol = self.current_scope.lookup(node.type.type.names[0])
        _auxtype = type_symbol.name
        assert type_symbol is not None, f"ERROR: Type not defined in language" #TODO parser breaks, idk
        
        # look if the initialize index has type int (here the index is a variable) 
        if node.dim is not None:
            if isinstance(node.dim, uc_ast.ID):
                aux_type = self.current_scope.lookup(node.dim.name)
                assert aux_type, f"ERROR: Index has no value declared"
                assert aux_type.type.name == "int", f"ERROR: Array index must be of type int"
            else:
                assert node.dim.type == "int", f"ERROR: Array index must be of type int"
       
        # array decl can be an array or a string
        if type_symbol.name == "char":
            type_symbol = self.current_scope.lookup("string")
        else:    
            type_symbol = self.current_scope.lookup("array")
        var_symbol = ArraySymbol(var_name, type_symbol, _auxtype)
        self.current_scope.insert(var_symbol)

    def visit_FuncDef(self, node):
        # visit the decl to see if its possible put the function symbol in the table
        self.visit(node.decl)
        
        # change to the function scope
        print('ENTER Scope: %s' %node.decl.name.name)
        procedure_scope = ScopedSymbolTable(
            scope_name = node.decl.name.name,
            scope_level = self.current_scope.scope_level + 1,
            enclosing_scope = self.current_scope
        )
        self.current_scope = procedure_scope

        # insert the function params to the current scoped symbol table
        _auxname = self.current_scope.scope_name
        _funcdef = self.current_scope.lookup(_auxname)
        _params = _funcdef.params
        for p in _params:
            p_type = self.current_scope.lookup(p[1])
            assert p_type is not None, f"ERROR: Type not defined in language"
            p_name = p[0]
            assert not self.current_scope.lookup(p_name), f"ERROR: {p_name} declared multiple times"
            var_symbol = VarSymbol(p_name, p_type)
            self.current_scope.insert(var_symbol)

        # visit the function body
        self.visit(node.body)

        print(procedure_scope)
        # leave the current function and get back to global scope
        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope %s' %node.decl.name.name)

    def visit_FuncDecl(self, node):
        # check the params
        _params = None
        if node.args is not None:
            _params = self.visit(node.args)
        
        # create a function symbol and store in the symboltable
        _functype = self.current_scope.lookup(node.type.type.names[0])
        _funcaux = FuncSymbol(node.type.declname.name, _functype, _params)
        self.current_scope.insert(_funcaux)

    def visit_Compound(self, node):
        # check every item in the block
        for i in node.block_items:
            self.visit(i)

    def visit_ArrayRef(self, node):
        # check if the reference is semantic correct
        _name = node.name.name
        assert self.current_scope.lookup(_name), f"ERROR: Reference to a undeclared array"
        _index = node.subscript
        if isinstance(_index, uc_ast.ID):
            _aux = self.current_scope.lookup(_index.name)
            assert _aux, f"ERROR: Index variable reference was not defined"
            assert _aux.type.name == "int", f"ERROR: Array index reference must be of int type"
        else:
            assert node.subscript.type == "int", f"ERROR: Array index reference must be of int type"

    def visit_FuncCall(self, node):
        # check if it is semantically ok
        _funcname = node.name.name
        _params = self.current_scope.lookup(_funcname)
        assert _params != None, f"ERROR: Function calls a undeclared function"
        _params = _params.params
        # check if the parameters number is ok
        # check if the parameters type matches
        if isinstance(node.args, uc_ast.ExprList):
            # case with more than one parameter
            _exprlist = node.args.exprs
            assert len(_params) == len(_exprlist), f"ERROR: Function call has missing/excede parameters"
            for _i in range(len(_params)):
                if isinstance(_exprlist[_i], uc_ast.ID):
                    _type = self.current_scope.lookup(_exprlist[_i].name)
                    assert _type != None, f"ERROR: Function call has a parameter being a not declared variable"
                    _type = _type.type.name
                else:
                    _type = _exprlist[_i].type
                assert _params[_i][1] == _type, f"ERROR: Function call has wrong types parameters"
        else:
            # case with a single parameter
            assert len(_params) == 1, f"ERROR: Function call has missing parameters"
            if isinstance(node.args, uc_ast.ID):
                    _type = self.current_scope.lookup(node.args.name)
                    assert _type != None, f"ERROR: Function call has a parameter being a not declared variable"
                    _type = _type.type.name
            else:
                _type = node.args.type
            assert _params[0][1] == _type, f"ERROR: Function call has wrong types parameters"

    def visit_For(self, node): #TODO finish this
        self.visit(node.init)
        print(node.cond)
        self.visit(node.cond)
        #self.visit(node.next)
        #self.visit(node.stmt)
        #self.visit(node.coord)

    def _auxBinOp_typeof(self, node):
        _type = None

        # define the type recursively
        if isinstance(node, uc_ast.Constant):
            _type = node.type
        elif isinstance(node, uc_ast.ID):
            _aux = self.current_scope.lookup(node.name)
            _type = _aux.type.name
        elif isinstance(node, uc_ast.ArrayRef):
            self.visit(node)
            _aux = self.current_scope.lookup(node.name.name)
            _type = _aux.auxtype
        elif isinstance(node, uc_ast.FuncCall):
            self.visit(node)
            _aux = self.current_scope.lookup(node.name.name)
            _type = _aux.type.name
        elif isinstance(node, uc_ast.BinaryOp):
            _type = self.visit(node) 
        
        return _type

    def visit_BinaryOp(self, node):
        # Make sure left and right operands have the same type
        _ltype = None
        _rtype = None

        _ltype = self._auxBinOp_typeof(node.left)
        _rtype = self._auxBinOp_typeof(node.right)

        assert _ltype == _rtype, f"ERROR: Type mismatch in the expression"
    
        # Make sure the operation is supported
        _auxtype = self.current_scope.lookup(_ltype)
        assert node.op in (_auxtype.type.binary_ops or _auxtype.type.rel_ops), f"ERROR: Operation not supported by the language"
        
        # Assign the result type
        if isinstance(node, uc_ast.BinaryOp):
            node.type = _ltype

        return _ltype
        
    def visit_ParamList(self, node):
        # will return all the params in a list like [[param, typeofparam], ...]
        _params = []
        for _i in range(len(node.params)):
            _auxparam = [node.params[_i].name.name, node.params[_i].type.type.names[0]]
            _params.append(_auxparam)
    
        return _params
    
    def visit_Return(self, node): 
        # return a list of types
        _ret_types = []
        _scopename = self.current_scope.scope_name
        _functype = self.current_scope.lookup(_scopename)

        if node.expr is not None:
            if isinstance(node.expr, uc_ast.ExprList):
                for _i in range(len(node.expr.exprs)):
                    if isinstance(node.expr.exprs[_i], uc_ast.ID):
                        _aux = self.current_scope.lookup(node.expr.exprs[_i].name)
                        assert _aux is not None, f"ERROR: {node.expr.exprs[_i].name} has no value to return"
                        _ret_types.append(_aux.type.name)
                    else:
                        _ret_types.append(node.expr.exprs[_i].type)   
            elif isinstance(node.expr, uc_ast.ID):
                _auxtype = self.current_scope.lookup(node.expr.name)
                assert _auxtype is not None, f"ERROR: {node.expr.name} has no value to return"
                _ret_types.append(_auxtype.type.name)
            else:
                self.visit(node.expr)
                _ret_types.append(node.expr.type)

            # check if all the return itens matches to the function type
            if _functype.type.name != "void": # void func can return 0, so here we let return anything 
                for _i in _ret_types:
                    assert _functype.type.name == _i, f"ERROR: return value not match to the function type"
        else:
            _ret_types.append("void")
            if _functype.type.name != _ret_types[0]:
                print("WARNING: you're returning void, maybe you should consider return a value equal to the function's type")        

    def visit_Assignment(self, node): #TODO check every op (ASSIGNMENT-OPERATOR)
        # visit the right side to see if its ok
        self.visit(node.rvalue)
        
        # look to the right side type
        _right_type = node.rvalue.type
        _var = node.lvalue
        # check the left side to see if its ok TODO look how to optimize this left side
        self.visit(_var)

        # check the location of the assignment is defined
        _sym = self.current_scope.lookup(_var.name)
        assert _sym, f"ERROR: {_var.name} was not declared"

        # check if both sides types matches
        assert _sym.type.name == _right_type, f"ERROR: Cannot assign {_right_type} to {_sym.type.name}"

    #TODO list of NODES i think don't need be visited
    def visit_Constant(self, node):
        pass
    
    def visit_ID(self, node):
        pass

    def visit_ExprList(self, node):
        pass

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