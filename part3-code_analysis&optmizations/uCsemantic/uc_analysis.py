from uc_block import BlockGenerator

class AnalyzeOptimaze(object):
    CFGs = []

    def __init__(self, cfg_list):
        # CFG divididas por funcoes
        self.CFGs = cfg_list

        # codigo optimal gerado (semelhante ao codegen)
        self.code = []


    def optmize(self): # classe de teste por enquanto, no futuro aplica as otimizacoes e gera codigo
        """ chama suas funcoes aqui, semelhante ao que voce fazia no uc.py """

        self.reachingdef_anal() #RUDO

        #aux = self.liveness_anal()
        #print(aux)

    
    ############################
    #   Reaching Definitions   #  
    ############################

    def reachingdef_anal(self):
        # defs é um dicionario variavel : lista de linhas onde a variavel recebe atribuição
        defs = {}
        # gen é um array com o tamanho da quantidade de linhas do bloco, onde há atribuição ele salva a variavel que foi atualiuzada
        gen = []
        # kill é todas as defs de alguma variavel menos a que foi atribuida na linha sendo itarada
        kill = []
        # itera todas cfgs e obtem o gen[]
        for idx, block in enumerate(self.CFGs):
            # print(f"gen e kill para cfg {idx}")
            while block:
                print(f"--------------------------\n\nBloco {block.label}")
                # e todas suas instrucoes
                for idx, inst in enumerate(block.instructions):
                    print(f"\t{inst}")
                    # cria lista vazia para linha sendo iterada
                    gen.append([])
                    kill.append([])
                    # qualquer store adiciona a variavel em questao no gen[]
                    if inst[1][0].find('store_') != -1:
                        # TODO verificar se no store a varivel que recebe atribuicao é a 2
                        attr_var = inst[1][2]
                        # adiciona na ultima lista vazia criada
                        gen[-1] = attr_var
                        # guarda a variavel e a linha que foi atribuida
                        if attr_var in defs.keys():
                            defs[attr_var].append(idx)
                        else:
                            defs[attr_var] = [idx]
                print("defs:")
                # eu quebrei em opcoes pois não tinha uma forma muito eficiente de fazer a
                # remoção de um elemento da lista sem modificar
                for var in defs.keys():
                    print(f"var: {var} linhas: {defs[var]}")
                    if len(defs[var]) == 1:
                        # se uma variavel é definida apenas uma vez seu kill é vazio
                        pass
                    if len(defs[var]) == 2:
                        # kill é a unica outra atribuicao feita
                        kill[defs[var][0]] = defs[var][1]
                        kill[defs[var][1]] = defs[var][0]
                    else:
                        for idx, line in enumerate(defs[var]):
                            # ineficiente mas é o que tem pra hoje
                            # kill é todas as atribuicoes menos a variavel em questao
                            kill[line-1] = defs[var][:idx] + defs[var][idx+1:]
                print("\n------Tabela Gen Kill ------\nlinha\tgen\tkill")
                for idx, (gen, kill) in enumerate(zip(gen, kill)):
                    print(f"   {idx}\t{gen}\t{kill}")
                
                # TODO reaching deve ser implementado aqui 
                
                gen = []
                kill = []
                defs = {}
                block = block.next_block


    #########################
    #   Liveness Analysis   #  
    #########################

    def liveness_anal(self):
        """ .funcao que realiza o liveness analysis
            .retorna uma lista que cada item é um dict contendo o bloco como chave e uma lista com os in's e out's 
        """

        # lista em que cada item é um dict da forma 'block_label': [[gen],[kill]]
        # portanto, cada item representa uma CFG
        cfgs_genkill = []
        block_gen = []
        block_kill = []
        labelGK = {}

        #find gen kill      
        for cfg in self.CFGs:                                   # percorre cada cfg (cada funcao) do programa
            if cfg.label == 'Globals':
                pass
            else:
                # cada cfg é um "ponteiro" do primeiro bloco dela
                block = cfg
                
                while block:                                    # percorre cada bloco da cfg         
                    labelGK[block.label] = []
                   
                    for instr in block.instructions:            # percorre cada instrucao da cfg
                        kill = self._getKill_live(instr)
                        if kill and (kill not in block_kill):
                            block_kill.append(kill)
                        gen = self._getGen_live(instr)
                        if gen and (gen not in block_gen) and (gen not in block_kill):
                            block_gen.append(gen)

                    auxgen = block_gen.copy()
                    auxkill = block_kill.copy()
                    lista = [auxgen, auxkill]
                    auxlist = lista.copy()
                    labelGK[block.label] = auxlist
                    lista.clear()
                    block_gen.clear()
                    block_kill.clear()

                    block = block.next_block
            
            auxdict = labelGK.copy()
            cfgs_genkill.append(auxdict)
            labelGK.clear()

        return cfgs_genkill
        
    def _getGen_live(self, instr):
        """ .recebe uma instrucao
            .retorna o GEN dela
        """
        gen = None

        if 'load' in instr[1][0]:
            gen = instr[1][1]            
        elif 'param' in instr[1][0]:
            pass
        elif 'print' in instr[1][0]:
            pass
        elif 'call' in instr[1][0]:
            pass
        
        return gen

    def _getKill_live(self, instr):
        """ .recebe uma instrucao
            .retorna o Kill dela
        """
        kill = None

        if 'store' in instr[1][0]:
            kill = instr[1][2]
        elif 'read' in instr[1][0]:
            pass

        return kill
        

        
    

    