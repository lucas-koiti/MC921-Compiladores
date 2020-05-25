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