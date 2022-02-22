import configparser
import json
import csv
from telethon import TelegramClient, connection
# для корректного переноса времени сообщений в json
from datetime import date, datetime
# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd
import xlsxwriter
import xlwt
# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

client = TelegramClient(
    'anon', api_id, api_hash)

client.start()

async def dump_all_messages(channel):

    offset_msg = 0  # номер записи, с которой начинается считывание
    limit_msg = 100  # максимальное число записей, передаваемых за один раз

    all_messages = []  # список всех сообщений
    all_datas = []  # список всех дат
    all_all = []
    total_messages = 0
    total_count_limit = 50  # поменяйте это значение, если вам нужны не все сообщения

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
        "дата": all_datas
    }
    z = pd.DataFrame(di)
    z['дата'] = all_datas
    z['дата'] = z['дата'].apply(lambda a: pd.to_datetime(a).date())
    z.to_excel("file_name.xlsx", index=False)


async def main():
    url = input("Введите ссылку на канал или чат: ")
    channel = await client.get_entity(url)

    await dump_all_messages(channel)



with client:
    client.loop.run_until_complete(main())
