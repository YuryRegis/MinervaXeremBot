import telebot
import DataBase
import datetime
import traceback
import markup
import time


bot = telebot.TeleBot('455265770:AAHdtANXvA3N7jUonXyur5HPQ9m7KcVOwjs')
msg_error = 'Oops! Algo de errado não está certo.\nUse /help ou /ajuda para consulta de comandos.'
removemkp = telebot.types.ReplyKeyboardRemove()
group_id = -209736221
adm_id = 473906011


@bot.message_handler(commands=['ajuda', 'help'], content_types='text')
def new_message(message):
    arquivo, txt = open('help_command.txt', 'r'), ''
    for linha in arquivo.readlines(): txt += linha
    bot.send_message(message.from_user.id, txt, parse_mode='HTML')


@bot.message_handler(commands=['start'], content_types='text')
def new_message(message):
    bot.send_chat_action(message.chat.id, action='TYPING')
    print('Nova conexão com ID: {}'.format(message.chat.id))
    markup.add_know_users(message.chat.id)
    name = message.from_user.first_name
    txt = 'Bem-vindo(a) {}! :)\nDigite /ajuda ou /help para me chamar.'
    if message.chat.id != group_id:
        txt = 'Bem-vindo(a) {}!\nDigite /menu para começar.'
        bot.send_message(message.chat.id, txt.format(name))
    else:
        bot.send_message(message.chat.id, txt.format(name))
    if message.chat.id != adm_id:
        notify = 'Nova conexão de {} com ID {}.'
        bot.send_message(adm_id, notify.format(name, message.chat.id))


def sair(message):
    try:
        bot.send_chat_action(message.chat.id, action='TYPING')
        del markup.userStep[message.from_user.id]
        del markup.ofertas[message.from_user.id]
        del markup.motoristas[message.from_user.id]
        del markup.selection[message.from_user.id]
        txt = 'Encerrando conexões...\n\nConcluído !\nClique em /menu para nova consulta.'
        bot.send_message(message.from_user.id, txt, reply_markup=removemkp)
    except KeyError:
        print(message.from_user.id, '- Chave não localizada (KeyError).')
    except NameError:
        print("NameError: name 'knownUsers' is not defined")


@bot.message_handler(commands=['sair'], content_types='text')
def new_message(message):
    sair(message)


