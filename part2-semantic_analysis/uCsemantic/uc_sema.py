# uc Semantic Analysis #
import uc_ast
from uc_parser import UCParser

###################################
#           AST visitor           #
###################################

class NodeVisitor(object):
    """ Classe padrao de visita herdada por todas funcoes de visita em 
    GenerateCode
    """
    _method_cache = None

    def visit(self, node):
        """ Verifica se já existe o método de visita guardado no dicionario,
        se não, obtem o callback, o adiciona e retorna
        """
        if self._method_cache is None:
            self._method_cache = {}
        # tenta obter o metodo do dicicionario de metodos
        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            # se não encontrar, cria o metodo
            method = 'visit_' + node.__class__.__name__
            # tenta obter o metodo de visita especigico de CodeGen, se não encontrarm faz a visita generica
            visitor = getattr(self, method, self.generic_visit)
            # adiciona o metodo de visita da funcao ao dicionario
            self._method_cache[node.__class__.__name__] = visitor
        # retorna o callback da funcao
        return visitor(node)


    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        # visita os elementos de __iter__ do node
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
                 rel_ops     = {"==", "!=", "&&", "||"},
                 assign_ops  = {"="}
                 )

ArrayType = uCType("array",
                 unary_ops   = {"*", "&"},
                 rel_ops     = {"==", "!="},
                 assign_ops  = {"="}
                 )

BoolType = uCType("bool",
                 unary_ops   = {"*", "&", "!"},
                 rel_ops     = {"==", "!=", "&&", "||"},
                 assign_ops  = {"="}
                 )
            
StringType = uCType("string",
                 binary_ops  = {"+"},
                 rel_ops     = {"==", "!="},
                 assign_ops  = {"="}
                 )

PtrType = uCType("ptr",
                 unary_ops   = {"*", "&"},
                 rel_ops     = {"==", "!="},
                 assign_ops  = {"="}
                 )

VoidType = uCType("void",
                 unary_ops   = {"*", "&"},
                 rel_ops     = {"==", "!="},
                 assign_ops  = {"="}
                 )

class BuiltInType(Symbol):
    def __init__(self, name, type):
            super().__init__(name, type)
            #self.kind = "tipo" 

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

class VarSymbol(Symbol):
    def __init__(self, name, type):
            super().__init__(name, type)
            #self.kind = "var"

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__

