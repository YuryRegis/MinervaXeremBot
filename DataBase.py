import sqlite3


def connection_on():
    connection = sqlite3.connect('banco.db', check_same_thread=False)
    cursor = connection.cursor()
    return connection, cursor


def create_table():
    connection, cursor = connection_on()
    cursor.execute('CREATE TABLE IF NOT EXISTS dados (data txt, id txt, origem text, destino txt, \
                    hora text, vagas integer, valor1 real, valor2 real, caroneiros txt)')
    connection.close()


def format_ans(linha, answer):
    answer += '\n<b>Data:</b> {} <b>Hora:</b> {}'.format(linha[0], linha[4])
    answer += '\n<b>Origem:</b> {} <b>Destino:</b> {}'.format(linha[2].title(), linha[3].title())
    answer += '\n<b>Motorista:</b> {} <b>Vagas:</b> {}'.format(linha[1].title(), linha[5])
    answer += '\n<b>Valor:</b> R${:.2f} ou R${:.2f}'.format(linha[6], linha[7])
    answer += '\n<b>Caroneiros:</b>'
    if len(linha[8]) == 0:
        answer += ' Nenhum'
    else:
        for nome in linha[8].split(' '):
            answer += ' {}'.format(nome.title())
    answer += '\n'
    return answer


def cancel_carona(passageiro, motorista, data, hora):
    connection, cursor = connection_on()
    slc = 'SELECT {} FROM dados where id = ? and data = ? and hora = ?'
    upd = 'UPDATE dados set {} = ? where id = ? and data = ? and hora = ?'
    vagas = list(cursor.execute(slc.format('vagas'), (motorista, data, hora)))
    vagas = vagas[0][0]
    try:
        caroneiros = list(cursor.execute(slc.format('caroneiros'), (motorista, data, hora)))
        caroneiros = [x.lower() for x in caroneiros[0]]
        caroneiros = caroneiros[0].split()
        if len(caroneiros) == 0 or passageiro.lower() not in caroneiros:
            connection.close()
            return 'Oops! {}, seu nome não consta na lista de caroneiros desta viagem.'.format(passageiro.title())
        caroneiros.remove(passageiro.lower())
        caroneiros = [x.title() for x in caroneiros]
        caroneiros = ' '.join(caroneiros)
        cursor.execute(upd.format('caroneiros'), (caroneiros, motorista, data, hora))
        cursor.execute(upd.format('vagas'), (vagas+1, motorista, data, hora))
        connection.commit()
    except:
        connection.close()
        return 'Oops! Algo de errado não está certo.\nUse /help ou /ajuda para consulta de comandos.'
    connection.close()
    return '{} cancelou carona com {}.\nViagem: {} às {}'.format(passageiro, motorista, data, hora)


def delet_info(nome, data, hora):
    connection, cursor = connection_on()
    try:
        ans = ''
        sql = 'DELETE FROM dados WHERE id = ? and data = ? and hora = ?'
        sql2 = 'SELECT * FROM dados WHERE id = ? and data = ? and hora = ?'
        for linha in cursor.execute(sql2, (nome, data, hora)):
            ans += format_ans(linha, ans)
        cursor.execute(sql, (nome, data, hora))
        connection.commit()
        connection.close()
        return '{} cancelou a seguinte viagem:\n'.format(nome) + ans
    except:
        return 'Sinto muito, viagem não localizada. :('


def insert_table(data, id, ida, volta, hora, vagas, valor1, valor2, caroneiros=''):
    connection, cursor = connection_on()
    cursor.execute('INSERT INTO dados (data, id, origem, destino, hora, vagas, valor1, valor2, caroneiros) '
                   'VALUES(?,?,?,?,?,?,?,?,?)', (data, id.lower(), ida.lower(), volta.lower(),
                                                 hora, vagas, valor1, valor2, caroneiros))
    connection.commit()
    connection.close()


