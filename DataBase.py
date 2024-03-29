import sqlite3


def connection_on():
    connection = sqlite3.connect('banco.db', check_same_thread=False)
    cursor = connection.cursor()
    return connection, cursor


def create_table():
    connection, cursor = connection_on()
    cursor.execute('CREATE TABLE IF NOT EXISTS dados (data txt, id txt, origem text, destino txt, \
                    hora text, vagas integer, valor1 real, valor2 real, caroneiros txt, pass_id txt, tgid int)')
    cursor.execute('CREATE TABLE IF NOT EXISTS cadastro (username txt, tgid int)')
    connection.close()


def check_cadastro(tgid):
    connection, cursor = connection_on()
    sql = 'SELECT * FROM cadastro WHERE tgid = ?'
    ans = list(cursor.execute(sql, (tgid,)))
    if len(ans) == 0: return False
    connection.close()
    return True


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


def search_byid(tgid, key):
    try:
        connection, cursor = connection_on()
        sql = 'SELECT {} FROM dados where tgid = ?'.format(key)
        ans = tuple(cursor.execute(sql, (tgid,)).fetchall())
        print(ans)
        ans = [x[0] for x in ans]
        connection.close()
        return ans
    except:
        print('Search_byid?', False)
        return 0


def cancel_carona(passageiro, pass_id, motorista, data, hora):
    connection, cursor = connection_on()
    slc = 'SELECT {} FROM dados where id = ? and data = ? and hora = ?'
    upd = 'UPDATE dados set {} = ? where id = ? and data = ? and hora = ?'
    vagas = list(cursor.execute(slc.format('vagas'), (motorista, data, hora)))
    try:
        vagas = vagas[0][0]
    except IndexError:
        vagas = 0
    try:
        caroneiros = list(cursor.execute(slc.format('caroneiros'), (motorista.lower(), data, hora)))
        print("Caroneiros?", caroneiros)
        caroneiros = [x.lower() for x in caroneiros[0]]
        caroneiros_id = list(cursor.execute(slc.format('pass_id'), (motorista.lower(), data, hora)))
        print("Caroneiros?", caroneiros_id)
        caroneiros_id = [x for x in caroneiros_id[0]]
        caroneiros = caroneiros[0].split()
        caroneiros_id = caroneiros_id[0].split()
        if len(caroneiros) == 0 or str(pass_id) not in caroneiros_id:
            connection.close()
            return 0
        caroneiros.remove(passageiro.lower())
        caroneiros_id.remove(str(pass_id))
        caroneiros = [x.title() for x in caroneiros]
        caroneiros = ' '.join(caroneiros)
        caroneiros_id = ' '.join(caroneiros_id)
        cursor.execute(upd.format('caroneiros'), (caroneiros, motorista, data, hora))
        cursor.execute(upd.format('pass_id'), (caroneiros_id, motorista, data, hora))
        cursor.execute(upd.format('vagas'), (vagas+1, motorista, data, hora))
        connection.commit()
    except:
        connection.close()
        return -1
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


def delet_info_byid(tgid, hora):
    connection, cursor = connection_on()
    try:
        ans = ''
        nome = search_byid(tgid, 'id')
        sql = 'DELETE FROM dados WHERE tgid = ? and hora = ?'
        sql2 = 'SELECT * FROM dados WHERE tgid = ? and hora = ?'
        for linha in cursor.execute(sql2, (tgid, hora)):
            ans += format_ans(linha, ans)
        cursor.execute(sql, (tgid, hora))
        connection.commit()
        connection.close()
        return '{} cancelou a seguinte viagem:\n'.format(nome[0].title()) + ans
    except:
        connection.close()
        return 'Sinto muito, viagem não localizada. :('


def insert_cadastro(username, tgid):
    try:
        if not check_cadastro(tgid):
            print('{} ainda não cadastrado. Cadastrando agora...'.format(username), end=' ')
            connection, cursor = connection_on()
            sql = 'INSERT INTO cadastro (username, tgid) VALUES(?, ?)'
            cursor.execute(sql, (username, tgid))
            connection.commit()
            connection.close()
            print('OK!')
            return True
        else:
            print('{} ja cadastrado'.format(username))
            return 0
    except:
        print('Erro ao cadastrar usuario {} id {} no banco de dados'.format(username, tgid))
        return False


