class AnalyzeOptimaze:
    CFGs = []

    def __init__(self, cfg_list: list):
        self.CFGs = cfg_list
        # self.gen = []
        # self.kill = []
        self.cfg_gen_kill = {}
        self.blocks_amt = {}
        # lista de dicionarios para detectar conversão de valores no reching definitions
        self.changed = []

    """ Reaching Definitions """

    def get_gen_kill(self):
        # itera todas cfgs e obtem o gen[]
        for cfg_count, block in enumerate(self.CFGs, 0):
            # defs é um dicionario VARIAVEL : LISTA DE LINHAS onde a variavel recebe atribuição
            defs = {}
            # gen é um array com o tamanho da quantidade de linhas do bloco, onde há atribuição ele salva a variavel que foi atualiuzada
            gens = {}
            # kill é todas as defs de alguma variavel menos a que foi atribuida na linha sendo itarada
            kills = {}
            self.changed.append({})
            self.blocks_amt[cfg_count] = 0
            print(f"\n---------CFG {cfg_count}----------")
            while block:
                self.blocks_amt[cfg_count] += 1
                print(f"Bloco {block.label}")
                print("Predecessors: ", end='')
                if block.predecessors:
                    for pred in block.predecessors:
                        print(pred.label, end=' ')
                    print()
                # bloco de globais é referido pelo indice 0
                block_id = block.label if isinstance(block.label, int) else 0
                # inicializa dicioanrio auxiliar para reaching definitins
                if block_id not in self.changed[cfg_count].keys():
                    self.changed[cfg_count][block_id] = False
                # dicionario para captacao dos gens
                gen_block = {}
                # e todas suas instrucoes
                for inst in block.instructions:
                    print(f"\t{inst}")
                    # qualquer store adiciona a variavel em questao no gen[]
                    if inst[1][0].find('store_') != -1:
                        attr_var = inst[1][2]
                        # adiciona na ultima lista vazia criada
                        gen_block[attr_var] = inst[0]
                        # guarda a variavel e a linha que foi atribuida
                        if attr_var in defs.keys():
                            defs[attr_var].append(inst[0])
                        else:
                            defs[attr_var] = [inst[0]]
                    # sava o gen do bloco
                    gens[block_id] = gen_block
                # obtem proximo bloco
                block = block.next_block
            print(f"CFG COM {self.blocks_amt[cfg_count]} BLOCOS")

            # Calcula Kill
            for block_id in gens.keys():
                # variavel que guarda os kills do bloco em questao
                kill_block = {}
                for var in gens[block_id].keys():
                    # converte a lista de atribuicoes da variavel em conjunto
                    var_set = set(defs[var])
                    # ontem a linha da ultima aatribuicao feita da data variavel
                    last_attr_line = [gens[block_id][var]]
                    # faz subtracao de conjunto para obter o kill
                    line_kill = var_set.difference(last_attr_line)
                    # converte em lista e salva o kill da variavel
                    kill_block[var] = list(line_kill)
                # salva o kill do bloco
                kills[block_id] = kill_block

            print("###### defs ######")
            for var in defs.keys():
                print(f"var: {var} linhas: {defs[var]}")
            print("###################")
            print("======== Gen Kill ========")
            for block in kills.keys():
                print(f"Bloco {block} ")
                print(f"\tgen : {gens[block]}")
                print(f"\tkill : {kills[block]}")
            # guarda gen e kill relativo aos cfgs
            self.cfg_gen_kill[cfg_count] = (gens, kills)
        self.reachingDefinitions()


    def reachingDefinitions(self):
        """ Função que executa a analise de reaching defintions nas CFGs obtidas.
        """
        RD_cfg = {}
        for cfg in self.changed:
            print(cfg)
        for cfg_id, block in enumerate(self.CFGs):
            _in = {}
            _out = {}
            changed = {}
            while block and all(changed.values()):
                block_id = block.label if isinstance(block.label, int) else 0
                # 0 gen - 1 kill
                if self.cfg_gen_kill[cfg_id][0] and block_id in _in.keys():
                    block_gen = set(self.cfg_gen_kill[cfg_id][0][block_id])
                    block_in = set(_in[block_id])
                    block_kill = set(self.cfg_gen_kill[cfg_id][1][block_id])
                    sub_set = block_in.difference(block_kill)
                    _out[block_id] = block_gen.union(sub_set)

                if block.predecessors:
                    for pred_block in block.predecessors:
                        # _in[block_id] = 
                        pred_id = pred_block.label if isinstance(pred_block.label, int) else 0
                        if pred_id in _out.keys():
                            if len(_in[block_id]) == 0:
                                _in[block_id] = _out[pred_id]
                            else:
                                pred_out = set(_out[pred_id])
                                block_in = set(_in[block_id])
                                _in[block_id] = list(block_in.union(pred_out))
                else:
                    _in[block_id] = None

                block = block.next_block
            RD_cfg[cfg_id] = (_in, _out)

        print(f"in: {RD_cfg[0]}")
        print(f"out: {RD_cfg[1]}")
        pass

    """ Liveness Analysis """

    """ Available Expressions """
