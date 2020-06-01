# 
#   CFG & Basic Blocks classes to be used for CodeGen & Analysis
#

import uc_ast
from graphviz import Digraph
from uc_sema import NodeVisitor, ScopedSymbolTable


def format_instruction(t):
    # Auxiliary method to pretty print the instructions 
    op = t[0]
    if len(t) > 1:
        if op == "define":
            return f"\n{op} {t[1]}"
        else:
            _str = "" if op.startswith('global') else "  "
            if op == 'jump':
                _str += f"{op} label {t[1]}"
            elif op == 'cbranch':
                _str += f"{op} {t[1]} label {t[2]} label {t[3]}"
            elif op == 'global_string':
                _str += f"{op} {t[1]} \'{t[2]}\'"
            elif op.startswith('return'):
                _str += f"{op} {t[1]}"
            else:
                for _el in t:
                    _str += f"{_el} "
            return _str
    elif op == 'print_void' or op == 'return_void':
        return f"  {op}"
    else:
        return f"{op}"


class CFG(object):

    def __init__(self, fname):
        self.fname = fname
        self.g = Digraph('g', filename=fname + '.gv', node_attr={'shape': 'record'})

    def visit_BasicBlock(self, block):
        # Get the label as node name
        _name = block.label
        if _name:
            # get the formatted instructions as node label
            _label = "{" + _name + ":\l\t"
            for _inst in block.instructions[1:]:
                _label += format_instruction(_inst) + "\l\t"
            _label += "}"
            self.g.node(_name, label=_label)
            if block.branch:
                self.g.edge(_name, block.branch.label)
        else:
            # Function definition. An empty block that connect to the Entry Block
            self.g.node(self.fname, label=None, _attributes={'shape': 'ellipse'})
            self.g.edge(self.fname, block.next_block.label)

    def visit_ConditionBlock(self, block):
        # Get the label as node name
        _name = block.label
        # get the formatted instructions as node label
        _label = "{" + _name + ":\l\t"
        for _inst in block.instructions[1:]:
            _label += format_instruction(_inst) + "\l\t"
        _label +="|{<f0>T|<f1>F}}"
        self.g.node(_name, label=_label)
        self.g.edge(_name + ":f0", block.taken.label)
        self.g.edge(_name + ":f1", block.fall_through.label)

    def view(self, block):
        while isinstance(block, Block):
            name = "visit_%s" % type(block).__name__
            if hasattr(self, name):
                getattr(self, name)(block)
            block = block.next_block
        # You can use the next stmt to see the dot file
        # print(self.g.source)
        self.g.view()

class Block():

    def __init__(self, label):
        # Label that identifies the block
        self.label = label      
        # Instructions in the block
        self.instructions = []   
        # List of predecessors
        self.predecessors = []
        # Link to the next block   
        self.next_block = None


    def append(self,instr):
        self.instructions.append(instr)


    def __iter__(self):
        return iter(self.instructions)


class BasicBlock(Block):
    '''
    Class for a simple basic block.  Control flow unconditionally
    flows to the next block.
    '''
    def __init__(self, label):
        super(BasicBlock, self).__init__(label)
        # Not necessary the same as next_block in the linked list
        self.branch = None  


class ConditionBlock(Block):
    """
    Class for a block representing an conditional statement.
    There are two branches to handle each possibility.
    """
    def __init__(self, label):
        super(ConditionBlock, self).__init__(label)
        self.taken = None
        self.fall_through = None

 
class BlockVisitor(object):
    '''
    Class for visiting basic blocks.  Define a subclass and define
    methods such as visit_BasicBlock or visit_IfBlock to implement
    custom processing (similar to ASTs).
    '''
    def visit(self, block):
        while isinstance(block,Block):
            name = f"visit_{type(block).__name__}"
            if hasattr(self,name):
                getattr(self,name)(block)
            block = block.next_block