def len_cadastrados():
    connection, cursor = connection_on()
    try:
        user_ids = list(cursor.execute('SELECT tgid FROM cadastro', ()))
        connection.close()
        return len(user_ids)
    except:
        connection.close()
        return 0


def cadastrados():
    connection, cursor = connection_on()
    sql = 'SELECT {} FROM cadastro'
    txt = ' <b>User_id</b>  <b>User</b>\n'
    usernames = list(cursor.execute(sql.format('username'), ()))
    usernames = [user[0] for user in usernames]
    user_ids = list(cursor.execute(sql.format('tgid'), ()))
    user_ids = [user[0] for user in user_ids]
    for selection in range(len(usernames)): txt += '\n{} - {}'.format(user_ids[selection], usernames[selection])
    connection.close()
    return txt


def insert_table(data, id, ida, volta, hora, vagas, valor1, valor2, tgid, caroneiros='', pass_id=''):
    try:
        connection, cursor = connection_on()
        cursor.execute('INSERT INTO dados (data, id, origem, destino, hora, vagas, valor1, valor2, caroneiros, pass_id,'
                       ' tgid) VALUES(?,?,?,?,?,?,?,?,?,?,?)', (data, id.lower(), ida.lower(), volta.lower(),
                                                     hora, vagas, valor1, valor2, caroneiros, pass_id, tgid))
        connection.commit()
        connection.close()
        return True
    except:
        return False


def insert_carona(motorista, data, hora, passageiro, id):
    try:
        connection, cursor = connection_on()
        sql = 'UPDATE dados SET {} = ? where id = ? and data = ? and hora = ?'
        sql2 = 'SELECT {} FROM dados where id = ? and data = ? and hora = ?'
        vagas = list(cursor.execute(sql2.format('vagas'), (motorista, data, hora)))
        pas_atual = list(cursor.execute(sql2.format('caroneiros'), (motorista, data, hora)))
        pas_id = list(cursor.execute(sql2.format('pass_id'), (motorista, data, hora)))
        pas_atual = pas_atual[0][0]
        pas_id = pas_id[0][0]
        vagas = vagas[0][0]
        if vagas > 0:
            vagas -= 1
            pas_atual += ' {}'.format(passageiro)
            pas_id += ' {}'.format(id)
            cursor.execute(sql.format('caroneiros'), (pas_atual, motorista, data, hora))
            cursor.execute(sql.format('vagas'), (vagas, motorista, data, hora))
        else:
            connection.close()
            return 0
        connection.commit()
        connection.close()
        return '{} adicionado(a) no carro de {}.\nViagem: {} às {}'.format(passageiro.title(),
                                                                      motorista.title(), data, hora)
    except IndexError:
        return 0
    except:
        return -1


def extract_hora(motorista, data):
    connection, cursor = connection_on()
    sql = 'SELECT hora from dados WHERE id = ? and data = ?'
    ans = list(cursor.execute(sql, (motorista.lower(), data)))
    ans = [data[0] for data in ans]
    connection.close()
    return ans



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


def exctract_coluna(coluna):
    connection, cursor = connection_on()
    valores = cursor.execute('SELECT {} FROM dados;'.format(coluna))
    valores = [valor[0] for valor in valores]
    connection.close()
    return valores


def simple_search(palavra):
    connection, cursor = connection_on()
    answer = ''
    aux = tuple([palavra.lower() for x in range (5)])
    txt = 'SELECT * FROM dados WHERE id = ? or origem = ? or destino = ? or data = ? or tgid = ?'
    valores = tuple(cursor.execute(txt, aux))
    valores = [x for x in valores]
    if len(valores) == 0:
        answer = '\nNenhum resultado para "{}"'.format(palavra.capitalize())
        return answer
    else:
        print(len(valores), valores)
        for lista in valores:
            answer += format_ans(lista, '')
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
