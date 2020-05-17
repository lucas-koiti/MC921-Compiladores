import os
import subprocess
import traceback

def test_0():
    test_name = 'test'
    test = True
    try:
        os.system(f"python3 uc.py codes_test/{test_name}.uc")
    except:
        traceback.print_exc()
        test = False
    # resposta correta
    res = [
        ('global_float_2_2', '@e', [[1.0, 2.0], [1.0, 2.0]]),
        ('global_int_3', '@.str.0', [1, 2, 3]),
        ('global_char_2', '@.str.1', 'oi'),
        ('global_float_2_2', '@.str.2', [[1.0, 2.0], [1.0, 2.0]]),
        ('define', '@main'),
        ('alloc_int_3', '%2'),
        ('store_int_3', '@.str.0', '%2'),
        ('alloc_int_2_3', '%3'),
        ('alloc_char_2', '%4'),
        ('store_char_2', '@.str.1', '%4'),
        ('alloc_float_2_2', '%5'),
        ('store_float_2_2', '@.str.2', '%5'),
        ('jump', '%1'),
        ('1',),
        ('return_void',)
        ]
    if test:
        test = check_output(test_name, res)
    
    assert test == True


def test_1():
    test_name = "1test"
    test = True
    try:
        os.system(f"python3 uc.py codes_test/{test_name}.uc")
    except:
        traceback.print_exc()
        test = False
    # resposta correta
    res = [
            ('global_int', '@n', 3),
            ('global_string', '@.str.0', 'assertion_fail on 10:12'),
            ('define', '@doubleMe'),
            ('alloc_int', '%2'),
            ('store_int', '%0', '%2'),
            ('load_int', '%2', '%4'),
            ('load_int', '%2', '%5'),
            ('mul_int', '%4', '%5', '%6'),
            ('store_int', '%6', '%1'),
            ('jump', '%3'),
            ('3',),
            ('load_int', '%1', '%7'),
            ('return_int', '%7'),
            ('define', '@main'),
            ('alloc_int', '%2'),
            ('load_int', '@n', '%3'),
            ('store_int', '%3', '%2'),
            ('load_int', '%2', '%4'),
            ('param_int', '%4'),
            ('call', '@doubleMe', '%5'),
            ('store_int', '%5', '%2'),
            ('load_int', '@n', '%6'),
            ('load_int', '@n', '%7'),
            ('mul_int', '%6', '%7', '%8'),
            ('load_int', '%2', '%9'),
            ('eq_int', '%9', '%8', '%10'),
            ('cbranch', '%10', '%11', '%12'),
            ('11',),
            ('jump', '%13'),
            ('12',),
            ('print_string', '@.str.0'),
            ('jump', '%1'),
            ('13',),
            ('jump', '%1'),
            ('1',),
            ('return_void',),
        ]
    if test:
        test = check_output(test_name, res)
    
    assert test == True


def test_2():
    test_name = "2test"
    test = True
    try:
        os.system(f"python3 uc.py codes_test/{test_name}.uc")
    except:
        traceback.print_exc()
        test = False
    # resposta correta
    res = [
            ('define', '@main'),
            ('alloc_int', '%2'),
            ('alloc_int', '%3'),
            ('alloc_float', '%4'),
            ('literal_int', 3, '%5'),
            ('store_int', '%5', '%3'),
            ('literal_float', 4.5, '%6'),
            ('store_float', '%6', '%4'),
            ('literal_int', 5, '%7'),
            ('load_int', '%3', '%8'),
            ('add_int', '%8', '%7', '%9'),
            ('store_int', '%9', '%2'),
            ('load_int', '%2', '%10'),
            ('sitofp', '%10', '%11'),
            ('store_float', '%11', '%4'),
            ('load_float', '%4', '%12'),
            ('fptosi', '%12', '%13'),
            ('store_int', '%13', '%3'),
            ('literal_int', 0, '%14'),
            ('store_int', '%14', '%0'),
            ('jump', '%1'),
            ('1',),
            ('load_int', '%0', '%15'),
            ('return_int', '%15'),
        ]
    if test:
        test = check_output(test_name, res)
    
    assert test == True


def test_3():
    test_name = "3test"
    test = True
    try:
        os.system(f"python3 uc.py codes_test/{test_name}.uc")
    except:
        traceback.print_exc()
        test = False
    # resposta correta
    res = [
            ('define', '@main'),
            ('alloc_int', '%2'),
            ('alloc_int', '%3'),
            ('alloc_int_*', '%4'),
            ('alloc_int_5', '%5'),
            ('load_int', '%3', '%6'),
            ('elem_int', '%5', '%6', '%7'),
            ('get_int_*', '%7', '%4'),
            ('load_int', '%3', '%8'),
            ('elem_int', '%5', '%8', '%9'),
            ('load_int_*', '%9', '%10'),
            ('store_int', '%10', '%2'),
            ('load_int', '%2', '%11'),
            ('load_int', '%3', '%12'),
            ('add_int', '%11', '%12', '%13'),
            ('load_int', '%2', '%14'),
            ('elem_int', '%5', '%14', '%15'),
            ('store_int_*', '%13', '%15'),
            ('jump', '%1'),
            ('1',),
            ('return_void',),
        ]
    if test:
        test = check_output(test_name, res)
    
    assert test == True


