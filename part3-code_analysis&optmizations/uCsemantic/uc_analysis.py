
class AnalyzeOptimaze:
    CFGs = []

    def __init__(self, cfg_list: list):
        self.CFGs = cfg_list
        self.gen = []
        self.kill = []

        # codigo optimal gerado (semelhante ao codegen)
        self.code = [('define', '@checkPrime')]


    """ Reaching Definitions """
    # TODO verificar qual é o escopo de execucao do RD, se ele é aplicado a individualmente a cada
    # CFG ou sua tabela gen e kill engloba todas cfg
    def get_gen_kill(self):
        # dicionario auxiliar que guarda todas as linhas da variaveis utilizadas
        defs = {}
        # itera todas cfgs e obtem o gen[]
        for cfg in self.CFGs:
            # e todas suas instrucoes
            for idx, inst in enumerate(cfg.instructions):
                self.gen.append([])
                self.kill.append([])
                # qualquer store adiciona a variavel em questao no gen[]
                if inst[1][0] == 'store_int':
                    # TODO verificar se no store a varivel que recebe atribuicao é a 2
                    attr_var = inst[1][2]
                    self.gen.append(attr_var)
                    # guarda a variavel e a linha que foi atribuida
                    if attr_var in defs.keys():
                        defs[attr_var].append(idx)
                    else:
                        defs[attr_var] = [idx]
        # TODO arrumar geração do kill
        for var in defs.keys():
            print(f"var: {var} linhas: {defs[var]}")
            for idx, line in enumerate(defs[var]):
                self.kill[line] = [defs[var][:idx:]]
        print(self.kill)
        

    def reachingDefinitions(self):
        """ Função que executa a analise de reaching defintions nas CFGs obtidas.
        """
        pass

    """ Liveness Analysis """

    """ Available Expressions """

    def optmize(self):
        self.get_gen_kill()