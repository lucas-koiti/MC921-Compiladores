import graphviz as gv

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


def format_instruction(t):
    """
    Auxiliary method to pretty print the instructions 
    """
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
    """ 
    Classe que gera uma imagem do CFG
    """
    def __init__(self, fname):
        self.fname = fname
        self.g = gv.Digraph('g', filename=fname + '.gv', node_attr={'shape': 'record'})


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

#        
# At the end of visit_Program method in the Code Generator Class you call CFG view method
# #

#     def visit_Program(self):
#         # ...
#         if self.viewcfg:  # evaluate to True if -cfg flag is present in command line
#             for _decl in node.gdecls:
#                 if isinstance(_decl, FuncDef):
#                     dot = CFG(_decl.decl.name.name)
#                     dot.view(_decl.cfg)  # _decl.cfg contains the CFG for the function