def test_4():
    test_name = "4test"
    test = True
    try:
        os.system(f"python3 uc.py codes_test/{test_name}.uc")
    except:
        traceback.print_exc()
        test = False
    # resposta correta
    res = [
            ('global_string', '@.str.0', 'assertion_fail on 5:12'),
            ('define', '@main'),
            ('alloc_int', '%2'),
            ('alloc_int', '%3'),
            ('alloc_int', '%4'),
            ('literal_int', 2, '%5'),
            ('store_int', '%5', '%2'),
            ('load_int', '%2', '%6'),
            ('literal_int', 1, '%7'),
            ('add_int', '%6', '%7', '%8'),
            ('store_int', '%8', '%2'),
            ('store_int', '%8', '%3'),
            ('load_int', '%2', '%9'),
            ('literal_int', 1, '%10'),
            ('add_int', '%9', '%10', '%11'),
            ('store_int', '%11', '%2'),
            ('store_int', '%9', '%4'),
            ('literal_int', 4, '%12'),
            ('load_int', '%2', '%13'),
            ('eq_int', '%13', '%12', '%14'),
            ('load_int', '%3', '%15'),
            ('load_int', '%4', '%16'),
            ('eq_int', '%15', '%16', '%17'),
            ('and_bool', '%14', '%17', '%18'),
            ('cbranch', '%18', '%19', '%20'),
            ('19',),
            ('jump', '%21'),
            ('20',),
            ('print_string', '@.str.0'),
            ('jump', '%1'),
            ('21',),
            ('literal_int', 1, '%22'),
            ('store_int', '%22', '%0'),
            ('jump', '%1'),
            ('1',),
            ('load_int', '%0', '%23'),
            ('return_int', '%23'),
        ]
    if test:
        test = check_output(test_name, res)
    
    assert test == True


def test_5():
    test_name = "5test"
    test = True
    try:
        os.system(f"python3 uc.py codes_test/{test_name}.uc")
    except:
        traceback.print_exc()
        test = False
    # resposta correta
    res = [
            ('global_string', '@.str.0', 'assertion_fail on 7:12'),
            ('define', '@main'),
            ('alloc_int', '%2'),
            ('alloc_int', '%3'),
            ('alloc_int', '%4'),
            ('literal_int', 1, '%5'),
            ('store_int', '%5', '%2'),
            ('literal_int', 2, '%6'),
            ('store_int', '%6', '%3'),
            ('literal_int', 1, '%10'),
            ('store_int', '%10', '%4'),
            ('7',),
            ('literal_int', 10, '%11'),
            ('load_int', '%4', '%12'),
            ('lt_int', '%12', '%11', '%13'),
            ('cbranch', '%13', '%8', '%9'),
            ('8',),
            ('load_int', '%3', '%14'),
            ('load_int', '%4', '%15'),
            ('mul_int', '%14', '%15', '%16'),
            ('load_int', '%2', '%17'),
            ('add_int', '%16', '%17', '%18'),
            ('store_int', '%18', '%2'),
            ('load_int', '%4', '%19'),
            ('literal_int', 1, '%20'),
            ('add_int', '%19', '%20', '%21'),
            ('store_int', '%21', '%4'),
            ('jump', '%7'),
            ('9',),
            ('literal_int', 91, '%22'),
            ('load_int', '%2', '%23'),
            ('eq_int', '%23', '%22', '%24'),
            ('cbranch', '%24', '%25', '%26'),
            ('25',),
            ('jump', '%27'),
            ('26',),
            ('print_string', '@.str.0'),
            ('jump', '%1'),
            ('27',),
            ('literal_int', 0, '%28'),
            ('store_int', '%28', '%0'),
            ('jump', '%1'),
            ('1',),
            ('load_int', '%0', '%29'),
            ('return_int', '%29'),
        ]
    if test:
        test = check_output(test_name, res)
    
    assert test == True


