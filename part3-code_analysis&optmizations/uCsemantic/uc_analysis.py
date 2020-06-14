class AnalyzeOptimaze:

    def __init__(self, cfg_list):
        # CFG divididas por funcoes
        self.CFGs = cfg_list
        # codigo optimal gerado no arquivo .opt pelo uc.py
        self.optcode = ''

        # codigo optimal gerado como tupla para ser interpretador no interpreter.py
        self.code = []


    def optmize(self): # classe de teste por enquanto, no futuro aplica as otimizacoes e gera codigo
        """ .realiza as otimizacoes no codigo alterando o valor no bloco
            .atravessa cada bloco armazenando o novo codigo
            .retorna o novo codigo em forma de string para emitir o arquivo .opt
        """
        reach_gen_kill = self.get_gen_kill_RD()
        RD_in_out = {}
        for cfg_id, block in enumerate(self.CFGs):
            RD_gen = reach_gen_kill[cfg_id]['gen']
            RD_kill = reach_gen_kill[cfg_id]['kill']
            # TODO verificar se gen e kill nulos garantem in e out nulos
            print(f"\t=== CFG {cfg_id} ===")
            if RD_gen and RD_kill:
                RD_in_out[cfg_id] = self.reachingDefinitions(block, RD_gen, RD_kill)

        #self.deadcode()

        # funcao que atravessa os blocos armazenando as intrucoes no self.optcode e self.code
        # self.opt_fileandcode()

        return self.optcode


    def opt_fileandcode(self):
        """ .acessa todos os blocos e sintetiza em um codigo
            .armazena as tuplas no self.code para ser interpretado
            .retorna o codigo em forma de string, para ser escrito no .opt
        """
        for block in self.CFGs:
            while block:
                for instr in block.instructions:
                    self.code.append(instr[1])
                    self.optcode += f"{str(instr[1])}\n"
                block = block.next_block

    ############################
    #   Reaching Definitions   #
    ############################

    def get_gen_kill_RD(self):
        """
            obtenca dos dicionarios gen e kill para REACHING DEFINITIONS
        """
        cfg_gen_kill = {}
        # itera todas cfgs e obtem o gen[]
        for cfg_count, block in enumerate(self.CFGs, 0):
            # defs é um dicionario com todas as variaveis declaradas e sua de linhas onde foram declaradas
            defs = {}
            # gen é um array com o tamanho da quantidade de linhas do bloco, onde há atribuição ele salva a variavel que foi atualiuzada
            gens = {}
            # kill é todas as defs de alguma variavel menos a que foi atribuida na linha sendo itarada
            kills = {}
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
                    # salva o gen do bloco
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
            cfg_gen_kill[cfg_count] = {'gen' : gens, 'kill' : kills}

        return cfg_gen_kill


    def reachingDefinitions(self, block_head, gen, kill):
        """ Função que executa a analise de reaching defintions nas CFGs obtidas.
        """
        # inicializa uma variavel com todos os blocos para facilitar o acesso
        blocks = {}
        successors = {}
        changed = []
        _out = {}
        _in = {}
        # monta dicionario com todos os blocos
        while block_head:
            block_id = block_head.label if isinstance(block_head.label, int) else 0
            blocks[block_id] = block_head
            changed.append(block_head)
            successors[block_id] = []
            _in[block_id] = {}
            _out[block_id] = {}

            # obtem successors
            if block_head.branch:
                successors[block_id].append(block_head.branch)
            if block_head.truelabel:
                successors[block_id].append(block_head.truelabel)
            if block_head.falselabel:
                successors[block_id].append(block_head.falselabel)
            block_head = block_head.next_block

        # enquanto houver mudança nos valores
        while changed:
            # obtem bloco a ser iterado
            block = changed.pop()
            block_id = block.label if isinstance(block.label, int) else 0
            # calcula novo in
            new_in = {}
            for pred in block.predecessors:
                pred_id = pred.label if isinstance(pred.label, int) else 0
                # same_var = _in[block_id].keys() & _out[pred_id].keys()
                for var in _out[pred_id].keys():
                    if var in new_in.keys():
                        new_in[var].append(_out[pred_id][var])
                    else:
                        new_in[var] = _out[pred_id][var]
            # registra novo in
            _in[block_id] = new_in

            # salva out antigo para checagem de mudança
            old_out = _out[block_id]

            # extrai quais variaveis sao comuns ao kill e gen
            same_var = kill[block_id].keys() & gen[block_id].keys()
            # caso houver variavei comuns, obtem novo out
            if same_var:
                for var in same_var:
                    # gen é uma variavel, logo precisa ser posto em uma lista
                    gen_set = set([gen[block_id][var]])
                    kill_set = set(kill[block_id][var])
                    in_set = set(_in[block_id][var]) if var in _in[block_id] else set()
                    if var in _out[block_id].keys():
                        _out[block_id][var] = list(gen_set.union(in_set.difference(kill_set)))
                    else:
                        _out[block_id] = {var: list(gen_set.union(in_set.difference(kill_set)))}
            # verifica se houve mudança ou o resultado convergiu
            if old_out != _out[block_id]:
                if block_id in successors.keys():
                    for suc in successors[block_id]:
                        changed.append(suc)
        # printa resultado
        print("BLOCK\tIN\t\tOUT")
        for blockin, blockout in zip(_in.keys(), _out.keys()):
            print(f"{blockin}\t{_in[blockin]} \t\t {_out[blockout]}")

        return {"in": _in, "out" : _out}

    #########################
    #   Liveness Analysis   #
    #########################

    def liveness_anal(self):
        """ .funcao que realiza o liveness analysis
            .retorna uma lista que cada item é um dict contendo o bloco como chave e uma lista com os in's e out's
            .retorna uma lista que cada item é um dict contendo o bloco como chave e uma lista com os use e defs
        """
        cfgs_inout = []
        # inicializa com um dict vazio, pois a primeira posicao é um bloco dos globais
        cfgs_inout.append({})

        # 1. achar o gen e kill de cada bloco em todas as CFG
        #       estrutura: [{},{label:[[gen],[kill]]}, ...]
        #       cada dict é uma CFG, cada key é label do bloco, cada key guarda uma lista com duas listas gen e kill
        cfgs_genkill = self._getGenKill()
        #print(cfgs_genkill[1][18])

        # 2. worklist para definir os in's e out's
        #       in_out é um dict contendo como key o label do bloco e valor uma lista [[in],[out]]
        for i in range(1, len(self.CFGs)):
            in_out = self._worklist_live(self.CFGs[i], cfgs_genkill[i])
            aux = in_out.copy()
            cfgs_inout.append(aux)
            in_out.clear()

        return cfgs_inout, cfgs_genkill


    def _worklist_live(self, cfg, cfg_genkill):
        """ .realiza o algoritmo de worklist para determinar os in's e out's de cada bloco
            .cfg corresponde ao primeiro bloco da CFG (lista a la 'c')
            .cfg_genkill representa um dicionario com uma key sendo o label do bloco e o valor uma lista[[gen],[kill]]
            .retorna um dict com a key sendo o label do bloco e o valor uma lista [[in],[out]]
        """
        # estrutura para criar o dict de return
        cfg_inout = {}

        # algoritmo worklist
        worklist = []

        #   inicializa a lista W com os labels de todos os blocos
        #   inicializa um dict com o label dos sucessores de um bloco
        #   inicializa um dict com o label dos predecessores de um bloco
        succ = {}
        successors = []
        pred = {}
        predecessors = []
        block = cfg
        while block:
            worklist.append(block.label)
            # successors
            if block.branch:
                successors.append(block.branch.label)
            if block.truelabel:
                successors.append(block.truelabel.label)
            if block.falselabel:
                successors.append(block.falselabel.label)
            succ[block.label] = successors.copy()
            successors.clear()
            # predecessors
            for p in block.predecessors:
                predecessors.append(p.label)
            pred[block.label] = predecessors.copy()
            predecessors.clear()

            block = block.next_block

        #   inicializa todos os blocos com duas listas vazias [in] e [out]
        for block in worklist:
            cfg_inout[block] = [[],[]]

        #   inicia a lista [out] dos blocos de saida com todas as variáveis globais
        # TODO

        #   enquanto houver blocos para serem analisados
        #   cfg_inout[n][0] -> in[n] e cfg_inout[n][1] -> out[n]
        #   cfg_genkill[n][0] -> gen[n] e cfg_genkill[n][1] -> kill[n]
        while worklist:
            # let n = w.pop()
            n = worklist.pop()
            # old_in = in[n]
            old_in = cfg_inout[n][0]
            # out[n] := Un'insucc[n] in[n1]
            auxin = []
            for succ_in in succ[n]:
                auxin = list(set(auxin) | set(cfg_inout[succ_in][0]))
            cfg_inout[n][1] = auxin.copy()
            auxin.clear()
            # in[n] := gen[n] U (out[n] - kill[n])
            cfg_inout[n][0] = list(set(cfg_genkill[n][0]) | set([v for v in cfg_inout[n][1] if v not in cfg_genkill[n][1]]))
            # if(old_in != in[n])
            if old_in != cfg_inout[n][0]:
                for m in pred[n]:
                    worklist.append(m)

        return cfg_inout


    def _getGenKill(self):
        # lista em que cada item é um dict da forma 'block_label': [[gen],[kill]]
        # portanto, cada item representa uma CFG
        cfgs_genkill = []

        # estrutura para armazenar os gen/kill de cada bloco
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
                            if kill in block_gen:
                                block_gen.remove(kill)
                        gen = self._getGen_live(instr)
                        if gen and (gen not in block_gen):
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
            .use
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
            .def
        """
        kill = None

        if 'store' in instr[1][0]:
            kill = instr[1][2]
        elif 'read' in instr[1][0]:
            pass

        return kill

    #############################
    #   Dead Code Elimination   #
    #############################
    def deadcode(self):
        """ .realiza a liveness analysis
            .para cada bloco analisa se ha deadcode
            .altera o codigo otimizando-o
        """
        liveness, usedef = self.liveness_anal()
        print(liveness)
        print(usedef)

        for i in range(1, len(self.CFGs)):
            firstblock = self.CFGs[i]
            block = firstblock
            while block:
                for instr in block.instructions:
                    if 'store' in instr[1][0]:
                        if instr[1][2] in usedef[i][block.label][1]:
                            if instr[1][2] not in liveness[i][block.label][1]:
                                print(instr)

                block = block.next_block

    """ Available Expressions """