# TODO tinha adicionado dim aqui
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
            #self.kind = "ptr"

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
        #self.kind = "func" 

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
        # print('Insert: %s' % symbol.name)
        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False):
        # print('Lookup: %s. (Scope name: %s)' % (name, self.scope_name))
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
        #print('ENTER scope: global')
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

        #print(global_scope)
        
        self.current_scope = self.current_scope.enclosing_scope
        #print('LEAVE scope: global')
        #print("Semantic Analysis finished Successfully - Have a Nice Day!")
    
    def visit_GlobalDecl(self, node):
        for i in node.decls:
            self.visit(i)
    
    def visit_InitList(self, node):
        # return a list with every item type
        _initlistaux = []
        _initvalues = []
        
        for _i in range(len(node.exprs)):
            if isinstance(node.exprs[_i], uc_ast.InitList):
                node.exprs[_i].type = node.type
                n, k = self.visit(node.exprs[_i])
                #node.dimaux.append(node.exprs[_i].dimaux)
                _initlistaux.append(n)
                _initvalues.append(k)
                #_initlistaux.append(self.visit(node.exprs[_i]))

            else:
                if isinstance(node.exprs[_i], uc_ast.ID):
                    _typeaux = self.current_scope.lookup(node.exprs[_i].name)
                    assert _typeaux, f"ERROR: Variable: {node.exprs[_i].name} used in array initialization was not declared"
                    _typeaux = _typeaux.type.name
                    assert node.type == _typeaux, f"ERROR: Array contain a different type from initialization"
                    _initlistaux.append(_typeaux)
                else:
                    assert node.type == node.exprs[_i].type, f"ERROR: Array contain a different type from initialization"
                    _initlistaux.append(node.exprs[_i].type)
                    _initvalues.append(node.exprs[_i].value)
        
        
        # assign the list of inits to the node, helps in IRcodegen
        #node.values = _initvalues
        #print(node.values)
        
        return _initlistaux, _initvalues

    def visit_Decl(self, node):
        name = node.name.name
        #self.visit(node.name) #TODO wait if some test breaks here
        # check if the var was already declared in the current_scope (don't look to the global)
        _temp = self.current_scope.lookup(name, True) 
        assert not _temp, f"ERROR: {name} declared multiple times"
        # check if the declaration has an init value
        if node.init:
            # InitList is an array initialized
            if isinstance(node.init, uc_ast.InitList):
                if node.type.dim is not None:
                    _dimaux = node.type
                    _auxlistdim = []
                    # here, get every index size value and the array type
                    while isinstance(_dimaux, uc_ast.ArrayDecl):
                        _auxlistdim.append(_dimaux.dim.value)
                        if isinstance(_dimaux.type, uc_ast.VarDecl):
                            _typeaux = _dimaux.type.type.names[0]
                            break
                        else:
                            _dimaux = _dimaux.type
                    # store the list of sizes in the node, helps in IR code gen
                    node.type.auxdim = _auxlistdim
                    node.type.aux = _auxlistdim
                    # get the init list as a list of every item type (eg. [[int],[int,int]]) and check if is the right init value
                    node.init.type = _typeaux
                    _auxlisttypes, _auxlistvalues= self.visit(node.init)
                    # store the list of values in the node, helps in IR code gen
                    node.type.values = _auxlistvalues 
                    # check if the index matches to init size
                    _tmp = _auxlisttypes
                    _i = 0
                    while _i < len(_auxlistdim):
                        if isinstance(_tmp, str):
                            break
                        assert len(_tmp) == _auxlistdim[_i], f"ERROR: Array size mismatch - index: {_auxlistdim[_i]} size:{len(_tmp)}"
                        _tmp = _tmp[0]
                        _i += 1
                #check items type when dim is []
                else:
                    for _i in node.init.exprs:
                        assert _i.type == node.type.type.type.names[0], f"ERROR: Array contain a different type from initialization"
                    node.init.type = node.type.type.type.names[0]
                    _aux, values = self.visit(node.init)
                    node.type.auxdim = [len(_aux)]
                    node.type.values = values
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
                    # information to IRgencode
                    node.type.typeaux = "string"
                    node.type.auxdim = [len(node.init.value)-2]
                    node.type.values = node.init.value[1:-1]
            # init value is a parameter variable
            elif isinstance(node.init, uc_ast.ID):
                self.visit(node.init)
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
            
            elif isinstance(node.init, uc_ast.FuncCall): 
                self.visit(node.init)
                assert node.type.type.names[0] == node.init.type, f"ERROR: FunCall return does not match to VarDecl type"   
        else:
            if isinstance(node.type, uc_ast.ArrayDecl):
                assert node.type.dim, f"ERROR: Array without init must have an index"
                _dimaux = node.type
                _auxlistdim = []

                # here, get every index size value and the array type
                while isinstance(_dimaux, uc_ast.ArrayDecl):
                    _auxlistdim.append(_dimaux.dim.value)
                    if isinstance(_dimaux.type, uc_ast.VarDecl):
                        _typeaux = _dimaux.type.type.names[0]
                        break
                    else:
                        _dimaux = _dimaux.type
                # store the list of sizes in the node, helps in IR code gen
                node.type.auxdim = _auxlistdim
                node.type.aux = _auxlistdim
        # to help IRgencode
        if isinstance(node.type, uc_ast.ArrayDecl):
            if node.type.dim != None:
                node.type.auxdim = [node.type.dim.value]
            node.type.name = node.name.name

        # declare the symbol
        self.visit(node.type)


    def visit_VarDecl(self, node):
        var_name = node.declname.name
        type_symbol = self.current_scope.lookup(node.type.names[0])

        assert type_symbol is not None, f"ERROR: Type not defined in language"

        var_symbol = VarSymbol(var_name, type_symbol) 
        self.current_scope.insert(var_symbol)


    def visit_ArrayDecl(self, node):
        if isinstance(node.type, uc_ast.VarDecl):
            var_name = node.type.declname.name
            type_symbol = self.current_scope.lookup(node.type.type.names[0])
            _auxtype = type_symbol.name
            assert type_symbol is not None, f"ERROR: Type not defined in language" 
            node.typeaux = type_symbol.name
            # check size and type
            self._auxArraySizeType(node)
            
            # array decl can be an array or a string
            if type_symbol.name == "char":
                type_symbol = self.current_scope.lookup("string")
            else:    
                type_symbol = self.current_scope.lookup("array")

            var_symbol = ArraySymbol(var_name, type_symbol, _auxtype)
            self.current_scope.insert(var_symbol)
        # recursively access to more than one dimension v[][]..
        else:
            # check size and types in every level
            self._auxArraySizeType(node)
            self.visit(node.type)
            node.typeaux = node.type.typeaux
        

    def _auxArraySizeType(self, node):
        # look if the initialize index has type int (here the index is a variable) 
        if node.dim is not None:
            if isinstance(node.dim, uc_ast.ID):
                aux_type = self.current_scope.lookup(node.dim.name)
                assert aux_type, f"ERROR: Index has no value declared"
                assert aux_type.type.name == "int", f"ERROR: Array index must be of type int"
            else:
                assert node.dim.type == "int", f"ERROR: Array index must be of type int"


    def visit_ArrayRef(self, node):
        if isinstance(node.name, uc_ast.ID):
            # check semantics
            _name = node.name.name
            _symbol = self.current_scope.lookup(_name)
            assert _symbol, f"ERROR: Reference to a undeclared array {_name}"
            self._ArrayRefCheck(node)
            # return the array type - assign it to the node
            node.type = _symbol.auxtype
            return node.type
        else:
            # check semantics in every level
            self._ArrayRefCheck(node)
            node.type = self.visit(node.name)


    def _ArrayRefCheck(self, node):
        # check if the reference is semantic correct
        _index = node.subscript
        if isinstance(_index, uc_ast.ID):
            _aux = self.current_scope.lookup(_index.name)
            assert _aux, f"ERROR: Index variable reference was not defined"
            assert _aux.type.name == "int", f"ERROR: Array index reference must be of int type"
        else:
            assert node.subscript.type == "int", f"ERROR: Array index reference must be of int type"


    def visit_FuncDef(self, node):
        # visit the decl to see if its possible put the function symbol in the table
        self.visit(node.decl)
        
        # change to the function scope
        #print('ENTER Scope: %s' %node.decl.name.name)
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
            assert not self.current_scope.lookup(p_name, True), f"ERROR: {p_name} declared multiple times"
            var_symbol = VarSymbol(p_name, p_type)
            self.current_scope.insert(var_symbol)
        # visit the function body
        self.visit(node.body)
        # leave the current function and get back to global scope
        self.current_scope = self.current_scope.enclosing_scope
        #print('LEAVE scope %s' %node.decl.name.name)


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
        if node.block_items:
            for _i in node.block_items:
                self.visit(_i)


    def visit_FuncCall(self, node):
        # check if it is semantically ok
        _funcname = node.name.name
        _auxfunc = self.current_scope.lookup(_funcname)
        assert _auxfunc != None, f"ERROR: Function calls has an undeclared function"
        _params = _auxfunc.params
        # check if the parameters number is ok
        # check if the parameters type matches
        
        if isinstance(node.args, uc_ast.ExprList):
            # case with more than one parameter
            _exprlist = node.args.exprs
            assert len(_params) == len(_exprlist), f"ERROR: Functioncall has missing/excede parameters"
            for _i in range(len(_params)):
                if isinstance(_exprlist[_i], uc_ast.ID):
                    self.visit(_exprlist[_i])
                    _type = self.current_scope.lookup(_exprlist[_i].name)
                    assert _type != None, f"ERROR: Functioncall has a parameter being a not declared variable"
                    _type = _type.type.name
                else:
                    self.visit(_exprlist[_i])
                    _type = _exprlist[_i].type
                assert _params[_i][1] == _type, f"ERROR: FunctionCall has wrong types parameters"
        else:
            # case with a single parameter
            if node.args:
                assert node.args and (1 == len(_params)), f"ERROR: Function call has missing/extra parameters"
                if isinstance(node.args, uc_ast.ID):
                        self.visit(node.args)
                        _type = self.current_scope.lookup(node.args.name)
                        assert _type != None, f"ERROR: FunctionCall has a parameter being a not declared variable"
                        _type = _type.type.name
                else:
                    self.visit(node.args) 
                    _type = node.args.type
                assert _params[0][1] == _type, f"ERROR: FunctionCall has wrong types parameters"
        
        # return the function type - assign it to the node
        node.type = _auxfunc.type.name
        return node.type


    def visit_For(self, node):
        # visit every node
        if node.init != None:  
            self.visit(node.init)
        if node.cond != None:
            self.visit(node.cond) 
        if node.next != None:
            self.visit(node.next)
        #assert node.stmt.block_items, f"ERROR: (For) must have an statement"
        self.visit(node.stmt)
    

    def visit_While(self, node):
        # just visi the condition and statement
        self.visit(node.cond)
        self.visit(node.stmt)


    def visit_If(self, node):
        # check if has a declared statement in iftrue and go to visit iffalse if there is an statement there
        self.visit(node.cond)
        self.visit(node.iftrue)
        if node.iffalse != None:
            self.visit(node.iffalse)
    
    def visit_Cast(self, node):
        # visit the expr to validate
        self.visit(node.expr)
        node.type = node.to_type.names[0]

    def visit_Assert(self, node):
        # visit the expr to validate
        self.visit(node.expr)

    def visit_Read(self, node):
        # check if there is an argument
        self.visit(node.expr)

    def visit_Print(self, node): 
        if node.expr != None:
            self.visit(node.expr)

    def visit_ExprList(self, node):
        # check every node in the list
        for _i in node.exprs:
            self.visit(_i)

    def visit_UnaryOp(self, node):
        if isinstance(node.expr, uc_ast.ID):
            self.visit(node.expr)
            _name = node.expr.name
        else: # not sure if a unaryop is always over an ID
            print("dude, look for error here")
        # check if the var was declared
        _vardecl = self.current_scope.lookup(_name)
        assert _vardecl != None, f"ERROR: Unary operation variable was not declared"

        # check if support the operation
        assert node.op in _vardecl.type.type.unary_ops, f"ERROR: This {node.op} operation isn't support by the language"

        # return the same type = assign the node
        node.type = _vardecl.type.name
        return node.type

    def _auxBinOp_typeof(self, node):
        _type = None

        # define the type recursively
        if isinstance(node, uc_ast.Constant):
            _type = node.type
        elif isinstance(node, uc_ast.ID):
            _type = self.visit(node)
            #_aux = self.current_scope.lookup(node.name)
            #_type = _aux.type.name
        elif isinstance(node, uc_ast.ArrayRef):
            self.visit(node)
            _aux = self.current_scope.lookup(node.name.name)
            _type = _aux.auxtype
        elif isinstance(node, uc_ast.FuncCall):
            _type = self.visit(node)
            #_aux = self.current_scope.lookup(node.name.name)
            #_type = _aux.type.name
        elif isinstance(node, uc_ast.UnaryOp):
            _type = self.visit(node)
        elif isinstance(node, uc_ast.BinaryOp):
            _type = self.visit(node)
        elif isinstance(node, uc_ast.Cast):
            self.visit(node)
            _type = node.to_type.names[0] 
        
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
        assert (node.op in _auxtype.type.binary_ops) or (node.op in _auxtype.type.rel_ops), f"ERROR: Operation not supported by the language"
        
        # Assign the result type
        if isinstance(node, uc_ast.BinaryOp):
            # if the binary ops do a rel_ops, results in a boolean type
            if node.op in _auxtype.type.rel_ops:
                node.type = "bool"
            else:
                node.type = _ltype

        return node.type
        
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
                self.visit(node.expr)
                _auxtype = self.current_scope.lookup(node.expr.name)
                assert _auxtype is not None, f"ERROR: {node.expr.name} has no value to return"
                _ret_types.append(_auxtype.type.name)
            else:
                self.visit(node.expr)
                _ret_types.append(node.expr.type)

            # check if all the return itens matches to the function type
            
            if _functype.type.name == "void": # void func can return 0, so here we let return anything 
                for _i in _ret_types:
                    assert _functype.type.name == _i, f"ERROR: return value not match to the function type"
        else:
            _ret_types.append("void")
            assert _functype.type.name == _ret_types[0], f"ERROR: return must be void"
                        

    def visit_Assignment(self, node): 
        # visit the right side to see if its ok
        self.visit(node.rvalue)   
        # look to the right side type
        _right_type = node.rvalue.type
        
        # check the left side to see if its ok 
        self.visit(node.lvalue)
        # look to the left side type
        _left_type = node.lvalue.type

        # check the location of the assignment is defined
        _sym = self.current_scope.lookup(_left_type)
        #assert _sym, f"ERROR: {_var.name} was not declared"

        # check if has operation support by the type
        assert node.op in _sym.type.assign_ops, f"ERROR: {node.op} not supported by type:{_sym.name}"
        
        # check if both sides types matches
        assert _left_type == _right_type, f"ERROR: Cannot assign {_right_type} to {_left_type}"

    def visit_ID(self, node):
        # just check if it was declared
        _auxID = self.current_scope.lookup(node.name) 
        assert _auxID, f"ERROR: ID:{node.name} not declared"
        
        # return the type - assign it to the ast node
        node.type = _auxID.type.name
        return node.type
        
    def visit_EmptyStatement(self, node):
        pass

# list of unused nodes
    # def visit_Constant(self, node):
    # def visit_DeclList(self, node):
    # def visit_Type(self, node):
    # def visit_Break(self, node):

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