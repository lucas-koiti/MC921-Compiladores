class AnalyzeOptimaze:

    def __init__(self, cfg_list):
        # CFG divididas por funcoes
        self.CFGs = cfg_list
        # codigo gerado no arquivo .opt pelo uc.py
        self.optcode = ''

        # codigo gerado como tupla para ser interpretador no interpreter.py
        self.code = []


    def optmize(self): # classe de teste por enquanto, no futuro aplica as otimizacoes e gera codigo
        """ .realiza as otimizacoes no codigo alterando o valor no bloco
            .atravessa cada bloco armazenando o novo codigo
            .retorna o novo codigo em forma de string para emitir no arquivo .opt
        """
        
        #realiza o constant propagation
        self.constantprop()

        #realiza o deadcode elimination
        self.deadcode()

        # funcao que atravessa os blocos armazenando as intrucoes no self.optcode e self.code
        self.opt_fileandcode()

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
    #   Constant Propagation   #
    ############################
    def constantprop(self):
        """ .calcula o gen/kill de todos os blocos em todas as cfgs
            .define quem sao os temporarios dos literais
            .realiza o reaching definitions
            .elimina as instrucoes de load do literal para a variavel
            .substitui os valores que sofriam load var -> temp, para temp = literal
        """
        # calcula os gens/kills e def de todas CFGs
        reach_gen_kill, defs = self.get_gen_kill_RD()
        
        # define os literais
        list_literals = []
        literals = {}
        i = 0
        for cfg in self.CFGs:
            block = cfg
            while block:
                for instr in block.instructions:
                    if 'literal' in instr[1][0]:
                        literals[instr[1][2]] = instr[1][1]
                block = block.next_block
            list_literals.append(literals.copy())
            literals.clear()
        
        # faz um match entre a variavel e o temporario do literal
        constants = []
        _cte = {}
        for i in range(len(self.CFGs)):
            for k in defs[i].keys():
                for v in defs[i][k]:
                    if v in list_literals[i].keys():
                        _cte[k] = v
            constants.append(_cte.copy())
            _cte.clear()

        #aplica o reaching definitions para todos os blocos e cfgs
        RD_in_out = {}
        for cfg_id, block in enumerate(self.CFGs):
            RD_gen = reach_gen_kill[cfg_id]['gen']
            RD_kill = reach_gen_kill[cfg_id]['kill']
            
            if cfg_id != 0:
                if RD_gen and RD_kill:
                    RD_in_out[cfg_id] = self.reachingDefinitions(block, RD_gen, RD_kill)
            
        # identifica as instrucoes que podem ser removidas e as que devem ser alteradas
        i = 0
        _rmvdict = {}
        _rmvlist = []
        for cfg in self.CFGs:
            block = cfg
            while block:
                for instr in block.instructions:
                    if 'load' in instr[1][0]:
                        if instr[1][1] in RD_in_out[i][block.label][1]:
                            if(len(defs[i][instr[1][1]]) == 1) and instr[1][1] in constants[i].keys():
                                _rmvdict[instr[1][2]] = instr[1][1]
                                _rmvlist.append(instr)

                for inst in _rmvlist:
                    block.instructions.remove(inst)
                
                for instr in block.instructions:
                    for var in _rmvdict.keys():
                        if var in instr[1]:
                            _aux = list(instr[1])
                            for w in range(len(_aux)):
                                if _aux[w] == var:
                                    _aux[w] = constants[i][_rmvdict[var]]
                            _aux = tuple(_aux)
                            instr[1] = _aux
                            
                _rmvdict.clear()
                _rmvlist.clear()
                block = block.next_block
            i += 1

    #############################
    #   Dead Code Elimination   #
    #############################
    def deadcode(self):
        """ .realiza a liveness analysis
            .para cada bloco analisa se ha deadcode
            .altera o codigo otimizando-o
        """
        liveness, usedef = self.liveness_anal()
        #print(liveness)
        #print(usedef)

        for i in range(1, len(self.CFGs)):
            # primeiro, identifica unreachable code
            firstblock = self.CFGs[i]
            block = firstblock
            while block:
                if block.kind == 0:
                    _return = -1
                    _rmvlist = []
                    for instr in block.instructions:
                        if 'return' in instr[1][0]:
                            block.kind = -1
                            _return = instr[0]
                        elif instr[0] > _return and _return != -1:
                            _rmvlist.append(instr)

                    for instr in _rmvlist:
                        block.instructions.remove(instr)
                    _rmvlist.clear()
                block = block.next_block

            # segundo, identifica dead code
            firstblock = self.CFGs[i]
            block = firstblock
            _rmvlist = []
            while block:
                for instr in block.instructions:
                    if 'store' in instr[1][0]:
                        if instr[1][2] in usedef[i][block.label][1]:
                            if instr[1][2] not in liveness[i][block.label][1] and instr[1][2] not in usedef[i][block.label][0]:
                                _rmvlist.append(instr)

                _tagged = []
                for dead in _rmvlist:
                    _tagged.append(dead[1][2])

                for instr in block.instructions:
                    for tag in _tagged:
                        if tag in instr[1]:
                            if instr not in _rmvlist:
                                _rmvlist.append(instr)

                for instr in _rmvlist:
                    block.instructions.remove(instr)

                _rmvlist.clear()
                _tagged.clear()

                block = block.next_block


    ############################
    #   Reaching Definitions   #
    ############################
    def get_gen_kill_RD(self):
        """
            obtenca dos dicionarios gen e kill para REACHING DEFINITIONS
        """
        cfg_gen_kill = {}
        list_defs = []
        # itera todas cfgs e obtem o gen[]
        for cfg_count, block in enumerate(self.CFGs, 0):
            # defs é um dicionario com todas as variaveis declaradas e sua de linhas onde foram declaradas
            defs = {}
            # gen é um array com o tamanho da quantidade de linhas do bloco, onde há atribuição ele salva a variavel que foi atualiuzada
            gens = {}
            # kill é todas as defs de alguma variavel menos a que foi atribuida na linha sendo itarada
            kills = {}
            
            while block:   
                # bloco de globais é referido pelo indice 0
                block_id = block.label if isinstance(block.label, int) else 0
                # dicionario para captacao dos gens
                gen_block = {}
                # e todas suas instrucoes
                for inst in block.instructions:
                    # qualquer store adiciona a variavel em questao no gen[]
                    if inst[1][0].find('store_') != -1 and '*' not in inst[1][0]:
                        if not inst[1][0][-1].isnumeric():
                            attr_var = inst[1][2]
                            # adiciona na ultima lista vazia criada
                            gen_block[attr_var] = inst[0]
                            # guarda a variavel e a linha que foi atribuida
                            if attr_var in defs.keys():
                                defs[attr_var].append(inst[1][1])
                            else:
                                defs[attr_var] = [inst[1][1]]
                    # salva o gen do bloco
                    gens[block_id] = gen_block
                # obtem proximo bloco
                block = block.next_block

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

            
            # guarda gen e kill relativo aos cfgs
            cfg_gen_kill[cfg_count] = {'gen' : gens, 'kill' : kills}
            list_defs.append(defs.copy())
            defs.clear()

        return cfg_gen_kill, list_defs


    def reachingDefinitions(self, block_head, gen, kill):
        """ Função que executa a analise de reaching defintions nas CFGs obtidas.
        """
        # tratando a estrutura
        _gen = {}
        _genaux = []
        for i in gen.keys():
            for k in gen[i].keys():
                _genaux.append(k)
            _gen[i] = _genaux.copy()
            _genaux.clear()
        
        _kill = {}
        _killaux = []
        for i in kill.keys():
            for k in kill[i].keys():
                _killaux.append(k)
            _kill[i] = _killaux.copy()
            _killaux.clear()
        
        #   inicializa a lista worklist com os labels de todos os blocos
        #   inicializa um dict com o label dos sucessores de um bloco (e.g. dict[bloco.label] = [succs])
        #   inicializa um dict com o label dos predecessores de um bloco
        worklist = []
        succ = {}
        successors = []
        pred = {}
        predecessors = []
        block = block_head
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
        
        # inicializa o IN e OUT como zero
        _inout = {}
        for l in worklist:
            _inout[l] = [[],[]]
        
        # _inout[n] => in[n] = _inout[n][0] 
        #              out[n] = _inout[n][1]
        while worklist:
            n = worklist.pop()

            _inaux = []
            # for all nodes p in predecessors(n) 
            for p in pred[n]:
                # in[n] = in[n] U out[p]
                _inaux = list(set(_inaux) | set(_inout[p][1]))
            _inout[n][0] = _inaux.copy()
            _inaux.clear()

            # oldout = OUT[n]
            _oldout = _inout[n][1]

            # OUT[n] = GEN[n] Union (IN[n] -KILL[n])
            _inout[n][1] = list(set(_gen[n]) | set([v for v in _inout[n][0] if v not in _kill[n]]))

            # if (OUT[n] changed)
            if _inout[n][1] != _oldout:
                # for all nodes s in successors(n) 
                for s in succ[n]:
                    # Changed = Changed U { s }
                    worklist.append(s)

        return _inout

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
        block = cfg
        while block:
            if block.kind == -1 or block.kind == 0:
                for instr in self.CFGs[0]:
                    cfg_inout[block.label][1].append(instr[1][1])
            block = block.next_block

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
                            block_gen += gen

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
        gen = []

        if 'load' in instr[1][0] and '*' not in instr[1][0]:
            if not instr[1][0][-1].isnumeric():
                gen.append(instr[1][1])
        elif 'param' in instr[1][0]:
            pass
        elif 'print' in instr[1][0]:
            pass
        elif 'call' in instr[1][0]:
            gen.append(instr[1][1])
            for inst in self.CFGs[0]:
                gen.append(inst[1][1])

        return gen

    def _getKill_live(self, instr):
        """ .recebe uma instrucao
            .retorna o Kill dela
            .def
        """
        kill = None

        if 'store' in instr[1][0] and '*' not in instr[1][0]:
            if not instr[1][0][-1].isnumeric():
                kill = instr[1][2]
        elif 'read' in instr[1][0]:
            pass

        return kill


