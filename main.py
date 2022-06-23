import configparser
import json
from telethon import TelegramClient, connection
# для корректного переноса времени сообщений в json
from datetime import date, datetime
# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd

# ссылка https://proglib.io/p/pishem-prostoy-grabber-dlya-telegram-chatov-na-python-2019-11-06

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

client = TelegramClient(
    'anon', api_id, api_hash)

client.start()

async def dump_all_messages(channel, url):
    if url== 'https://t.me/trueresearch':
        channel_name = 'Русский research'
    if url== 'https://t.me/katorga_sci':
        channel_name = 'Научная каторга'
    if url== 'https://t.me/scienpolicy':
        channel_name = 'Научно-образовательная политика'
    if url=='https://t.me/ivoryzoo':
        channel_name = 'Зоопарк из слоновой кости'
    if url=='https://t.me/rasofficial':
        channel_name = 'Российская академия наук'
    if url=='https://t.me/RU_Biology':
        channel_name = 'RU_Biology'
    # if url == 'https://t.me/+tqDAn2TMFHU0ZWMy':
    #     channel_name = 'Научная Коммуна'  ссылка бракованная
    if url == 'https://t.me/minobrnaukiofficial':
        channel_name = 'Минобрнауки России'
    # if url == 'https://t.me/interesting_but_true':
    #     channel_name = 'Высшее образование' канал загнулся
    offset_msg = 0  # номер записи, с которой начинается считывание
    limit_msg = 100  # максимальное число записей, передаваемых за один раз

    all_messages = []  # список всех сообщений
    all_datas = []  # список всех дат
    all_all = []
    total_messages = 0
    total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

    class DateTimeEncoder(json.JSONEncoder):

        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages


        try:
            for message in messages:
                if message.to_dict()['message'] != "":
                    all_messages.append(message.to_dict()['message'])
                    all_datas.append(message.to_dict()['date'])
                    all_all.append(message.to_dict())
        except:
            print('ошибка')
        else:
            print('вроде ок')
        finally:
            print('всё')

        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)

        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    # формирование json файла
    with open('channel_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(all_all, outfile, ensure_ascii=False, cls=DateTimeEncoder)
    # формирование exel файла
    di = {
        "новости": all_messages,
        "дата": all_datas,
        "канал" : channel_name
    }
    z = pd.DataFrame(di)
    z['дата'] = all_datas
    z['дата'] = z['дата'].apply(lambda a: pd.to_datetime(a).date())
    z.to_excel("data.xlsx", index=False)


async def main():
    url = input("Введите ссылку на канал или чат: ")
    channel = await client.get_entity(url)

    await dump_all_messages(channel,url)

with client:
    client.loop.run_until_complete(main())