def test_6():
    test_name = "6test"
    test = True
    try:
        os.system(f"python3 uc.py codes_test/{test_name}.uc")
    except:
        traceback.print_exc()
        test = False
    # resposta correta
    res = [
            ('global_float_3', '@.str.0', [1.0, 2.5, 5.0]),
            ('global_string', '@.str.1', 'xpto'),
            ('global_int_6_2', '@.str.2', [[1, 3], [2, 6], [3, 9]]),
            ('global_string', '@.str.3', 'Isto eh um teste: '),
            ('define', '@main'),
            ('alloc_float_3', '%2'),
            ('alloc_char_4', '%3'),
            ('alloc_int_6_2', '%4'),
            ('alloc_int', '%5'),
            ('alloc_int', '%6'),
            ('store_float_3', '@.str.0', '%2'),
            ('store_char_4', '@.str.1', '%3'),
            ('store_int_6_2', '@.str.2', '%4'),
            ('literal_int', 1, '%7'),
            ('store_int', '%7', '%5'),
            ('literal_int', 0, '%8'),
            ('store_int', '%8', '%6'),
            ('print_string', '@.str.3'),
            ('literal_int', 2, '%9'),
            ('load_int', '%6', '%10'),
            ('add_int', '%10', '%9', '%11'),
            ('elem_char', '%3', '%11', '%12'),
            ('load_char_*', '%12', '%13'),
            ('print_char', '%13'),
            ('load_int', '%5', '%14'),
            ('elem_float', '%2', '%14', '%15'),
            ('load_float_*', '%15', '%16'),
            ('print_float', '%16'),
            ('literal_int', 2, '%17'),
            ('load_int', '%5', '%18'),
            ('mul_int', '%17', '%18', '%19'),
            ('load_int', '%6', '%20'),
            ('add_int', '%19', '%20', '%21'),
            ('elem_int', '%4', '%21', '%22'),
            ('load_int_*', '%22', '%23'),
            ('print_int', '%23'),
            ('literal_int', 0, '%24'),
            ('store_int', '%24', '%0'),
            ('jump', '%1'),
            ('1',),
            ('load_int', '%0', '%25'),
            ('return_int', '%25'),
        ]
    if test:
        test = check_output(test_name, res)
    
    assert test == True


def check_output(test_name: str, res: [(str)])->bool:
    """ Verifica se as operacoes do .ir são as mesmas que as passadas pelo marcio nos exemplos
    Não varifica variaveis nem ordem.
    Parametros
    -----------
        test_name: str
            nome do arquivo de saída
        res: list
            lista de tuplas com as operacoes de saída
    Return
    ----------
        bool
            resultado do teste, verdadeiro se todas operacoes resultantes estao na saída do Marcio
    """
    test = True
    # extrai saida
    with open(f"codes_test/{test_name}.ir", 'r') as file:
        lines = [line.rstrip('\n') for line in file]
    # verifica 
    if lines:
        for idx, line in enumerate(lines, 1):
            # extrai a operacao
            op = line.split("\'")[1]
            ops = [x[0] for x in res]
            if op not in ops:
                test == False
                print(f"{line} está incorreto (linha {idx})")
    else:
        test = False
    
    return test


# if __name__ == '__main__':
#     res = [
#             ('global_float_3', '@.str.0', [1.0, 2.5, 5.0]),
#             ('global_string', '@.str.1', 'xpto'),
#             ('global_int_6_2', '@.str.2', [[1, 3], [2, 6], [3, 9]]),
#             ('global_string', '@.str.3', 'Isto é um teste: '),
#             ('define', '@main'),
#             ('alloc_float_3', '%2'),
#             ('alloc_char_4', '%3'),
#             ('alloc_int_6_2', '%4'),
#             ('alloc_int', '%5'),
#             ('alloc_int', '%6'),
#             ('store_float_3', '@.str.0', '%2'),
#             ('store_char_4', '@.str.1', '%3'),
#             ('store_int_6_2', '@.str.2', '%4'),
#             ('literal_int', 1, '%7'),
#             ('store_int', '%7', '%5'),
#             ('literal_int', 0, '%8'),
#             ('store_int', '%8', '%6'),
#             ('print_string', '@.str.3'),
#             ('literal_int', 2, '%9'),
#             ('load_int', '%6', '%10'),
#             ('add_int', '%10', '%9', '%11'),
#             ('elem_char', '%3', '%11', '%12'),
#             ('load_char_*', '%12', '%13'),
#             ('print_char', '%13'),
#             ('load_int', '%5', '%14'),
#             ('elem_float', '%2', '%14', '%15'),
#             ('load_float_*', '%15', '%16'),
#             ('print_float', '%16'),
#             ('literal_int', 2, '%17'),
#             ('load_int', '%5', '%18'),
#             ('mul_int', '%17', '%18', '%19'),
#             ('load_int', '%6', '%20'),
#             ('add_int', '%19', '%20', '%21'),
#             ('elem_int', '%4', '%21', '%22'),
#             ('load_int_*', '%22', '%23'),
#             ('print_int', '%23'),
#             ('literal_int', 0, '%24'),
#             ('store_int', '%24', '%0'),
#             ('jump', '%1'),
#             ('1',),
#             ('load_int', '%0', '%25'),
#             ('return_int', '%25'),
#         ]
#     ops = [x[0] for x in res]
#     print(ops)
#     if 'jump' in ops:
#         print('top')
#     else:
#         print('not top')