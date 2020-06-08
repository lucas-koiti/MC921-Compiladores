
class AnalyzeOptimaze:
    CFGs = []

    def __init__(self, cfg_list: list):
        self.CFGs = cfg_list
        self.gen = []
        self.kill = []


    """ Reaching Definitions """
    # TODO verificar qual é o escopo de execucao do RD, se ele é aplicado a individualmente a cada
    # CFG ou sua tabela gen e kill engloba todas cfg
    def get_gen_kill(self):
        # dicionario auxiliar que guarda todas as linhas da variaveis utilizadas
        defs = {}
        # itera todas cfgs e obtem o gen[]
        for cfg in self.CFGs:
            # e todas suas instrucoes
            for idx, inst in enumerate(cfg.instructions, 1):
                self.gen.append([])
                self.kill.append([])
                # qualquer store adiciona a variavel em questao no gen[]
                if inst[1][0].find('store_') != -1:
                    # TODO verificar se no store a varivel que recebe atribuicao é a 2
                    attr_var = inst[1][2]
                    # adiciona na ultima lista vazia criada
                    self.gen[-1] = attr_var
                    print(f"apendou na {idx}")
                    # guarda a variavel e a linha que foi atribuida
                    if attr_var in defs.keys():
                        defs[attr_var].append(idx)
                    else:
                        defs[attr_var] = [idx]
        print("defs:")
        for var in defs.keys():
            print(f"var: {var} linhas: {defs[var]}")
            if len(defs[var]) == 1:
                # lista é vazia
                pass
            if len(defs[var]) == 2:
                self.kill[defs[var][0]-1] = defs[var][1]
                self.kill[defs[var][1]-1] = defs[var][0]
            else:
                for idx, line in enumerate(defs[var]):
                    # ineficiente mas é o que tem pra hoje
                    self.kill[line-1] = defs[var][:idx] + defs[var][idx+1:]
        print("linha\tgen\tkill")
        for idx, (gen, kill) in enumerate(zip(self.gen, self.kill), 1):
            print(f"   {idx}\t{gen}\t{kill}")


            
        
    def reachingDefinitions(self):
        """ Função que executa a analise de reaching defintions nas CFGs obtidas.
        """
        pass

    """ Liveness Analysis """

    """ Available Expressions """