@bot.message_handler(commands=['menu'], content_types='text')
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    mkp = markup.main_menu()
    txt = 'As suas ordens! :)\nO que gostaria de fazer?'
    bot.send_message(message.from_user.id, txt, reply_markup=mkp)
    markup.userStep[message.from_user.id] = 1


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 1)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    texto = message.text
    if texto == 'Ofertar Viagem':
        aux = 'Deseja ofertar para hoje ou agendar para outra data?'
        mkp = markup.day_menu()
        bot.send_message(message.from_user.id, aux, reply_markup=mkp)
        markup.userStep[message.from_user.id] = 2  # criar função para alterar em BD

    elif texto == 'Cancelar Viagem':
        ans = DataBase.search_byid(message.from_user.id, 'hora')
        mkp = markup.menu_from_list(ans, message.from_user.id)
        bot.send_message(message.from_user.id, 'Qual viagem gostaria de cancelar?', reply_markup=mkp)
        markup.userStep[message.from_user.id] = 3  # criar função para alterar em BD

    elif texto == 'Solicitar Carona':
        ans = DataBase.exctract_coluna('id')
        mkp = markup.menu_from_motor(ans, message.from_user.id)
        if len(ans) == 0:
            txt = 'Não existe ofertas de caronas no banco de dados.'
            bot.send_message(message.from_user.id, txt, reply_markup=removemkp)
            sair(message)
        else:
            nome = message.from_user.first_name.split(' ')
            nome = [x.lower() for x in nome]
            insere = markup.InserirCarona('_'.join(nome), message.from_user.id)
            motoristas = []
            for motorista in ans:
                if motorista not in motoristas: motoristas.append(motorista.title())
            bot.send_message(message.from_user.id, 'Com qual motorista?', reply_markup=mkp)
            markup.selection[message.from_user.id] = insere
            markup.userStep[message.from_user.id] = 4  # criar função para alterar em BD

    elif texto == 'Cancelar Carona':
        nome = message.from_user.first_name.split(' ')
        nome = [x.lower() for x in nome]
        cancela = markup.CancelarCarona('_'.join(nome), message.from_user.id)
        txt = 'Com quem você pegou carona?'
        ans = DataBase.exctract_coluna('id')
        motoristas = []
        for motorista in ans:
            if motorista not in motoristas: motoristas.append(motorista.title())
        mkp = markup.menu_from_motor(motoristas, message.from_user.id)
        bot.send_message(message.from_user.id, txt, reply_markup=mkp)
        markup.selection[message.from_user.id] = cancela
        markup.userStep[message.from_user.id] = 5  # criar função para alterar em BD

    elif texto == '/sair':
        sair(message)

    elif texto == 'Ver Ofertas':
        data = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
        ans = DataBase.simple_search(data)
        bot.send_message(message.from_user.id, ans, reply_markup=removemkp, parse_mode='HTML')
        del markup.userStep[message.from_user.id]  # criar função para alterar em BD

    elif texto == 'Pesquisar':
        txt = 'Voce pode pesquisar por origem, destino, nome do motorista, data ou hora.' \
              '\nLembre-se que você pode usar apenas uma palavra por pesquisa.'
        bot.send_message(message.from_user.id, txt, reply_markup=removemkp)
        markup.userStep[message.from_user.id] = 6  # criar função para alterar em BD

    else:
        txt = 'Use o teclado de opções:'
        mkp = markup.main_menu()
        bot.send_message(message.from_user.id, txt, reply_markup=mkp)


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 2)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    nome = message.from_user.first_name.split(' ')
    nome = [x.lower() for x in nome]
    oferta = markup.Oferta('_'.join(nome))
    if message.text == 'Hoje':
        data = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
        oferta.data = data
        bot.send_message(message.from_user.id, 'Origem da Viagem:')
        markup.ofertas[message.from_user.id] = oferta
        markup.userStep[message.from_user.id] = 22
    elif message.text == '/sair':
        sair(message)
    else:
        bot.send_chat_action(message.from_user.id, action='TYPING')
        txt = 'Digite uma data para agendamento (DD/MM):\nExemplo: 09/11'
        bot.send_message(message.from_user.id, txt, reply_markup=removemkp)
        markup.ofertas[message.from_user.id] = oferta
        markup.userStep[message.from_user.id] = 21


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 21)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    if message.text == '/sair':
        sair(message)
    else:
        oferta = markup.ofertas[message.from_user.id]
        data = message.text
        try:
            if data.split('/')[0].isdigit() and data.split('/')[1].isdigit() and len(data) == 5:
                oferta.data = data
                bot.send_message(message.from_user.id, 'Origem da viagem:')
                markup.ofertas[message.from_user.id] = oferta
                markup.userStep[message.from_user.id] = 22
            else:
                bot.reply_to(message, 'Oops! Data inválida. :(')
                txt = 'Digite uma data para agendamento (DD/MM):\nExemplo: 09/11'
                bot.send_message(message.from_user.id, txt)
        except:
            bot.reply_to(message, 'Oops! Data inválida. :(')
            txt = 'Digite uma data para agendamento (DD/MM):\nExemplo: 09/11'
            bot.send_message(message.from_user.id, txt)


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 22)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    if message.text == '/sair':
        sair(message)
    else:
        oferta = markup.ofertas[message.from_user.id]
        oferta.origem = message.text.lower()
        bot.send_message(message.from_user.id, 'Destino da viagem:')
        markup.ofertas[message.from_user.id] = oferta
        markup.userStep[message.from_user.id] = 23


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 23)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    if message.text == '/sair':
        sair(message)
    else:
        mkp = markup.hour_menu()
        oferta = markup.ofertas[message.from_user.id]
        oferta.destino = message.text.lower()
        if oferta.data != datetime.datetime.fromtimestamp(message.date).strftime('%d/%m)'):
            bot.send_message(message.from_user.id, 'Qual será o horário da viagem (HH:MM)?')
            markup.userStep[message.from_user.id] = 241
        else:
            bot.send_message(message.from_user.id, 'Esta saindo agora ou deseja agendar horário?', reply_markup=mkp)
            markup.ofertas[message.from_user.id] = oferta
            markup.userStep[message.from_user.id] = 24


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 24)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    oferta = markup.ofertas[message.from_user.id]
    if message.text == 'Saindo Agora':
        hora = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
        hora = hora.split(':')
        hora[1] = str(int(hora[1]) + 17)
        hora = ':'.join(hora)
        txt = 'Lembre-se de que os caroneiros terão 15 minutos de tolerância para solicitar carona.'
        bot.send_message(message.from_user.id, txt, reply_markup=removemkp)
        oferta.hora = hora
        bot.send_message(message.from_user.id, 'Quantas vagas você esta oferecendo?')
        markup.ofertas[message.from_user.id] = oferta
        markup.userStep[message.from_user.id] = 25
    elif message.text == 'Agendar Horário':
        bot.send_message(message.from_user.id, 'Horário de agendamento (HH:MM):', reply_markup=removemkp)
        markup.userStep[message.from_user.id] = 241
    elif message.text == '/sair':
        sair(message)
    else:
        mkp = markup.hour_menu()
        bot.send_message(message.from_user.id, 'Oops! Opção inválida\nEscolha uma das opções:', reply_markup=mkp)
        markup.userStep[message.from_user.id] = 24


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 241)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    oferta = markup.ofertas[message.from_user.id]
    if message.text == '/sair':
        sair(message)
    else:
        hora = message.text
        try:
            hora = hora.split(':')
            if hora[0].isdigit() and hora[1].isdigit():
                if 0 <= int(hora[0]) < 60 and 0 <= int(hora[1]) < 60:
                    oferta.hora = ':'.join(hora)
                    bot.send_message(message.from_user.id, 'Qauntas vagas está oferecendo?')
                    markup.ofertas[message.from_user.id] = oferta
                    markup.userStep[message.from_user.id] = 25
                else:
                    bot.reply_to(message, 'Oops! Tente digitar a hora novamente:')
            else:
                bot.reply_to(message, 'Oops! Respeite o formato indicado.\n Tente novamente (HH:MM):')
        except:
            bot.reply_to(message, 'Oops! Tente digitar novamente (HH:MM):')


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 25)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    oferta = markup.ofertas[message.from_user.id]
    if message.text == '/sair':
        sair(message)
    else:
        vagas = message.text
        if vagas.isdigit():
            oferta.vagas = vagas
            bot.send_message(message.from_user.id, 'Valor da passagem (direto):', reply_markup=removemkp)
            markup.ofertas[message.from_user.id] = oferta
            markup.userStep[message.from_user.id] = 26
        else:
            bot.reply_to(message, 'Oops! Opção inválida.\nDigite apenas números.')


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 26)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    oferta = markup.ofertas[message.from_user.id]
    try:
        if message.text == '/sair':
            sair(message)
        else:
            valor1 = float(message.text.replace(',', '.'))
            oferta.valor1 = valor1
            bot.send_message(message.from_user.id, 'Valor da passagem (baldeação):')
            markup.ofertas[message.from_user.id] = oferta
            markup.userStep[message.from_user.id] = 27
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.reply_to(message, 'Oops! Digite apenas números separados por vírgula ou ponto (EX. 7,00):')


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 27)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    oferta = markup.ofertas[message.from_user.id]
    try:
        if message.text == '/sair':
            sair(message)
        else:
            valor2 = float(message.text.replace(',', '.'))
            oferta.valor2 = valor2
            ans = DataBase.insert_table(oferta.data, oferta.motorista, oferta.origem, oferta.destino,
                                  oferta.hora, oferta.vagas, oferta.valor1, oferta.valor2, message.from_user.id)
            print('InsertDataBase ?', ans)
            bot.send_message(message.from_user.id, 'Sua oferta foi adicionada ao banco de dados.')
            txt = '{} adincionou uma nova oferta de viagem. :)'.format(oferta.motorista.title().replace('_', " "))
            bot.send_message(group_id, txt)
            sair(message)
            print(markup.ofertas, markup.userStep)
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.reply_to(message, 'Oops! Digite apenas números separados por vírgula ou ponto (EX. 7,00):')


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 3)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    try:
        if message.text == '/sair':
            sair(message)
        else:
            for n in range(markup.qtd_bt[message.from_user.id]):
                txt = message.text.split(' ')
                if int(txt[0][7]) == (n+1):  # Se opção(botao n) == n:
                    bot.send_chat_action(group_id, action='TYPING')
                    print('Enviando id {} e hora {}'.format(message.from_user.id, txt[1]))
                    ans = DataBase.delet_info_byid(message.from_user.id, txt[1])
                    print('delete_info_ans?', ans)
                    bot.send_message(message.from_user.id, 'Viagem cancelada!')
                    bot.send_message(group_id, ans)
                    sair(message)
                    break
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.from_user.id, 'Oops!\nParece que você não tem viagens ofertadas para excluir.')
        sair(message)


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 4)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    motoristas = markup.motoristas[message.from_user.id]
    insere = markup.selection[message.from_user.id]
    escolha = message.text
    insere.motorista = escolha
    if escolha == '/sair':
        sair(message)
    elif escolha in motoristas:
        ans = DataBase.exctract_coluna('data')
        datas = []
        for data in ans:
            if data not in datas: datas.append(data)
        mkp = markup.menu_from_motor(datas, message.from_user.id)
        txt = 'Escolha a data agendada para a viagem:'
        bot.send_message(message.from_user.id, txt, reply_markup=mkp)
        markup.selection[message.from_user.id] = insere
        markup.userStep[message.from_user.id] = 41


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 41)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    insere = markup.selection[message.from_user.id]
    insere.data = message.text
    print('Enviando:', insere.motorista, insere.data)
    ans = DataBase.extract_hora(insere.motorista, insere.data)
    mkp = markup.menu_from_motor(ans, message.from_user.id)
    if message.text == '/sair':
        sair(message)
    else:
        txt = 'Qual horário da viagem?'
        bot.send_message(message.from_user.id, txt, reply_markup=mkp)
        markup.selection[message.from_user.id] = insere
        markup.userStep[message.from_user.id] = 42


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 42)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    insere = markup.selection[message.from_user.id]
    horarios = markup.motoristas[message.from_user.id]
    print('horarios?', horarios)
    try:
        if message.text == '/sair':
            sair(message)
        else:
            for hora in range(len(horarios)):
                if message.text == horarios[hora]:
                    insere.hora = horarios[hora]
                    ans = DataBase.insert_carona(insere.motorista, insere.data,
                                             insere.hora, insere.passageiro, insere.pass_id)
                    if ans == 0:
                        txt = 'Não existe vaga ou viagem para o horário indicado.\nDigite menu para tentar novamente.'
                        bot.send_message(message.from_user.id, txt, reply_markup=removemkp)
                    elif ans == -1:
                        bot.send_message(message.from_user.id, msg_error)
                    else:
                        bot.send_chat_action(group_id, action='TYPING')
                        bot.send_message(group_id, ans)
                        bot.send_message(message.from_user.id, 'Tudo certo! :)', reply_markup=removemkp)
                        sair(message)
                else:
                    bot.send_message(message.from_user.id, msg_error, reply_markup=removemkp)
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.from_user.id, msg_error)
        sair(message)



