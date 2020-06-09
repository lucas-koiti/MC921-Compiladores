
class AnalyzeOptimaze:
    CFGs = []

    def __init__(self, cfg_list: list):
        self.CFGs = cfg_list
        # self.gen = []
        # self.kill = []


    """ Reaching Definitions """
    def get_gen_kill(self):
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
                gen = []
                kill = []
                defs = {}
                block = block.next_block


            
        
    def reachingDefinitions(self):
        """ Função que executa a analise de reaching defintions nas CFGs obtidas.
        """
        # out = {}
        # print("\n\nFUNCAO PORRA")
        # for cfg in self.CFGs:
        #     while cfg:
        #         print(cfg.label)
        #         print(f"\t{cfg.instructions}")
        #         cfg = cfg.next_block

    """ Liveness Analysis """

    """ Available Expressions """