def insert_carona(motorista, data, hora, passageiro):
    connection, cursor = connection_on()
    sql = 'UPDATE dados SET {} = ? where id = ? and data = ? and hora = ?'
    sql2 = 'SELECT {} FROM dados where id = ? and data = ? and hora = ?'
    vagas = list(cursor.execute(sql2.format('vagas'), (motorista, data, hora)))
    pas_atual = list(cursor.execute(sql2.format('caroneiros'), (motorista, data, hora)))
    pas_atual = pas_atual[0][0]
    vagas = vagas[0][0]
    if vagas > 0:
        vagas -= 1
        pas_atual += ' {}'.format(passageiro)
        cursor.execute(sql.format('caroneiros'), (pas_atual, motorista, data, hora))
        cursor.execute(sql.format('vagas'), (vagas, motorista, data, hora))
    else:
        connection.close()
        txt = '{} solicitou uma carona de {} ({} às {}) porem não existe mais vagas para esta viagem. :('
        return txt.format(passageiro.title, motorista.title, data, hora)
    connection.commit()
    connection.close()
    return '{} adicionado(a) no carro de {}.\nViagem: {} às {}'.format(passageiro.title(),
                                                                      motorista.title(), data, hora)


def change_table(opcao, valor, origem, destino, data):
    connection, cursor = connection_on()
    if opcao.lower() in ['data', 'hora', 'vagas', 'origem', 'destino', 'valor1', 'valor2']:
        if opcao.lower == 'vagas':
            valor = int(valor)
        elif opcao.lower in ['valor1', 'valor2']:
            valor = float(valor.replace(',', '.'))
        sql = 'UPDATE dados SET {} = ? where origem = ? and destino = ? and data = ?'.format(opcao.lower())
        cursor.execute(sql, (valor, origem, destino, data))
        connection.commit()
        ans = 'Alterações salvas com sucesso.'
    else:
        ans = 'Ooops, algo de errado não esta certo!\nUse o comando /help ou /ajuda para consultar o manual.'
    connection.close()
    return ans


def search_table(origem, destino, date):
    connection, cursor = connection_on()
    sql = 'SELECT * FROM dados WHERE origem = ? and destino = ? and data = ?'
    answer = ''
    for linha in cursor.execute(sql, (origem.lower(), destino.lower(), date)):
        answer += format_ans(linha, answer)
    if len(answer) == 1:
        answer = '\nNenhuma carona ofertada de {} para {}.'.format(origem.capitalize(), destino.capitalize())
    connection.close()
    return answer


def simple_search(palavra):
    connection, cursor = connection_on()
    answer = ''
    valores = cursor.execute('SELECT * FROM dados;').fetchall()
    for linha in valores:
        if palavra.lower() in linha:
            answer += format_ans(linha, answer)
    if len(answer) == 0:
        answer = '\nNenhum resultado para "{}"'.format(palavra.capitalize())
    connection.close()
    return answer


def select_date_destiny(origem, destino, data):
    connection, cursor = connection_on()
    selecao = tuple(cursor.execute('SELECT * FROM dados where origem = ? and destino = ? and data = ?',
                             (origem.lower(), destino.lower(), data)))
    connection.close()
    return selecao


def select_date_id(motorista, data, hora):
    connection, cursor = connection_on()
    sql = 'SELECT * FROM dados where id = ? and data = ? and hora = ?'
    selecao = tuple(cursor.execute(sql, (motorista, data, hora)))
    connection.close()
    return selecao


def clean_table(date):
    connection, cursor = connection_on()
    try:
        cursor.execute('DELETE FROM dados WHERE data < ?', (date,))
        connection.commit()
        connection.close()
        return 'Limpeza do banco de dados concluida ! :)'
    except:
        return 'Sinto muito, não foi possível completar a limpeza do banco de dados. :('


def check_value(value, date):
    connection, cursor = connection_on()
    for linha in cursor.execute('SELECT * FROM dados;').fetchall():
        if value in linha and date in linha:
            connection.close()
            return True
        else:
            pass
    connection.close()
    return False