@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 5)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    motoristas = markup.motoristas[message.from_user.id]
    cancela = markup.selection[message.from_user.id]
    escolha = message.text
    if escolha == '/sair':
        sair(message)
    elif escolha in motoristas:
        cancela.motorista = escolha
        ans = DataBase.exctract_coluna('data')
        datas = []
        for data in ans:
            if data not in datas: datas.append(data)

        mkp = markup.menu_from_motor(datas, message.from_user.id)
        txt = 'Escolha a data agendada para a viagem:'
        bot.send_message(message.from_user.id, txt, reply_markup=mkp)
        markup.selection[message.from_user.id] = cancela
        markup.userStep[message.from_user.id] = 51


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 51)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    cancela = markup.selection[message.from_user.id]
    cancela.data = message.text
    print('Enviando:', cancela.motorista, cancela.data)
    ans = DataBase.extract_hora(cancela.motorista, cancela.data)
    mkp = markup.menu_from_motor(ans, message.from_user.id)
    if message.text == '/sair':
        sair(message)
    else:
        txt = 'Digite o horário agendado para esta viagem (HH:MM):'
        bot.send_message(message.from_user.id, txt, reply_markup=mkp)
        markup.selection[message.from_user.id] = cancela
        markup.userStep[message.from_user.id] = 52


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 52)
def new_markup_message(message):
    bot.send_chat_action(message.from_user.id, action='TYPING')
    cancela = markup.selection[message.from_user.id]
    horarios = markup.motoristas[message.from_user.id]
    print('horarios?', horarios)
    try:
        if message.text == '/sair':
            sair(message)
        else:
            for hora in range(len(horarios)):
                if message.text == horarios[hora]:
                    cancela.hora = horarios[hora]
                    ans = DataBase.cancel_carona(cancela.passageiro, cancela.pass_id,
                                                 cancela.motorista, cancela.data, cancela.hora)

                    if ans == 0:
                        bot.send_message(message.from_user.id, 'Ooops!\nVoce não faz parte desta carona.')
                        sair(message)
                    elif ans == -1:
                        bot.send_message(message.from_user.id, msg_error)
                        sair(message)
                    else:
                        bot.send_message(group_id, ans)
                        bot.send_message(message.from_user.id, 'Carona Cancelada!')
                        sair(message)
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.from_user.id, msg_error)
        sair(message)


