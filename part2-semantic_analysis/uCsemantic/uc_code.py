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
                node.type.value = node.init.value

        self.visit(node.type)

    def visit_VarDecl(self, node):
        if self.current_scope.scope_name == "global":
            inst = ('global_'+ node.type.names[0], '@'+node.declname.name, node.value)
            self.code.append(inst)
        else:
            # inside a func
            pass
        # allocate on stack memory
        """inst = ('alloc_' + node.type.name, node.id)
        self.code.append(inst)
        # store optional init val
        if node.value:
            self.visit(node.value)
            inst = ('store_' + node.type.name, node.value.gen_location, node.id)
            self.code.append(inst)"""

    def visit_ArrayDecl(self, node):
        if self.current_scope.scope_name == "global":
            _underdim = '_'+ str(node.auxdim[0])
            for _i in range(1,len(node.auxdim)):
                _underdim += '_'+ str(node.auxdim[_i])
            inst = ('global_'+ node.typeaux + _underdim, '@'+ node.name, node.values)
            self.code.append(inst)
            pass
        else:
            # inside a func
            pass







    """def visit_Constant(self, node):
        # Create a new temporary variable name 
        target = self.new_temp()

        # Make the SSA opcode and append to list of generated instructions
        inst = ('literal_' + node.type.name, node.value, target)
        self.code.append(inst)

        # Save the name of the temporary variable where the value was placed 
        node.gen_location = target

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