# nenhum import por enquanto, dado que pegamos o .ir pela uc.py

    #################################
    #      CFG Block Structure      #   
    #################################
class Block(object):

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

    #################################
    #      CFG Block Generator      #   
    #################################
class BlockGenerator(object):

    def __init__(self, code_3):
        # codigo em 3 enderecos 
        self.code_3 = code_3
        # ponteiros para os CFG's de cada funcao/global contida no codigo
        self.progCFG = []


    def get_globals(self):
        """ 
            .Pega todas as declaracoes globais e guarda em um bloco, enumerando as linhas a partir de 0
            .Retira essas declaracoes da lista de instrucoes 
            .Armazena em uma variavel da classe que contem todos os ponteiros para os blocos iniciais de uma CFG
        """
        i = 0
        globalblock = BasicBlock('Globals')

        while self.code_3[0][0] != 'define':
            instr = [i, self.code_3[0]]
            globalblock.append(instr)
            i += 1
            del self.code_3[0]

        self.progCFG.append(globalblock)


    def brokein2funcs(self):
        """
            .Pega a lista de instrucoes e a divide em funcoes
            .Enumera cada linha dentro do escopo da funcao
            .Armazena a lista de instrucoes em uma lista
            .Retorna a lista na qual cada item eh uma lista contendo as instrucoes de uma funcao
            .Retorna a lista na qual cada item eh uma lista contendo as instrucoes lider de cada funcao
        """
        _func = []
        _instraux = []
        _leaders = []
        _leadaux = []
        line = 1
        for inst in self.code_3:
            instr = [line, inst]
            line += 1
            _instraux.append(instr)

            if inst[0].isnumeric():
                _leadaux.append(instr)

            if 'return' in inst[0]:
                line = 1
                _aux1 = _instraux.copy()
                _func.append(_aux1)
                _instraux.clear()
                _aux2 = _leadaux.copy()
                _leaders.append(_aux2)
                _leadaux.clear()

        return _func, _leaders
                
    def get_blocks(self):
        """
            .Pega uma sequencia de instrucoes de uma funcao e separa em blocos no modelo CFG
            .Armazena o ponteiro do primeiro bloco de cada CFG em self.progCFG
            .Por padrao progCFG[0] eh o bloco de instrucoes globais, pode ser None
        """

        # primeiro, separa as declaracoes globais
        self.get_globals()

        # segundo, separa as funcoes 
        funcs_code, leaders = self.brokein2funcs()
        
        # terceiro, a partir do conjunto de instrucoes lider, determina os blocos existentes na funcao e os conecta gerando um CFG
        


        # quarto, conecta os blocos gerando um CFG

        block = BasicBlock('entry')
        first_block = block
        for code in self.code_3:
            if code[0] == 'jump':
                # adiciona instrucao atual
                block.append(code)
                print(f"adicinou {code}")
                # cria novo bloco
                new_block = BasicBlock(code[1])
                # salva 'ponteiro'
                block.next_block = new_block
                # salva lista de nós predecessores
                for pred_block in block.predecessors:
                    new_block.predecessors.append(pred_block)
                new_block.predecessors.append(block)
                # muda o bloco sendo iterado
                block = new_block
            if code[0] == 'cbranch':
                # adiciona instrucao atual
                block.append(code)
                # cria novo bloco
                new_block = BasicBlock(code[2])
                # salva 'ponteiro'
                block.next_block = new_block
                # salva lista de nós predecessores
                for pred_block in block.predecessors:
                    new_block.predecessors.append(pred_block)
                new_block.predecessors.append(block)
                # muda o bloco sendo iterado
                block = new_block
            else:
                block.append(code)
                print(f"Adicionou {format_instruction(code)} no bloco {block.label}")
        print(f"primeiro bloco {first_block.label}")

        # itera sobre todos os blocos imprimindo-os
        block_pointer = first_block
        while block_pointer.next_block:
            print(f"Bloco {block_pointer.label}")
            # imprime todas instrucoes do bloco
            for inst in block_pointer.instructions:
                print(f"\t{inst}")
            block_pointer = block_pointer.next_block
            # print(format_instruction(code))





    