@bot.message_handler(func=lambda message: markup.get_user_step(message.from_user.id) == 6)
def new_markup_message(message):
    if message.text == '/sair':
        sair(message)
    else:
        bot.send_chat_action(message.from_user.id, action='TYPING')
        date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
        DataBase.clean_table(date)
        palavra = message.text
        ans = DataBase.simple_search(palavra)
        bot.send_message(message.from_user.id, ans, parse_mode='HTML')
        sair(message)


@bot.message_handler(commands=['carona'], content_types='text')
def new_message(message):
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    try:
        texto = (message.text.split(maxsplit=1)[1].split())
        texto = [texto[x].lower() for x in range(len(texto))]
        if len(texto) == 2:
            date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
            motorista, hora = texto[0], texto[1]
            print(motorista, date, hora)
        elif len(texto) == 3:
            date, motorista, hora = texto[0], texto[1], texto[2]
        else:
            bot.send_message(message.from_user.id, 'Olá! :}\nDigite ou clique em /menu para começar.')
        if DataBase.check_value(motorista, date):
            ans = DataBase.insert_carona(motorista, date, hora, name, message.from_user.id)
            if ans == 0:
                txt = 'Oops! Creio que não existem mais vagas disponíveis para esta viagem.'
                bot.send_message(message.from_user.id, txt)
            elif ans == -1:
                bot.send_message(message.from_user.id, msg_error)
            else:
                if message.chat.id == group_id:
                    bot.send_message(message.chat.id, ans)
                else:
                    bot.send_message(message.chat.id, ans)
                    bot.send_message(group_id, ans)
        else:
            bot.send_message(message.chat.id, 'Não localizamos oferta de {} para {}. :('.format(motorista, date))
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.chat.id, msg_error)


