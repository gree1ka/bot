import requests
import telebot
from bs4 import BeautifulSoup
import datetime
from telebot import types

bot = telebot.TeleBot('5251329150:AAGUeWVWgRYEpbXI2GO7hLyfIk_GGUvpNUg')


def bitcoin():
    url = 'https://api.bitaps.com/market/v1/ticker/btcusdt'
    return(requests.get(url=url).json()['data']['last'])


def get_text(month = datetime.date.today().month   , day = datetime.date.today().day):
    url = f'https://www.sut.ru/studentu/raspisanie/raspisanie-zanyatiy-studentov-ochnoy-i-vecherney-form-obucheniya?group=54963&date=2022-{int(month)}-{int(day)}' #страница расписания нашей группы с нынешней датой
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' #что бы удалось спарсить, иначе за бота принимает система
    code = requests.get(url, headers={'User-Agent': user_agent}) #получаем код сайта
    soup = BeautifulSoup(code.text)     #создаем переменную с которой будем искать
    return(soup)


def get_raspisanie_from_text(soup, weekday = int(datetime.date.today().weekday()) + 1):
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


@bot.message_handler(commands=['rasp'])
def rasp(message):
    day = (message.text.split())[1]
    month = (message.text.split())[3]
    weekday = (message.text.split())[2]
    date_massive = []
    raspisanie_massive = []
    vremya_par = ['1\n9:00 - 10:35\n', '2\n10:45 - 12:20\n', '3\n13:00 - 14:35\n', '4\n14:45 - 16:20\n', '5\n16:30 - 18:05\n', '6\n18:15 - 19:50\n'] #это что бы время пар не парсить, просто отедльно

    url = f'https://www.sut.ru/studentu/raspisanie/raspisanie-zanyatiy-studentov-ochnoy-i-vecherney-form-obucheniya?group=54963&date=2022-{int(month)}-{int(day)}' #страница расписания нашей группы с нынешней датой
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' #что бы удалось спарсить, иначе за бота принимает система
    code = requests.get(url, headers={'User-Agent': user_agent}) #получаем код сайта
    soup = BeautifulSoup(code.text)     #создаем переменную с которой будем искать
    tables=soup.find_all('div', {'class': f'vt239 rasp-day rasp-day{int(weekday)}'})
    for ind, n in enumerate(tables):
        n = n.text.strip()    #нужно что бы получить чисто текст, без всяких дивов и тд
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
        bot.send_message(message.chat.id, 'Занятий нет, идём пить пиво!\nhttps://krasnoeibeloe.ru/\nhttps://yandex.ru/maps?rtext=59.902821%2C30.489175~60.049597%2C30.426361&rtt=mt')
        
        return
    bot.send_message(message.chat.id, res)


@bot.message_handler(commands=['start'])
def start(m, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Расписание на неделю")
    btn2 = types.KeyboardButton("Расписание на сегодня")
    markup.add(btn1, btn2)
    bot.send_message(m.chat.id, 'Я работаю, напиши что - нибудь...', reply_markup=markup)


@bot.message_handler(commands=['btc'])
def btc(message):
    bot.send_message(message.chat.id, bitcoin())


@bot.message_handler(commands=['week'])
def week(message):
    week_days = ['*Понедельник*', '*Вторник*', '*Среда*', '*Четверг*', '*Пятница*', '*Суббота*']
    text = get_text()
    for i in range(1, 7):
        res = get_raspisanie_from_text(text, i)
        if 'Занятий нет' not in res and 'Военная подготовка' not in res:
            bot.send_message(message.chat.id, week_days[i-1] + '\n\n' + res, parse_mode='MarkDown')
    return


@bot.message_handler(content_types=['text'])
def knopki(message):
        if message.text == 'Расписание на неделю':
            week(message)
        elif message.text == 'Расписание на сегодня':
            bot.send_message(message.chat.id, get_raspisanie_from_text(get_text()))


bot.polling(non_stop=True, interval=0)