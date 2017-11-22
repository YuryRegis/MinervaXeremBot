from telebot import types

markuprmv = types.ReplyKeyboardHide()
motoristas = {}
selection = {}
ofertas = {}
userStep = {}
qtd_bt = {}
knowUsers = []


class Answer:
    def __init__(self, name):
        self.name = name
        self.ans1 = None


class InserirCarona:
    def __init__(self, name, id):
        self.passageiro = name
        self.pass_id = id
        self.motorista = None
        self.data = None
        self.hora = None


class CancelarCarona:
    def __init__(self, name, id):
        self.passageiro = name
        self.pass_id = id
        self.motorista = None
        self.data = None
        self.hora = None


class Oferta:
    def __init__(self, name):
        self.motorista = name
        self.data = None
        self.origem = None
        self.destino = None
        self.hora = None
        self.vagas = None
        self.valor1 = None
        self.valor2 = None
        self.caroneiros = ''


def add_know_users(user):
    if user not in knowUsers:
        knowUsers.append(user)
        userStep[user] = 0
        return True
    return False


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print("Novo usuário detectado")
        return 0


def main_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    bt1 = types.KeyboardButton('Ofertar Viagem')
    bt2 = types.KeyboardButton('Cancelar Viagem')
    bt3 = types.KeyboardButton('Solicitar Carona')
    bt4 = types.KeyboardButton('Cancelar Carona')
    bt5 = types.KeyboardButton('Ver Ofertas')
    bt6 = types.KeyboardButton('Pesquisar')
    bt7 = types.KeyboardButton('/sair')
    markup.row(bt1, bt2)
    markup.row(bt3, bt4)
    markup.row(bt5, bt6)
    markup.row(bt7)
    return markup


def menu_from_motor(lista, id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    motoristas[id] = lista
    print('motors?', motoristas)
    try:
        bts = []
        for nome in lista: bts.append(types.KeyboardButton(nome))
        for botao in bts: markup.row(botao)
        last_bt = types.KeyboardButton('/Sair')
        markup.row(last_bt)
        qtd_bt[id] = len(bts)
        print('qtd_bt?', qtd_bt[id])
        return markup
    except:
        return 0


def menu_from_list(lista, id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    try:
        buttons = []
        for n, nome in enumerate(lista):
            txt = 'Viagem_{}: '.format(n+1)
            buttons.append(types.KeyboardButton(txt + nome))
        for botao in buttons:
            markup.row(botao)
        last_bt = types.KeyboardButton('/sair')
        markup.row(last_bt)
        qtd_bt[id] = len(buttons)
        return markup
    except:
        return 0


def day_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    bt1 = types.KeyboardButton('Hoje')
    bt2 = types.KeyboardButton('Agendar Oferta')
    bt3 = types.KeyboardButton('/sair')
    markup.row(bt1)
    markup.row(bt2)
    markup.row(bt3)
    return markup


def hour_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    bt1 = types.KeyboardButton('Saindo Agora')
    bt2 = types.KeyboardButton('Agendar Horário')
    bt3 = types.KeyboardButton('/sair')
    markup.row(bt1)
    markup.row(bt2)
    markup.row(bt3)
    return markup