@bot.message_handler(commands=['cancela'], content_types='text')
def new_message(message):
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    texto = message.text.split(maxsplit=1)[1].split()
    texto = [x.lower() for x in texto]
    try:
        if len(texto) == 2:
            motorista, hora = texto[0], texto[1]
            date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
            ans = DataBase.cancel_carona(name, message.from_user.id, motorista, date, hora)
        elif len(texto) == 3:
            motorista, date, hora = texto[0], texto[1], texto[2]
            ans = DataBase.cancel_carona(name, message.from_user.id, motorista, date, hora)
        else:
            bot.send_message(message.from_user.id, 'Olá! :}\nDigite ou clique em /menu para começar.')
        if message.chat.id == group_id:
            bot.send_message(message.chat.id, ans)
        else:
            bot.send_message(group_id, ans)
            bot.send_message(message.chat.id, ans)
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.chat.id, msg_error)


@bot.message_handler(commands=['excluir'], content_types='text')
def new_message(message):
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    try:
        texto = message.text.split(maxsplit=1)[1].split()
        if len(texto) == 1:
            date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
            hora = texto[0]
        elif len(texto) == 2:
            date, hora = texto[0], texto[1]
        else:
            bot.send_message(message.from_user.id, 'Olá! :}\nDigite ou clique em /menu para começar.')
        ans = DataBase.delet_info(name, date, hora)
        if message.chat.id == group_id:
            bot.send_message(message.chat.id, ans, parse_mode='HTML')
        else:
            bot.send_message(group_id, ans, parse_mode='HTML')
            bot.send_message(message.chat.id, ans, parse_mode='HTML')
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.chat.id, msg_error)



