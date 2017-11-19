import telebot
import DataBase
import datetime
import time


bot = telebot.TeleBot('501268361:AAHp056OeZVAC3oE2dQtjMKyDucPHfz0Ya0')
msg_error = 'Oops! Algo de errado não está certo.\nUse /help ou /ajuda para consulta de comandos.'


@bot.message_handler(commands=['ajuda', 'help'], content_types='text')
def new_message(message):
    arquivo, txt = open('help_command.txt','r'), ''
    for linha in arquivo.readlines(): txt += linha
    bot.send_message(message.chat.id, txt)


@bot.message_handler(commands=['start'], content_types='text')
def new_message(message):
    name = message.from_user.first_name
    txt = 'Bem-vindo(a) {} ! :)\nDigite /ajuda ou /help para me chamar.'
    bot.send_message(message.chat.id, txt.format(name))


@bot.message_handler(commands=['carona'], content_types='text')
def new_message(message):
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    texto = (message.text.split(maxsplit=1)[1].split())
    texto = [texto[x].lower() for x in range(len(texto))]
    try:
        if len(texto) == 2:
            date = datetime.datetime.fromtimestamp(message.date).strftime('%m/%d')
            motorista, hora = texto[0], texto[1]
        else:
            date, motorista, hora = texto[0], texto[1], texto[2]
        if DataBase.check_value(motorista, date):
            ans = DataBase.insert_carona(motorista, date, hora, name)
            bot.message_handler(message.chat.id, ans)
        else:
            bot.message_handler(message.chat.id, 'Não localizamos oferta de {} para {}. :('.format(motorista, date))
    except:
        bot.message_handler(message.chat.id, msg_error)


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
            ans = DataBase.cancel_carona(name, motorista, date, hora)
        else:
            motorista, date, hora = texto[0], texto[1], texto[2]
            ans = DataBase.cancel_carona(name, motorista, date, hora)
        bot.send_message(message.chat.id, ans)
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
        else:
            date, hora = texto[0], texto[1]
        ans = DataBase.delet_info(name, date, hora)
        bot.send_message(message.chat.id, ans)
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
            texto[4], texto[5], texto[6] = int(texto[4]), float(texto[5].replace(',','.')), \
                                           float(texto[6].replace(',','.'))
            date, ida, volta, hour, vagas, v1, v2 = tuple(texto)
        else:
            texto[3], texto[4], texto[5] = int(texto[3]), float(texto[4].replace(',', '.')), \
                                           float(texto[5].replace(',', '.'))
            date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
            ida, volta, hour, vagas, v1, v2 = tuple(texto)
        DataBase.insert_table(date, name, ida, volta, hour, vagas, v1, v2)
        bot.send_message(message.chat.id, '{}, sua oferta foi adicionada.'.format(name.title()))
    except:
        bot.send_message(message.chat.id, msg_error)


@bot.message_handler(commands=['buscar'], content_types='text')
def new_message(message):
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    try:
        texto = tuple(message.text.split(maxsplit=1)[1].split())
        date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
        if len(texto) == 2:
            ida, volta = texto
            ans = DataBase.search_table(ida, volta, date)
        else:
            palavra = texto[0]
            ans = DataBase.simple_search(palavra)
        bot.send_message(message.chat.id, '{}, aqui esta o resultado da sua busca:'.format(name.title()) + ans)
    except:
        bot.send_message(message.chat.id, msg_error)


@bot.message_handler(commands=['alterar'], content_types='text')
def new_message(message):
    name = message.from_user.first_name.split()
    name = [x.lower() for x in name]
    name = '_'.join(name)
    try:
        texto = tuple(message.text.split(maxsplit=1)[1].split())
        date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
        if DataBase.check_value(name, date):
            if len(texto) == 5:
                origem, destino, date, opcao, valor = texto[0], texto[1], texto[2], texto[3], texto[4]
                selecao = DataBase.select_date_destiny(origem, destino, date)
            else:
                origem, destino, opcao, valor = texto[0], texto[1], texto[2], texto[3]
                selecao = DataBase.select_date_destiny(origem, destino, date)
            ans = DataBase.change_table(opcao, valor, selecao[0][2], selecao[0][3], selecao[0][0])
            bot.send_message(message.chat.id, ans)
        else:
            ans = '{}, somente o motorista pode alterar/excluir viagem'.format(name.title())
            bot.send_message(message.chat.id, ans)
    except:
        bot.send_message(message.chat.id, msg_error)
        

@bot.message_handler(commands=['limpar'], content_types='text')
def new_message(message):
    date = datetime.datetime.fromtimestamp(message.date).strftime('%d/%m')
    ans = DataBase.clean_table(date)
    bot.send_message(message.chat.id, ans)


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        traceback_error_string=traceback.format_exc()
        with open("Error.Log", "a") as myfile:
            myfile.write("\r\n\r\n" + time.strftime("%c")+"\r\n<<ERROR polling>>\r\n"+ traceback_error_string + "\r\n<<ERROR polling>>")
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


if __name__ == '__main__':
    print("executando...")
    DataBase.create_table()
    telegram_polling()
