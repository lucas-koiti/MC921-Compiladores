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

        # Identifies if is a basic (0) or conditional (1: cbranch | 2: jump) block
        self.kind = None

        # Basic Block
        self.branch = None  

        # Conditional Block
        self.truelabel = None
        self.falselabel = None


    def append(self,instr):
        self.instructions.append(instr)


    def __iter__(self):
        return iter(self.instructions)


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
        i = 1
        globalblock = Block('Globals')

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
        block_dict = {}
        i_func = 0
        # laco para criar uma CFG pra cada funcao contida na lista de instrucoes
        for func in funcs_code:
            start_block = Block(func[0][0])                     # primeira instrucao eh sempre lider
            current_block = start_block
            current_block.append(func[0])
            for inst in func[1:]:                               # percorre cada instrucao da funcao
                if inst in leaders[i_func]:                     # se ela fizer parte de uma instrucao lider, inicia um novo bloco
                    key = current_block.instructions[0][1][0]   # a chave para identificar o bloco é a label do temp usado na tupla e.g. ('1',)
                    block_dict[key] = current_block             # salva o bloco corrente em um dict
                    new_block = Block(inst[0])                  # cria um novo bloco
                    current_block.next_block = new_block        # liga os blocos sequencialmente
                    current_block = new_block
                
                current_block.append(inst)                      # continua a adicionar instrucoes ao bloco corrente       
            i_func += 1                                         # contador para acessar a lista de instrucoes lider da funcao correta
            key = current_block.instructions[0][1][0]
            block_dict[key] = current_block 
                    
            # conecta os blocos da CFG, criando uma lista ligada com os blocos em sequencia do codigo e com pointers para seus fluxos
            for block in block_dict.values():
                # checa se a ultima instrucao do bloco eh um jump, cbranch ou qlq coisa
                inst = block.instructions[-1][1]
                if inst[0] == 'cbranch':
                    block.kind = 1
                    key = inst[2][1:]
                    block.truelabel = block_dict[key]
                    key = inst[3][1:]
                    block.falselabel = block_dict[key]
                elif inst[0] == 'jump':
                    block.kind = 2
                    key = inst[1][1:]
                    block.branch = block_dict[key]
                else:
                    if 'return' in block.instructions[-1][1][0]:
                        block.kind = -1
                    else:
                        block.kind = 0
                        block.branch = block.next_block
                                       
            # salva o start_block como cabeça da lista de blocos da funcao analisada
            self.progCFG.append(start_block)

            # limpa a lista de blocos, pois todos ja estao ligados como "lista" (C kind of list)
            block_dict.clear()
        
        # itera sobre todos os blocos imprimindo-os
        for block_pointer in self.progCFG:
            print()
            print("---NEW CFG---")
            while block_pointer:
                print(f"Bloco {block_pointer.label}")
                # imprime todas instrucoes do bloco
                for inst in block_pointer.instructions:
                    print(f"\t\t{inst}")
                # imprime o fluxo do bloco
                if block_pointer.kind == 0:
                    print("\t NEXT BLOCK : " + "bloco " + str(block_pointer.branch.label))
                elif block_pointer.kind == 1:
                    print("\t TRUE BLOCK : " + "bloco: " + str(block_pointer.truelabel.label))
                    print("\t FALSE BLOCK : " + "bloco " + str(block_pointer.falselabel.label))
                elif block_pointer.kind == 2:
                    print("\t NEXT BLOCK : " + "bloco " + str(block_pointer.branch.label))
                block_pointer = block_pointer.next_block
                


    





    