class GenerateCode(NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self, viewcfg):
        super(GenerateCode, self).__init__()
        self.viewcfg = viewcfg
        self.current_block = None

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
                            '%' : "mod",
                            '==': "eq",
                            '!=': "ne",
                            '<' : "lt",
                            '>' : "gt",
                            '<=': "le",
                            '>=': "ge",
                            '%=': "modeq",
                            '&&': "and",
                            '||': "or",
                            '!' : "not"
                        }
        self.assignOp = {
                            '+=': "add",
                            '-=': "sub",
                            '*=': "mul",
                            '/=': "div",
                            '%=': "mod"
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

        if self.viewcfg:
            for _decl in node.gdecls:
                if isinstance(_decl, uc_ast.FuncDef):
                    dot = CFG(_decl.decl.name.name)
                    dot.view(_decl.cfg)

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
                elif isinstance(node.init, uc_ast.ID):
                    node.type.valuetmp = node.init

        elif isinstance(node.type, uc_ast.ArrayDecl):
            if isinstance(node.init, uc_ast.BinaryOp):
                node.type.values = node.init
            if node.type.aux:
                node.type.auxdim = node.type.aux
        

        return self.visit(node.type)


    def visit_VarDecl(self, node):
        _tmp = None
        if self.current_scope.scope_name == "global":
            inst = ('global_'+ node.type.names[0], '@'+node.declname.name, node.value)
            self.code.append(inst)
            self.globals[node.declname.name] = node.value
        else:
            
            # allocate on stack memory
            _tmp = self.new_temp()
            inst = ('alloc_' + node.type.names[0], _tmp)
            self.code.append(inst)
                       
            # store the temporary used in dict
            self.temps[node.declname.name] = _tmp
            
            # store init value when its a func call result
            if isinstance(node.valuetmp, uc_ast.FuncCall):
                _freturn = self.visit(node.valuetmp)
                inst = ('store_'+node.valuetmp.type, _freturn, _tmp)
                self.code.append(inst)
            elif isinstance(node.valuetmp, uc_ast.ID):
                _idvalue = self.visit(node.valuetmp)
                inst = ('store_'+node.valuetmp.type, _idvalue, _tmp)
                self.code.append(inst)
            elif isinstance(node.valuetmp, uc_ast.Constant):
                _gen = self.visit(node.valuetmp)
                inst = ('store_' + node.type.names[0], _gen, _tmp)
                self.code.append(inst)
        return _tmp

    def visit_FuncCall(self, node):   
        if isinstance(node.args, uc_ast.ExprList):
            _paramlist = []
            for _k in node.args.exprs:
                _target = self.new_temp()
                if isinstance(_k, uc_ast.ID):
                    _src = self.temps.get(_k.name)
                    if _src is None:
                        _src = '@'+_k.name                  # if its not in the current scope, its in global
                elif isinstance(_k, uc_ast.Constant):
                    _src = self.visit(_k)
                elif isinstance(_k, uc_ast.BinaryOp):
                    _src = self.visit(_k)
                inst = ('load_'+_k.type, _src, _target)
                self.code.append(inst)
                inst = ('param_'+_k.type, _target)
                _paramlist.append(inst)
            self.code += _paramlist
        elif isinstance(node.args, uc_ast.ID):
            _target = self.new_temp()
            _src = self.temps.get(node.args.name)
            if _src is None:
                _src = '@'+node.args.name
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

        elif isinstance(node.args, uc_ast.BinaryOp):
            _target = self.new_temp()
            _src = self.visit(node.args)
            inst = ('load_'+node.args.type, _src, _target)
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
        if node.type == "bool": # in a rel ops the binary returns bool, but before it's a int compare
            if node.op != "&&" and node.op != "||":
                node.type = node.left.type
        inst = (self.binaryop[node.op]+"_"+node.type, _ltemp, _rtemp, _target)
        self.code.append(inst)

        # return the target used
        return _target

    def visit_ID(self, node):
        # plus 1 because its the stored temporary used in FuncDecl
        _src = self.temps.get(node.name+"1") # stored value in another temporary
        if not _src:
            _src = self.temps.get(node.name) # original temporary
        _target = self.new_temp()
        
        # in case the variable isn't in the scope, he consider it is in global
        if _src:  
            inst = ('load_'+node.type, _src, _target)
        else:
            inst = ('load_'+node.type, '@'+node.name, _target)
        
        self.code.append(inst)

        return _target
         
         
    def visit_Constant(self, node):
        if node.type == "string":
            _gen = '@.str.'+str(self.str_counter)
            inst = ('global_string', _gen, node.value[1:-1])
            self.str_counter += 1
            # find where to declare in the code flow
            _i = 0
            while 'global' in self.code[_i][0]:
                _i += 1
                # insert in the right spot
            self.code.insert(_i, inst)
        else:
            # literal value
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
        return _tmp

    def visit_ArrayRef(self, node):
        if isinstance(node.name, uc_ast.ID):
            _indextmp = self.visit(node.subscript)
            _arrayref = self.temps.get(node.nameaux)
            if _arrayref is None:
                _arrayref = '@'+(node.nameaux)
            _target = self.new_temp()
            _target1 = self.new_temp()
            
            # elem and load to a new temporary
            inst = ('elem_'+node.type, _arrayref, _indextmp, _target)
            self.code.append(inst)
            inst = ('load_'+node.type+'_*', _target, _target1)
            self.code.append(inst)

            return _target1
        else:
            _arrayref = self.temps.get(node.nameaux)
            if _arrayref is None:
                _arrayref = '@'+(node.nameaux)
            # only works for 2-D arrays
            _factor = len(node.index)
            _target = self.new_temp()
            inst = ('literal_int', _factor, _target)
            self.code.append(inst)
            _1d = self.visit(node.index[1])
            _target1 = self.new_temp()
            inst = ('mul_int', _target, _1d, _target1)
            self.code.append(inst)
            _2d = self.visit(node.index[0])
            _target = self.new_temp()
            inst = ('add_int', _target1, _2d, _target)
            self.code.append(inst)
            _target1 = self.new_temp()
            inst = ('elem_'+node.type, _arrayref, _target, _target1)
            self.code.append(inst)
            _target = self.new_temp()
            inst = ('load_'+node.type+'_*', _target1, _target)
            self.code.append(inst)

            return _target

    def visit_Print(self, node):
        if node.expr:
            if isinstance(node.expr, uc_ast.ExprList):
                for _i in node.expr.exprs:
                    _printTmp = self.visit(_i)
                    _type = _i.type
                    inst = ('print_'+_type, _printTmp)
                    self.code.append(inst) 
            else:
                _printTmp = self.visit(node.expr)
                _type = node.expr.type
                inst = ('print_'+_type, _printTmp)
                self.code.append(inst)
        else:
            # empty print (creates a \n string and print it)
            _str = '@.str.'+str(self.str_counter)
            inst = ('global_char', _str, '\n')
            self.str_counter += 1
            # find where to declare in the code flow
            _i = 0
            while 'global' in self.code[_i][0]:
                _i += 1
                # insert in the right spot
            self.code.insert(_i, inst)
            inst = ('print_char', _str)
            self.code.append(inst)

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
            _aloc = []
            _store = []
            if node.args:
                # create pass params temporaries
                for _i in range(len(node.args.params)):
                    self.temps[node.args.params[_i].name.name] = self.new_temp()

                # create a temporary to store return value
                self.temps['return'] = self.new_temp()
                
                # alloc and store temporaries to receive the params
                for _k in range(len(node.args.params)):
                    _tmp = self.new_temp()
                    _type = node.args.params[_k].type.type.names[0]
                    inst = ('alloc_'+_type, _tmp)
                    _aloc.append(inst)
                    _src = self.temps[node.args.params[_k].name.name]
                    inst = ('store_'+_type, _src, _tmp)
                    _store.append(inst)
                    self.temps[node.args.params[_k].name.name] = _tmp
                
                self.code += _aloc
                self.code += _store
    
                # create a jump label to return
                self.temps['label1'] = self.new_temp()
            else:
                # in @main we just need reserve temporaries to return and jump return
                self.temps['return'] = self.new_temp()
                self.temps['label1'] = self.new_temp()

    def visit_Assignment(self, node):
        if isinstance(node.lvalue, uc_ast.ArrayRef):
            _target = self._assignment2array(node)
        else:
            _gen = self.visit(node.rvalue)                          # gets the temporary used (eg. 'a': %2)
            _target = self.temps.get(node.lvalue.name)              # access the global dict with declared variables
            if _target is None:
                _target = '@'+(node.lvalue.name)
            if node.op == "=":
                inst = ('store_'+ node.lvalue.type, _gen, _target)  
                self.code.append(inst)
            else:
                _tgt = self.new_temp()
                inst = ('load_'+ node.lvalue.type, _target, _tgt)
                self.code.append(inst)
                _tgt1 = self.new_temp()
                inst = (self.assignOp[node.op]+'_'+ node.lvalue.type, _gen, _tgt, _tgt1)
                self.code.append(inst)
                inst = ('store_'+ node.lvalue.type, _tgt1, _target)
                self.code.append(inst)
            
        return _target
    
    def _assignment2array(self, node):
        _gen = self.visit(node.rvalue)

        # get array temporary, the left side
        if isinstance(node.lvalue.name, uc_ast.ID):
            _arraytmp = self.temps.get(node.lvalue.name.name)
        else:
            _arraytmp = self.visit(node.lvalue)

        # find the subscript and store as demand
        _idx = self.visit(node.lvalue.subscript)
        _target = self.new_temp()
        inst = ('elem_'+node.lvalue.type, _arraytmp, _idx, _target)
        self.code.append(inst)
        inst = ('store_'+node.lvalue.type+'_*', _gen, _target)
        self.code.append(inst)
        return _target
        

    def visit_UnaryOp(self, node):
        _elem = self.visit(node.expr)
        _one = self.new_temp()
        _target = self.new_temp()
        
        if node.op == "++" or node.op == "p++":
            inst = ('literal_'+node.expr.type, 1, _one)
            self.code.append(inst)
            inst = ('add_'+node.expr.type, _elem, _one, _target)
            self.code.append(inst)
            if node.op == "++":
                _aux = _target          #ex: x = x++ -> z = x
            else:
                _aux = _elem            #ex: x = x++ -> z = x
        elif node.op == "--" or node.op == "p--":
            inst = ('literal_'+node.expr.type, 1, _one)
            self.code.append(inst)
            inst = ('sub_'+node.expr.type, _elem, _one, _target)
            self.code.append(inst)
            if node.op == "--":
                _aux = _target
            else:
                _aux = _elem    
        elif node.op == "-":
            inst = ('literal_'+node.expr.type, -1, _one)
            self.code.append(inst)
            inst = ('mul_'+node.expr.type, _elem, _one, _target)
            self.code.append(inst)
            _aux = _target
        elif node.op == "+":
            inst = ('literal_'+node.expr.type, 1, _one)
            self.code.append(inst)
            inst = ('mul_'+node.expr.type, _elem, _one, _target)
            self.code.append(inst)
            _aux = _target
        
        # here we find the temporary used by the variable
        _src = self.temps.get(node.expr.name) 
        # in case the variable isn't in the scope, he consider it is in global
        if _src:  
            inst = ('store_'+node.expr.type, _target, _src)
        else:
            inst = ('store_'+node.expr.type, _target ,'@'+node.expr.name)
        
        self.code.append(inst)

        return _aux 


    def visit_Compound(self, node):
        # check every item in the block
        if node.block_items:
            for _i in node.block_items:
                self.visit(_i)
        else:
            inst = ('1',)
            self.code.append(inst)
            inst = ('return_void',)
            self.code.append(inst)

    def visit_Assert(self, node):
        _test = self.visit(node.expr)
        _true = self.new_temp()
        _false0 = self.new_temp()
        _true1 = self.new_temp() # label to jump

        # code flow
        inst = ('cbranch', _test, _true, _false0)
        self.code.append(inst)
        inst = (_true[1:],) # label true
        self.code.append(inst)
        inst = ('jump', _true1) # temporary with the label true
        self.code.append(inst)
        inst = (_false0[1:],)
        self.code.append(inst)
        inst = ('print_string', '@.str.'+str(self.str_counter))
        self.code.append(inst)
        inst = ('jump', self.temps.get('label1'))
        self.code.append(inst)
        inst = (_true1[1:],)
        self.code.append(inst)

        # assertion fail str
        inst = ('global_string', '@.str.'+str(self.str_counter), 'assertion_fail on '+str(node.coord.line)+':'+str(node.coord.column))
        self.str_counter += 1
        # find where to declare in the code flow
        _i = 0
        while 'global' in self.code[_i][0]:
            _i += 1
        # insert assertion fail in the top of code flow
        self.code.insert(_i, inst)

    def visit_Cast(self, node):
        _src = self.visit(node.expr)   
        _target = self.new_temp()
        if node.to_type.names[0] == "float":
            inst = ('sitofp', _src, _target)
            self.code.append(inst)
        else:
            inst = ('fptosi', _src, _target)
            self.code.append(inst)
        
        return _target
    
    def visit_For(self, node):
        # start the 3 labels
        _labelinit = self.new_temp()
        _labelcont = self.new_temp()
        _labelfinish = self.new_temp()

        # first get the initial value
        if isinstance(node.init, uc_ast.DeclList):
            _cond = self.visit(node.init.decls[0])
        elif isinstance(node.init, uc_ast.Assignment):
            _cond = self.visit(node.init)
        
        # label to the init jump
        inst = (_labelinit[1:],)
        self.code.append(inst)
        
        # make the conditional op
        _condop = self.visit(node.cond)
        inst = ('cbranch', _condop, _labelcont, _labelfinish)
        self.code.append(inst)
        inst = (_labelcont[1:],)
        self.code.append(inst)

        # execute the body
        self.visit(node.stmt)

        # update the conditional
        _condatt = self.visit(node.next)
        inst = ('jump', _labelinit)
        self.code.append(inst)

        # label to finish
        inst = (_labelfinish[1:],)
        self.code.append(inst)


    def visit_While(self, node):
         # start the 3 jump labels
        _labelinit = self.new_temp()
        _labelcont = self.new_temp()
        _labelfinish = self.new_temp()

        # label to the init jump
        inst = (_labelinit[1:],)
        self.code.append(inst)

        # conditional op
        _cond = self.visit(node.cond)
        inst = ('cbranch', _cond, _labelcont, _labelfinish)
        self.code.append(inst)
        inst = (_labelcont[1:],)
        self.code.append(inst)

        # execute the body ( where the conditional is att)
        self.visit(node.stmt)

        # if gets here, jump to the init
        inst = ('jump', _labelinit)
        self.code.append(inst)

        # label to finish
        inst = (_labelfinish[1:],)
        self.code.append(inst)

    def visit_Read(self, node):
        if isinstance(node.expr, uc_ast.ExprList):
            for _i in node.expr:
                if isinstance(_i, uc_ast.ID):
                    self._read_ID(_i)
                elif isinstance(_i, uc_ast.ArrayRef):
                    self._read_ArrayRef(_i)
        elif isinstance(node.expr, uc_ast.ID):
            self._read_ID(node.expr)
        elif isinstance(node.expr, uc_ast.ArrayRef):
            self._read_ArrayRef(node.expr)

    def _read_ID(self, node):
        # read and store in a variable
        _src = self.new_temp()
        _target = self.temps.get(node.name)
        inst = ('read_'+node.type, _src)
        self.code.append(inst)
        inst = ('store_'+node.type, _src, _target)
        self.code.append(inst)

    def _read_ArrayRef(self, node):
        # read and store in an array reference
        _indextmp = self.visit(node.subscript)
        _arrayref = self.temps.get(node.nameaux)
        _target = self.new_temp()
            
        # get the elem address
        inst = ('elem_'+node.type, _arrayref, _indextmp, _target)
        self.code.append(inst)

        # read the value
        _src = self.new_temp()
        inst = ('read_'+node.type, _src)
        self.code.append(inst)

        #store in the right address
        inst = ('store_'+node.type+'_*', _src, _target)
        self.code.append(inst)

    def visit_If(self, node):
        # true and false labels
        _truelabel = self.new_temp()
        _falselabel = self.new_temp()
        
        # check condition
        _cond = self.visit(node.cond)
        inst = ('cbranch', _cond, _truelabel, _falselabel)
        self.code.append(inst)
        
        # label if true
        inst = (_truelabel[1:],)
        self.code.append(inst)
        # true stmt
        self.visit(node.iftrue)

        # label if false
        inst = (_falselabel[1:],)
        self.code.append(inst)
        # false stmt
        if node.iffalse:
            self.visit(node.iffalse)

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
                _src = self.visit(node.expr)
                #_src = self.temps.get(node.expr.name)
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