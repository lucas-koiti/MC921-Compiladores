
class AnalyzeOptimaze:
    CFGs = []

    def __init__(self, cfg_list: list):
        self.CFGs = cfg_list
        # self.gen = []
        # self.kill = []


    """ Reaching Definitions """
    def get_gen_kill(self):
        # defs é um dicionario VARIAVEL : LISTA DE LINHAS onde a variavel recebe atribuição
        defs = {}
        # gen é um array com o tamanho da quantidade de linhas do bloco, onde há atribuição ele salva a variavel que foi atualiuzada
        gens = {}
        # kill é todas as defs de alguma variavel menos a que foi atribuida na linha sendo itarada
        kills = {}

        _in = []

        _out = []
        # itera todas cfgs e obtem o gen[]
        for block in self.CFGs:
            # print(f"gen e kill para cfg {cfg_idx}")
            # cfgs_in_out['in'] =
            # _out.append({})
            # _in.append({})
            while block:
                print(f"--------------------------\n\nBloco {block.label}")
                # bloco de globais é referido pelo indice 0
                block_id = block.label if isinstance(block.label, int) else 0
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
                # print(f"GEN Bloco {block.label}")
                # for var in gen_block.keys():
                #     print(f"\t{var} : {gen_block[var]}")
                    gens[block_id] = gen_block
                    # gen_block = {}
                block = block.next_block
            print("defs:")
            for var in defs.keys():
                print(f"var: {var} linhas: {defs[var]}")
            # Calcula Kill
            # print(gens)
            # defs_set = set(defs)
            for block_id in gens.keys():
                kill_block = {}
                for var in gens[block_id].keys():
                    last_attr_line = [gens[block_id][var]]
                    # print(f"vai tirar {last_attr_line} de {defs[var]}")
                    var_set = set(defs[var])
                    line_kill = var_set.difference(last_attr_line)
                    # print(defs_set)
                    kill_block[var] = list(line_kill)
                kills[block_id] = kill_block
            
            for block in kills.keys():
                print(f"Bloco {block}")
                print(f"\tgen : {gens[block]}")
                print(f"\tkill : {kills[block]}")


   
    def reachingDefinitions(self):
        """ Função que executa a analise de reaching defintions nas CFGs obtidas.
        """
        pass

    """ Liveness Analysis """

    """ Available Expressions """