@bot.message_handler(commands=['ofertar'], content_types='text')
def new_message(message):
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    try:
        texto = (message.text.split(maxsplit=1)[1].split())
        texto = [x.lower() for x in texto]
        if len(texto) == 7:
            texto[4], texto[5], texto[6] = int(texto[4]), float(texto[5].replace(',', '.')), \
                                           float(texto[6].replace(',', '.'))
            date, ida, volta, hour, vagas, v1, v2 = tuple(texto)
        elif len(texto) == 0:
            bot.send_message(message.from_user.id, 'Olá! :}\nDigite ou clique em /menu para começar.')
        else:
            texto[3], texto[4], texto[5] = int(texto[3]), float(texto[4].replace(',', '.')), \
                                           float(texto[5].replace(',', '.'))
            date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
            ida, volta, hour, vagas, v1, v2 = tuple(texto)
        DataBase.insert_table(date, name, ida, volta, hour, vagas, v1, v2, message.from_user.id)
        if message.chat.id > 0:
            bot.send_message(message.chat.id, '{}, sua oferta foi adicionada! :)'.format(name.title()))
        else:
            txt = '{} adicionou uma nova oferta de carona! :)'
            bot.send_message(group_id, txt.format(name.title()))
            bot.send_message(message.chat.id, '{}, sua oferta foi adicionada! :)'.format(name.title()))
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.chat.id, msg_error)


@bot.message_handler(commands=['buscar'], content_types='text')
def new_message(message):
    date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
    DataBase.clean_table(date)
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    try:
        texto = tuple(message.text.split(maxsplit=1)[1].split())
        if len(texto) == 2:
            ida, volta = texto
            ans = DataBase.search_table(ida, volta, date)
        elif len(texto) == 1:
            palavra = texto[0]
            ans = DataBase.simple_search(palavra)
        else:
            bot.send_message(message.from_user.id, 'Olá! :}\nDigite ou clique em /menu para começar.')
        txt = '{}, aqui esta o resultado da sua busca:'
        bot.send_message(message.chat.id, txt.format(name.title()) + ans, parse_mode='HTML')
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.chat.id, msg_error)


@bot.message_handler(commands=['alterar'], content_types='text')  # testar
def new_message(message):
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    try:
        texto = tuple(message.text.split(maxsplit=1)[1].split())
        texto = [x.lower() for x in texto]
        date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
        if len(texto) == 0:
            bot.send_message(message.from_user.id, 'Olá! :}\nDigite ou clique em /menu para começar.')
        elif DataBase.check_value(name, date):
            if len(texto) == 5:
                origem, destino, date, opcao, valor = texto[0], texto[1], texto[2], texto[3], texto[4]
                selecao = DataBase.select_date_destiny(origem, destino, date)
            else:
                origem, destino, opcao, valor = texto[0], texto[1], texto[2], texto[3]
                selecao = DataBase.select_date_destiny(origem, destino, date)
            ans = DataBase.change_table(opcao, valor, selecao[0][2], selecao[0][3], selecao[0][0])
            if message.chat.id == group_id:
                bot.send_message(message.chat.id, ans)
            else:
                txt = '{} fez uma nova alteração em uma oferta existente ({}).'
                bot.send_message(group_id, txt.format(name.title(), opcao))
        else:
            ans = '{}, somente o motorista pode alterar/excluir viagem'.format(name.title())
            bot.send_message(message.chat.id, ans)
    except NameError:
        print("NameError: name 'knownUsers' is not defined")
    except:
        bot.send_message(message.chat.id, msg_error)


@bot.message_handler(commands=['limpar'], content_types='text')
def new_message(message):
    date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
    ans = DataBase.clean_table(date)
    bot.send_message(message.chat.id, ans)


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60, interval=0)
    except:
        traceback_error_string = traceback.format_exc()
        with open("Error.Log", "a") as myfile:
            myfile.write("\r\n\r\n" + time.strftime(
                "%c") + "\r\n<<ERROR polling>>\r\n" + traceback_error_string + "\r\n<<ERROR polling>>")
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


if __name__ == '__main__':
    print("executando...")
    DataBase.create_table()
    telegram_polling()
