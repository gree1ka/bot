import requests
import telebot
from bs4 import BeautifulSoup
from telebot import types
from pendulum import now, date


bot = telebot.TeleBot('5251329150:AAGUeWVWgRYEpbXI2GO7hLyfIk_GGUvpNUg')


def bitcoin():
    url = 'https://api.bitaps.com/market/v1/ticker/btcusdt'
    return(requests.get(url=url).json()['data']['last'])


def get_text(month = now().month , day = now().day): #Делаем так что бы ставился понедельник
    url = f'https://www.sut.ru/studentu/raspisanie/raspisanie-zanyatiy-studentov-ochnoy-i-vecherney-form-obucheniya?group=54963&date=2022-{int(month)}-{int(day)}' #страница расписания нашей группы с нынешней датой
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' #что бы удалось спарсить, иначе за бота принимает система
    code = requests.get(url, headers={'User-Agent': user_agent}) #получаем код сайта
    soup = BeautifulSoup(code.text)     #создаем переменную с которой будем искать
    return(soup)


def get_raspisanie_from_text(soup, weekday = int(now().weekday() + 1)):
    date_massive = []
    raspisanie_massive = []
    vremya_par = ['1\n9:00 - 10:35\n', '2\n10:45 - 12:20\n', '3\n13:00 - 14:35\n', '4\n14:45 - 16:20\n', '5\n16:30 - 18:05\n', '6\n18:15 - 19:50\n']
    tables=soup.find_all('div', {'class': f'vt239 rasp-day rasp-day{int(weekday)}'})
    for ind, n in enumerate(tables):
        n = n.text.strip()
        if n != '':
            n = list(map(lambda x: x.strip(), n.split('\n')))
            while '' in n:
                n.remove('')
            n = '\n'.join(n)
            date_massive.append(vremya_par[ind])
            raspisanie_massive.append(n)
    res = str()
    for i in range(len(date_massive)):
        res += date_massive[i] + raspisanie_massive[i] + '\n\n'
    if res == '':
        return('Занятий нет, идём пить пиво!\nhttps://krasnoeibeloe.ru/\nhttps://yandex.ru/maps?rtext=59.902821%2C30.489175~60.049597%2C30.426361&rtt=mt')
    return(res)


@bot.message_handler(commands=['start'])
def start(m, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Эта неделя")
    btn2 = types.KeyboardButton("Сегодня")
    btn3 = types.KeyboardButton('Следующая неделя')
    btn4 = types.KeyboardButton('Своя дата')
    btn5 = types.KeyboardButton('Курс Bitcion')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(m.chat.id, 'Я работаю, напиши что - нибудь...', reply_markup=markup)


@bot.message_handler(commands=['btc'])
def btc(message):
    bot.send_message(message.chat.id, bitcoin())


def week(message, needed_date=now().add(days=-now().weekday()).date()):
    week_days = ['*Понедельник*', '*Вторник*', '*Среда*', '*Четверг*', '*Пятница*', '*Суббота*']
    text = get_text(needed_date.month, needed_date.day)
    for i in range(1, 7):
        res = get_raspisanie_from_text(text, i)
        if 'Занятий нет' not in res and 'Военная подготовка' not in res:
            bot.send_message(message.chat.id, week_days[i-1] + f'* - {needed_date.add(days=i-1).month:02}.{needed_date.add(days=i-1).day:02}*' + '\n\n' + res, parse_mode='MarkDown')
    return


def custom_date(message):
    day, month = message.text.split('.')
    bot.send_message(message.chat.id, get_raspisanie_from_text(get_text(month, day), weekday=date(now().year,int(month), int(day)).weekday()+1))


@bot.message_handler(content_types=['text'])
def knopki(message):
        if message.text == 'Эта неделя':
            week(message)

        elif message.text == 'Сегодня':
            bot.send_message(message.chat.id, get_raspisanie_from_text(get_text()))
            
        elif message.text == 'Следующая неделя':
            week(message, now().add(days=7 - now().weekday()))  #Тот день окажется всегда понедельником

        elif message.text == 'Курс Bitcion':
            bot.send_message(message.chat.id, str(bitcoin()) + '$')

        elif message.text == 'Своя дата':
            bot.register_next_step_handler(message, custom_date)




bot.polling(non_stop=True, interval=0)