import sqlite3
import urllib3
import hashlib
import telebot
from telebot import types
import qrcode
import os
from Crypto.Cipher import AES
from secrets import token_bytes
from datetime import datetime
from mimesis import Person
from mimesis.locales import Locale
import base64
import codecs

database_name = 'database.db'
token = "5586853833:AAFCfHp2dgZ1cQ6np2AzMErX4luwgZFlCxs"
folder_way = "/Users/andrey/PycharmProjects/pythonProject44/"
key = b'\x82^\r\x01\xed\x97\xeb\x1b|\x15\x85\xb1\xe3.\xc5\xcfH09\xf7z\xcap\x07\xfa\x0b\xcb\x80\xba/\xadN'

http = urllib3.PoolManager()
bot = telebot.TeleBot(token)
person = Person(locale=Locale.RU)
qr = qrcode.QRCode()


def encrypt(msg):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(msg.encode('ascii'))

    return nonce, ciphertext, tag


def decrypt(nonce, ciphertext, tag):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
        return plaintext.decode('ascii')
    except:
        return False


def getName(nick):
    con = sqlite3.connect(database_name)
    cursor = con.cursor()
    con.commit()
    cursor.execute(f"SELECT FIO FROM pass_holders where TG_nick='{nick}'")
    ans = cursor.fetchall()
    cursor.close()
    return ans


def collect_id(nick):
    con = sqlite3.connect(database_name)
    cursor = con.cursor()
    con.commit()
    data = ''
    cursor.execute(f"SELECT id FROM pass_holders where TG_nick='{nick}'")
    data += str(cursor.fetchall()[0][0])
    cursor.close()
    return data


@bot.message_handler(commands=['start'])
def start_message(message):
    nick = message.from_user.username
    name = getName(nick)[0][0]
    bot.send_message(message.chat.id, "Приветствую, " + name.split()[0])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Войти")
    button2 = types.KeyboardButton("Выйти")
    markup.add(button1, button2)
    bot.send_message(message.chat.id, 'Что хотите сделать?', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def main(message):
    if message.chat.type == 'private':
        time = str(datetime.now().time())[:8]
        id = collect_id(message.from_user.username)

        if message.text == "Войти":
            con = sqlite3.connect(database_name)
            cursor = con.cursor()
            con.commit()
            cursor.execute(f"DELETE from pass WHERE Id='{id}'")
            con.commit()
            l = str(id) + " in " + time
            n, c, t = encrypt(l)
            code = str(n) + "," + str(c) + "," + str(t)
            qr = qrcode.make(code)
            qr.save(f"{message.chat.id}.png")
            bot.send_photo(message.chat.id, open(f"{message.chat.id}.png", "rb"), caption="Ваш QR-код для входа")
            way = str(folder_way) + f"{message.chat.id}.png"
            image = ''
            dt = (id, \
                  image, \
                  'in')
            cursor.execute(f"INSERT INTO pass VALUES(?,?,?)", dt)
            con.commit()
            os.remove(way)
            cursor.close()

        elif message.text == "Выйти":
            con = sqlite3.connect(database_name)
            cursor = con.cursor()
            con.commit()
            cursor.execute(f"DELETE from pass WHERE Id='{id}'")
            con.commit()

            l = str(id) + " out " + time
            n, c, t = encrypt(l)
            code = str(n) + " " + str(c) + " " + str(t)
            qr = qrcode.make(code)
            qr.save(f"{message.chat.id}.png")
            bot.send_photo(message.chat.id, open(f"{message.chat.id}.png", "rb"), caption="Ваш QR-код для выхода")
            way = str(folder_way) + f"{message.chat.id}.png"
            image = ''
            dt = (id, \
                  image, \
                  'out')
            cursor.execute(f"INSERT INTO pass VALUES(?,?,?)", dt)
            con.commit()
            cursor.close()
            os.remove(way)
        else:
            bot.send_message(message.chat.id, "Я такого не умею")
    else:
        pass


def create_tables():
    con = sqlite3.connect(database_name)
    cursor = con.cursor()
    con.commit()
    command = '''
    CREATE TABLE IF NOT EXISTS pass(Id INT,
                                    QR_code_input TEXT,
                                    QR_code_output TEXT,
                                    Validity BIT)
    '''
    cursor.execute(command)
    command = '''
        CREATE TABLE IF NOT EXISTS pass_holders(Id INT,
                                               FIO TEXT,
                                               Photo BLOB,
                                               NUM_phone TEXT,
                                               TG_nick TEXT)
        '''
    cursor.execute(command)
    command = '''
        CREATE TABLE IF NOT EXISTS type_of_pass_holders(Id INT,
                                                        Name_type_of_pass_holders TEXT)
        '''
    cursor.execute(command)
    command = '''
        CREATE TABLE IF NOT EXISTS divisions(Id INT,
                                             Name_divisions TEXT)
        '''
    cursor.execute(command)
    command = '''
        CREATE TABLE IF NOT EXISTS pass_log(Id INT,
                                            Data_and_time_log TEXT,
                                            Direction TEXT)
        '''
    cursor.execute(command)
    command = '''
        CREATE TABLE IF NOT EXISTS rooms(Id_room INT,
                                        Num_room INT,
                                        Name_room TEXT)
        '''
    cursor.execute(command)
    command = '''
            CREATE TABLE IF NOT EXISTS checkpoint(Id INT,
                                                  Name_checkpoint TEXT)
        '''
    cursor.execute(command)
    command = '''
                CREATE TABLE IF NOT EXISTS change(Id INT,
                                                  Num_change INT)
            '''
    cursor.execute(command)
    command = '''
                CREATE TABLE IF NOT EXISTS employee(Id INT,
                                                    FIO TEXT,
                                                    Login TEXT,
                                                    Password TEXT)
            '''
    cursor.execute(command)
    command = '''
                CREATE TABLE IF NOT EXISTS time_event_log(Id INT,
                                                          Name_event TEXT,
                                                          Time_event TEXT,
                                                          Cause TEXT)
                                                          
            '''
    cursor.execute(command)
    con.commit()
    cursor.close()


def generate_pass_holders(n):
    con = sqlite3.connect(database_name)
    cursor = con.cursor()
    con.commit()
    for i in range(n):
        FIO = person.full_name().replace("'", '')
        byte_name = bytearray(FIO + str(datetime.now())[-1], encoding='utf-8')
        NUM_phone = person.telephone(mask='+7-9##-###-##-##')
        Photo = ''
        TG_nick = person.username()
        dt = (hashlib.md5(byte_name).hexdigest(), \
              FIO, \
              Photo, \
              NUM_phone, \
              TG_nick)
        cursor.execute(f"INSERT INTO pass_holders VALUES(?,?,?,?,?)", dt)
        con.commit()
        cursor.close()


def add_me():
    con = sqlite3.connect(database_name)
    cursor = con.cursor()
    con.commit()
    FIO = "Андрей Шмунк"
    byte_name = bytearray(FIO + str(datetime.now())[-1], encoding='utf-8')
    NUM_phone = '+7-913-018-40-14'
    Photo = ''
    TG_nick = "Andrey_Shmunk"
    dt = (hashlib.md5(byte_name).hexdigest(), \
          FIO, \
          Photo, \
          NUM_phone, \
          TG_nick)
    cursor.execute(f"INSERT INTO pass_holders VALUES(?,?,?,?,?)", dt)
    con.commit()
    cursor.close()


bot.infinity_polling()
