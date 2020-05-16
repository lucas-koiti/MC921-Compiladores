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

        # ops dictionary
        self.binaryop = {
                            '+' : "add",
                            '-' : "sub",
                            '*' : "mul",
                            '/' : "div",
                            '%' : "mod" 
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

        self.visit(node.type)


    def visit_VarDecl(self, node):
        if self.current_scope.scope_name == "global":
            inst = ('global_'+ node.type.names[0], '@'+node.declname.name, node.value)
            self.code.append(inst)
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


    def visit_Constant(self, node):
        _gen = self.new_temp()
        inst = ('literal_'+ node.type, node.value, _gen)
        self.code.append(inst)
        return _gen


    def visit_ArrayDecl(self, node):
        if self.current_scope.scope_name == "global":
            _underdim = '_'+ str(node.auxdim[0])
            for _i in range(1,len(node.auxdim)):
                _underdim += '_'+ str(node.auxdim[_i])
            if node.values is None:
                inst = ('global_'+ node.typeaux + _underdim, '@'+ node.name)
            else:
                inst = ('global_'+ node.typeaux + _underdim, '@'+ node.name, node.values)
            self.code.append(inst)
            pass
        else:
            # inside a func
            pass


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
        inst = ('define', node.type.declname.name)
        self.code.append(inst)

        if node.type.declname.name == "main":
            self.temps['r0'] = self.new_temp()
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
        inst = ('jump', self.temps['label1'])
        self.code.append(inst)
        inst = (self.temps['label1'][1:],)
        self.code.append(inst)

        if node.expr: # if has a return value
            pass
        else:
            inst = ('return_void',)
            self.code.append(inst)

        print(self.temps)

    """

    def visit_BinaryOp(self, node):
        # Visit the left and right expressions
        self.visit(node.left)
        self.visit(node.right)

        # Make a new temporary for storing the result
        target = self.new_temp()

        # Create the opcode and append to list
        opcode = binary_ops[node.op] + "_"+node.left.type.name
        inst = (opcode, node.left.gen_location, node.right.gen_location, target)
        self.code.append(inst)

        # Store location of the result on the node
        node.gen_location = target

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

    def visit_AssignmentStatement(self, node):
        self.visit(node.value)
        inst = ('store_' + node.value.type.name, node.value.gen_location, node.location)
        self.code.append(inst)

    def visit_UnaryOp(self, node):
        self.visit(node.left)
        target = self.new_temp()
        opcode = unary_ops[node.op] + "_" + node.left.type.name
        inst = (opcode, node.left.gen_location)
        self.code.append(inst)
        node.gen_location = target"""