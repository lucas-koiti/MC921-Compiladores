from uc_sema import NodeVisitor, ScopedSymbolTable
import uc_ast

class GenerateCode(NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self):
        super(GenerateCode, self).__init__()

        # version dictionary for temporaries
        self.fname = 'main'  # We use the function name as a key
        self.versions = {self.fname:0}

        # store some temporaries
        self.temps = {}
        self.globals = {}

        # string counter
        self.str_counter = 0

        # ops dictionary
        self.binaryop = {
                            '+' : "add",
                            '-' : "sub",
                            '*' : "mul",
                            '/' : "div",
                            '%' : "mod"
                            '''relops''' 
                        }

        # The generated code (list of tuples)
        self.code = []


    def new_temp(self):
        '''
        Create a new temporary variable of a given scope (function name).
        '''
        if self.fname not in self.versions:
            self.versions[self.fname] = 0
        name = "%" + "%d" % (self.versions[self.fname])
        self.versions[self.fname] += 1
        return name

    ####################################
    #           AST visitors           #
    ####################################

    def visit_Program(self, node):
        # get scope to distinguish global from functions
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=None, # None
        )
        self.current_scope = global_scope

        # Visit all of the global declarations
        for _decl in node.gdecls:
            self.visit(_decl)

        self.current_scope = self.current_scope.enclosing_scope


    def visit_GlobalDecl(self, node):
        # Visit all decls
        for i in node.decls:
            self.visit(i)
    

    def visit_Decl(self, node):
        if isinstance(node.type, uc_ast.VarDecl):
            if node.init:
                if isinstance(node.init, uc_ast.Constant):
                    node.type.value = node.init.value
                    node.type.valuetmp = node.init
                elif isinstance(node.init, uc_ast.BinaryOp):
                    node.type.value = 1                         # kind of a boolean when a init value is an expression
                    node.type.valuetmp = node.init              # pass the init type to call later and get processed
                elif isinstance(node.init, uc_ast.FuncCall):
                    node.type.value = None
                    node.type.valuetmp = node.init

        elif isinstance(node.type, uc_ast.ArrayDecl):
            if isinstance(node.init, uc_ast.BinaryOp):
                node.type.values = node.init
            if node.type.aux:
                node.type.auxdim = node.type.aux
        

        self.visit(node.type)

    def visit_VarDecl(self, node):
        if self.current_scope.scope_name == "global":
            inst = ('global_'+ node.type.names[0], '@'+node.declname.name, node.value)
            self.code.append(inst)
            self.globals[node.declname.name] = node.value
        else:
            # allocate on stack memory
            _tmp = self.new_temp()
            inst = ('alloc_' + node.type.names[0], _tmp)
            self.code.append(inst)
            # store optional init val
            if node.value:
                _gen = self.visit(node.valuetmp)
                inst = ('store_' + node.type.names[0], _gen, _tmp)
                self.code.append(inst)
            
            # store the temporary used in dict
            self.temps[node.declname.name] = _tmp
            
            # store init value when its a func call result
            if isinstance(node.valuetmp, uc_ast.FuncCall):
                _freturn = self.visit(node.valuetmp)
                inst = ('store_'+node.valuetmp.type, _freturn, _tmp)
                self.code.append(inst)

    def visit_FuncCall(self, node):   
        if isinstance(node.args, uc_ast.ExprList):
            for _k in node.args.exprs:
                _target = self.new_temp()
                _src = self.temps.get(_k.name)
                inst = ('load_'+_k.type, _src, _target)
                self.code.append(inst)
                inst = ('param_'+_k.type, _target)
                self.code.append(inst)
        elif isinstance(node.args, uc_ast.ID):
            _target = self.new_temp()
            _src = self.temps.get(node.args.name)
            inst = ('load_'+node.args.type, _src, _target)
            self.code.append(inst)
            inst = ('param_'+node.args.type, _target)
            self.code.append(inst)

        elif isinstance(node.args, uc_ast.Constant):
            _target = self.new_temp()
            inst = ('literal_'+node.args.type, node.args.value, _target)
            self.code.append(inst)
            inst = ('param_'+node.args.type, _target)
            self.code.append(inst)
        
        _freturn = self.new_temp()
        inst = ('call', '@'+node.name.name, _freturn)
        self.code.append(inst)

        return _freturn


    def visit_BinaryOp(self, node):
        # get left and right temporaries
        _ltemp = self.visit(node.left)
        _rtemp = self.visit(node.right)

        # create a target to store result
        _target = self.new_temp()

        # process
        inst = (self.binaryop[node.op]+"_"+node.type, _ltemp, _rtemp, _target)
        self.code.append(inst)

        # return the target used
        return _target

    def visit_ID(self, node):
        # plus 1 because its the stored temporary used in FuncDecl
        _src = self.temps.get(node.name+"1")
        _target = self.new_temp()
        # in case the variable isn't in the scope, he consider it is in global
        if _src:  
            inst = ('load_'+node.type, _src, _target)
        else:
            inst = ('load_'+node.type, '@'+node.name, _target)
        
        self.code.append(inst)

        return _target
         
    def visit_Constant(self, node):
        _gen = self.new_temp()
        inst = ('literal_'+ node.type, node.value, _gen)
        self.code.append(inst)
        return _gen

    def visit_ArrayDecl(self, node):
        # get the dimension subscript to process
        _underdim = ""
        for _k in node.auxdim:
            _underdim += "_"+str(_k)
        
        if self.current_scope.scope_name == "global":
            if node.values is None:
                inst = ('global_'+ node.typeaux + _underdim, '@'+ node.name)
            else:
                inst = ('global_'+ node.typeaux + _underdim, '@'+ node.name, node.values)
            self.code.append(inst)   
        else:
            _tmp = self.new_temp()

            inst = ('alloc_'+ node.typeaux + _underdim, _tmp)
            self.code.append(inst)
            
            if node.values:
                if isinstance(node.values, uc_ast.BinaryOp):
                    # DARK ZONE, WHEN INITIALIZE WITH STRING CONCATENATE
                    inst = ('alloc_'+node.typeaux+'_', _tmp)
                    self.code.append(inst)
                    _conc = self.visit(node.values)    
                    inst = ('store_' + node.typeaux+", "+ _conc, _tmp)
                    self.code.append(inst)   
                else:
                    # process the string initialized
                    _str = '@.str.'+str(self.str_counter)
                    inst = ('global_'+ node.typeaux + _underdim, _str , node.values)
                    self.str_counter += 1
                    # find where to declare in the code flow
                    _i = 0
                    while 'global' in self.code[_i][0]:
                        _i += 1
                    # insert in the right spot
                    self.code.insert(_i, inst)

                    # store in the declared temporary
                    inst = ('store_'+ node.typeaux + _underdim, _str, _tmp)
                    self.code.append(inst)
                    
            self.temps[node.name] = _tmp


    def visit_FuncDef(self, node):
        # get into a new scope to help in any Decl
        procedure_scope = ScopedSymbolTable(
            scope_name = node.decl.name.name,
            scope_level = self.current_scope.scope_level + 1,
            enclosing_scope = self.current_scope
        )
        self.current_scope = procedure_scope
        self.fname = self.current_scope.scope_name
        # func declaration
        self.visit(node.decl)
        # func body
        self.visit(node.body)
        # get out of the scope
        self.temps.clear()
        self.current_scope = self.current_scope.enclosing_scope


    def visit_FuncDecl(self, node):
        inst = ('define', '@'+node.type.declname.name)
        self.code.append(inst)

        if node.type.declname.name == "main":
            self.temps['return'] = self.new_temp()
            self.temps['label1'] = self.new_temp()
        
        else:
            if node.args:
                # create pass params temporaries
                for _i in range(len(node.args.params)):
                    self.temps[node.args.params[_i].name.name] = self.new_temp()

                # create a temporary to store return value
                self.temps['return'] = self.new_temp()
                
                # alloc temporaries to receive the params
                for _k in range(len(node.args.params)):
                    _tmp = self.new_temp()
                    _type = node.args.params[_k].type.type.names[0]
                    inst = ('alloc_'+_type, _tmp)
                    self.code.append(inst)
                    self.temps[node.args.params[_k].name.name+"1"] = _tmp

                # store the params in the allocate temporaries
                for _j in range(len(node.args.params)):
                    _type = node.args.params[_j].type.type.names[0]
                    _src = self.temps[node.args.params[_j].name.name]
                    _target = self.temps[node.args.params[_j].name.name+"1"]
                    inst = ('store_'+_type, _src, _target)
                    self.code.append(inst)

                    # look if it is necessary att the value in temps
                    #self.temps[self.temps[node.args.params[_j].name.name]] = _target

                # create a jump label to return
                self.temps['label1'] = self.new_temp()
            else:
                # in @main we just need reserve temporaries to return and jump return
                self.temps['return'] = self.new_temp()
                self.temps['label1'] = self.new_temp()

    def visit_Assignment(self, node):
        _gen = self.visit(node.rvalue)                      # gets the temporary used (eg. 'a': %2)
        _target = self.temps[node.lvalue.name]              # access the global dict with declared variables
        inst = ('store_'+ node.lvalue.type, _gen, _target)  
        self.code.append(inst)


    def visit_Compound(self, node):
        # check every item in the block
        for _i in node.block_items:
            self.visit(_i)


    def visit_Return(self, node):
        if node.expr:
            if isinstance(node.expr, uc_ast.BinaryOp):
                _return = self.visit(node.expr)
                inst = ('store_'+node.expr.type, _return, self.temps.get('return'))
                self.code.append(inst)
            
            elif isinstance(node.expr, uc_ast.Constant):
                _target = self.new_temp()
                inst = ('literal_'+node.expr.type, node.expr.value, _target)
                self.code.append(inst)
                inst = ('store_'+node.expr.type, _target, self.temps.get('return'))
                self.code.append(inst)
            
            elif isinstance(node.expr, uc_ast.ID):
                _src = self.temps.get(node.expr.name)
                _target = self.temps.get('return')
                inst = ('store_'+node.expr.type, _src, _target)
                self.code.append(inst)
                
        inst = ('jump', self.temps['label1'])
        self.code.append(inst)
        inst = (self.temps['label1'][1:],)
        self.code.append(inst)
        
        # if has a return value
        if node.expr:
            if isinstance(node.expr, uc_ast.BinaryOp):
                _target = self.new_temp()
                # check here, node.expr.type works when its a binary operation
                inst = ('load_'+node.expr.type, self.temps.get('return'), _target)
                self.code.append(inst)
                inst = ('return_'+node.expr.type, _target)
                self.code.append(inst)
            
            elif isinstance(node.expr, uc_ast.Constant):
                _target = self.new_temp()
                inst = ('load_'+node.expr.type, self.temps.get('return'), _target)
                self.code.append(inst)
                inst = ('return_'+node.expr.type, _target)
                self.code.append(inst)
            
            elif isinstance(node.expr, uc_ast.ID):
                _target = self.new_temp()
                inst = ('load_'+node.expr.type, self.temps.get('return'), _target)
                self.code.append(inst)
                inst = ('return_'+node.expr.type, _target)
                self.code.append(inst)
                
        else:
            inst = ('return_void',)
            self.code.append(inst)

        print(self.temps)
        print(self.globals)


    """

    def visit_PrintStatement(self, node):
        # Visit the expression
        self.visit(node.expr)

        # Create the opcode and append to list
        inst = ('print_' + node.expr.type.name, node.expr.gen_location)
        self.code.append(inst)

    
    def visit_LoadLocation(self, node):
        target = self.new_temp()
        inst = ('load_' + node.type.name, node.name, target)
        self.code.append(inst)
        node.gen_location = target


    def visit_UnaryOp(self, node):
        self.visit(node.left)
        target = self.new_temp()
        opcode = unary_ops[node.op] + "_" + node.left.type.name
        inst = (opcode, node.left.gen_location)
        self.code.append(inst)
        node.gen_location = target"""