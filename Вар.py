from aiogram import Bot, types, Dispatcher
from asyncio import run, get_event_loop, create_task, gather
from aiogram import F, Router, BaseMiddleware
from aiogram.fsm.state import default_state
from aiogram.types import Message, FSInputFile, \
KeyboardButton,ReplyKeyboardMarkup,TelegramObject, InputFile
from aiogram.types.input_text_message_content import InputTextMessageContent
from aiogram import Router, F
from aiogram.filters import Command, StateFilter, BaseFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionSender
import requests
import logging
from sqlite3 import connect
from math import ceil
from json import load, dump
from random import choice
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Callable, Awaitable, Any, Dict

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename="Ло.txt", filemode="w")

t = Bot('')
dp = Dispatcher(storage = MemoryStorage())
iam_token = "t1.9euelZqXkZuMisePnIyTkMyRyIqXze3rnpWakYmMzIzLnZaSk4uZjsqZzszl8_doFUNO-e9ZNkgE_d3z9yhEQE7571k2SAT9zef1656VmsuXzZPHjs2blYmRnMyOx4ud7_zF656VmsuXzZPHjs2blYmRnMyOx4udveuelZqcy8-Mm5SRmY3Ll5jHl8zPy7XehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.sOGqW0wvn7EyCc2DUOU9BmUT8K_oZJv3qkG8fzPvqnhkuQ5j4ZKZqXrG_kpnOLWLGNqre7wXLGg0O4s1Tt6QDA"
folder_id = ''

class N(StatesGroup):
    n = State()
    n1 = State()
    n2 = State()
    n3 = State()
    n4 = State()
    n5 = State()
    n6 = State()
    n7 = State()
    
class P(BaseFilter):
    async def __call__(self, message): 
        if str(message.from_user.id) in load(open("us.json", "r"))["Забанан"]:             
            return False
        return True

rout = Router()
rout.message.filter(P())

class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, apscheduler: AsyncIOScheduler):
        self.gavnulka = apscheduler

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message | AsyncIOScheduler,
        data: Dict[str, Any | AsyncIOScheduler],
    ) -> Any:
        data["apscheduler"] = self.gavnulka
        return await handler(event, data)

async def main():
    await t.delete_webhook(drop_pending_updates=True)
    dp.include_router(rout)
    scheduler = AsyncIOScheduler()
    scheduler.start()
    dp.update.middleware(SchedulerMiddleware(apscheduler=scheduler),)
    await dp.start_polling(t)

def count_tokens(g):
    # Подсчитывает количество токенов в тексте
    headers = { # заголовок запроса, в котором передаем IAM-токен
        'Authorization': f'Bearer {iam_token}', # token - наш IAM-токен
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://b1ghl4q6lijhc0ii8hdf/yandexgpt/latest", # указываем folder_id
       "maxTokens": 100,
       "text": g # text - тот текст, в котором мы хотим посчитать токены
    }
    r = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json=data,
            headers=headers
        ).json()

    if "tokens" in r: 
        return len(r["tokens"])
    else:
        logging.debug("Ключ просрочен")
        raise Exception
    

class Right(BaseFilter):
    async def __call__(self, message): 
        l = load(open("i.json", "r"))
        if message.from_user.id in l["Диалог"]:             
            return True
        return False
@rout.message(Right())
async def l1(message: Message,bot:Bot):
    print(3)
    l = load(open("i.json", "r"))
    if message.text == "Всё":
        l["Диалог"].remove(l["Юзеры"][str(message.from_user.id)]["id"])
        l["Диалог"].remove(message.from_user.id)
        await t.send_message(l["Юзеры"][str(message.from_user.id)]["id"],"Диалог завершён")
        l["Юзеры"][str(l["Юзеры"][str(message.from_user.id)]["id"])]["id"] = 0
        l["Юзеры"][str(message.from_user.id)]["id"] = 0
        dump(l, open("i.json", "w"))
        await t.send_message(message.from_user.id,"Диалог завершён")
        return
    await t.send_message(l["Юзеры"][str(message.from_user.id)]["id"],message.text)
    await t.send_message(l["Юзеры"][l["Юзеры"][str(message.from_user.id)]["id"]]["id"],message.text)
    

@rout.message(Command("start"))
async def hh(message:Message, apscheduler:AsyncIOScheduler):
    ser = connect("Гавно.db")
    s = ser.cursor()
    s.execute("""CREATE TABLE IF NOT EXISTS us(
    user_id PRIMARY KEY,
    user TEXT,
    assis TEXT,
    tokens_gpt INTEGER,
    tokens_sst INTEGER,
    tokens_tts INTEGER,
    Отлад BLOB);
""")
    g = s.execute(f"SELECT user_id FROM us WHERE EXISTS(SELECT user_id FROM us WHERE user_id = {message.from_user.id});").fetchone()
    k = s.execute('''SELECT user_id FROM us''').fetchall()
    if not g and len(k) >= 5:
        s.execute("INSERT INTO us (user_id, user, assis, tokens_gpt, tokens_sst, tokens_tts, Отлад) VALUES(?, ?, ?, ?, ?, ?, ?);", (message.from_user.id, "", "", 0, 0, 0, False))
        l = load(open("i.json", "r"))
        l["Юзеры"][str(message.from_user.id)] = {"id":0}
        dump(l, open("i.json", "w")) 
        await message.answer("Я твой диалог")         
    elif len(k) >= 5:
        k = load(open("us.json", "r"))
        if message.from_user.id not in k["Забанан"]:
            k["Забанан"].append(message.from_user.id)
        dump(k, open("us.json", "w"))
        await message.answer("Всё переполнено")
        return
    apscheduler.add_job(job,'interval',days=1 ,args=(message,))    
    ser.commit()
    ser.close()
    await message.answer("Привет") 
    

@rout.message(Command("debug"))
async def l(message:Message):
    async with ChatActionSender(bot=t,chat_id=message.chat.id):
        await message.answer_document(FSInputFile("Ло.txt", "ГыГ"), caption = "ГыГ")
    
 
@rout.message(Command("gavno"))
async def p(message:Message,state=FSMContext): 
    mark = types.ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text="Новая"),KeyboardButton(text="Старая")],[KeyboardButton(text="tts"),KeyboardButton(text="Отлад"),KeyboardButton(text="sst"), KeyboardButton(text="История"), KeyboardButton(text="Диалог")]],row_width=2, one_time_keyboard=True, resize_keyboard=True)
    await message.answer("Выбирай", reply_markup=mark)
    await state.set_state(N.n)

@rout.message(N.n, F.text)
async def i(message:Message,state=FSMContext):
    g = f2(message.from_user.id, "user_id", "tokens_gpt", "tokens_sst", "tokens_tts", "Отлад", "user", "assis")
    if message.text == "Новая" or message.text == "Старая":          
        if g[1] > 1000:
            await message.answer("Ты потратил все токены")
            return
        elif g[1] > 500:
            await message.answer("Ты потратил больше 500 токенов из 1000")
        elif g[1] > 800:
            await message.answer("Ты потратил больше 800 токенов из 1000")
        if message.text == "Новая":
            f1(message.from_user.id, ("user", ""), ("assis", ""))
            await state.set_state(N.n5)
        if message.text == "Старая" and not g[5]:
            await message.answer("Диалог не начат")
            return
        else:    
            await state.set_state(N.n6)
        mark = types.ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text="GPTSST")], [KeyboardButton(text="GPT")]],row_width=2, one_time_keyboard=True, resize_keyboard=True)
        await message.answer("Выбери", reply_markup=mark)
        return
    elif message.text == "sst":
        if g[2] > 12:      
            await message.answer("Ты потратил все блоки")
            return
        await state.set_state(N.n3)
        await message.answer("Говори")
    elif message.text == "tts":
        if g[3] > 1000:
            await message.answer("Ты потратил все символы")
            return
        await state.set_state(N.n2)
        await message.answer("Вводи")
    elif message.text == "Отлад":
        if g[4]:
            f1(message.from_user.id, ("Отлад", False))
            await message.answer("Отлад выключен")
        else:
            f1(message.from_user.id, ("Отлад", True))
            await message.answer("Отлад включён")
    elif message.text == "История":
        if g[5]:
            k = ""
            print(list(zip(g[5].split("[]"), g[6].split("[]"))))
            for r in list(zip(g[5].split("[]"), g[6].split("[]"))):        
                if r[1] == "":
                    continue
                k += "Ты: " + r[0] + "\n" + "Нейро: " + r[1] + "\n"
            print(k)
            await message.answer(k)
        else:
            await message.answer("История не начата")
    elif message.text == "Диалог": 
        l = load(open("i.json", "r"))
        # while u == message.from_user.id:      Проверка на самого себя
        #     u = choice(list(l["Юзеры"].keys()))
        u = choice(list(l["Юзеры"].keys()))
        if message.from_user.id not in l["Диалог"]:
            l["Диалог"].append(message.from_user.id)
            l["Диалог"].append(int(u))
            l["Юзеры"][str(message.from_user.id)]["id"] = u
            l["Юзеры"][u]["id"] = message.from_user.id
        dump(l, open("i.json", "w"))
        await state.clear()
        await message.answer("Начинай диалог")        
    else:
        await message.answer("Неверный запрос")
      
@rout.message(N.n5, F.text)
async def i(message:Message,state=FSMContext):
    if message.text == "GPTSST":  
        await state.set_state(N.n7)
        await message.answer("Говори") 
    if message.text == "GPT":
        await state.set_state(N.n1)
        await message.answer("Вводи")

@rout.message(N.n6, F.text)
async def i(message:Message,state=FSMContext):
    if message.text == "GPTSST":
        await state.set_state(N.n7)
        await message.answer("Говори")
    if message.text == "GPT": 
        await state.set_state(N.n1)
        await message.answer("Вводи")

def f1(id, *ar):
    ser = connect("Гавно.db")
    s = ser.cursor()        
    n = []
    k = "UPDATE us SET "
    for i in ar:
        if i == ar[-1]:
            k += i[0] + " = ?"
        else:
            k += i[0] + " = ?, "
        n.append(i[1])
    list(n)
    s.execute(k + f" WHERE user_id = {id};", n)
    ser.commit()
    ser.close()

def f2(id, *ar):
    ser = connect("Гавно.db")
    s = ser.cursor()
    k = "SELECT "
    for i in ar:
        if i == ar[-1]:
            k += i
        else:
            k += i + ", "
    h = s.execute(k + f" FROM us WHERE user_id IS NOT NULL AND user_id = {id};").fetchall()
    ser.commit()
    ser.close()
    return h[0]
  
def tts(id, text):
    g = f2(id,"tokens_tts", "Отлад")
    if g[0] > 1000:
        return (3, True)
    
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': 'ru-RU',  # язык текста - русский
        'voice': 'filipp',  # голос Филлипа
        'folderId': folder_id,
    }
    # Выполняем запрос
    response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize', headers=headers, data=data)
    
    
    if response.status_code == 200:
        # Если все хорошо, сохраняем аудио в файл
        with open("output.ogg", "+wb") as audio_file:
            audio_file.write(response.content)               
            f1(id, ("tokens_tts", g[0] + len(text)))
            return (2, True)
    else:
        if g[1]:
            return (4, response.json)
        else:
            return (5, True)
    
async def tts1(message:Message, text):
    t = tts(message.from_user.id, text)
    if t[0] == 2:
        async with ChatActionSender(bot=t,chat_id=message.chat.id):
            await message.answer_audio(FSInputFile("output.ogg", "ГыГ"), caption = "ГыГ")
    if t[0] == 3:
        await message.answer("Нету символов")
    if t[0] == 4:
        await message.answer(str(t[1]))
    if t[0] == 5:
        await message.answer("Ошибка")
        
@rout.message(N.n2, F.text)
async def tts2(message:Message,state=FSMContext):
    await tts1(message, message.text)
        
async def sst(id, voice):
    g = f2(id,"tokens_sst", "Отлад")
    
    if g[0] > 10:
        return (3, True)
    
    await t.download(voice, "ov.ogg")
    
    # iam_token, folder_id для доступа к Yandex SpeechKit

    # Указываем параметры запроса
    params = "&".join([
        "topic=general",  # используем основную версию модели
        f"folderId={folder_id}",
        "lang=ru-RU"  # распознаём голосовое сообщение на русском языке
    ])

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
        
        # Выполняем запрос
    response = requests.post(
            f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
        headers=headers, 
        data=open("ov.ogg", "rb")
    )
    
    # Читаем json в словарь
    decoded_data = response.json()
    # Проверяем, не произошла ли ошибка при запросе
    if decoded_data.get("error_code") is None:
        f1(id,("tokens_sst", (g[0] + ceil(voice.duration / 15))))
        return (2, decoded_data)
    else:
        if g[1]:
            return (4, decoded_data)
        else:
            return (5, True)
    
async def sst1(message):
    s = await sst(message.from_user.id, message.voice)
    if s[0] == 2:
        async with ChatActionSender(bot=t,chat_id=message.chat.id):
            if s[1]["result"] == "":
                await message.answer("Ничо не слышно")
            else:
                await message.answer(s[1]["result"])
            return s[1]["result"]
    if s[0] == 3:
        await message.answer("Нету блоков")
    if s[0] == 4:
        await message.answer(str(tts[1]))
    if s[0] == 5:
        await message.answer("Ошибка")
        
@rout.message(N.n3, F.voice)
async def sst2(message:Message,state=FSMContext):
    await sst1(message)
         
def gpt(id, text):
    g = list(f2(id,"user","assis","tokens_gpt", "Отлад"))
    
    if g[2] > 1000:               
        return (3, True)
    
    data = {
        "modelUri": f"gpt://b1ghl4q6lijhc0ii8hdf/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 30
        },
        "messages": [{"role":"system", "text":"Ответь"}]
    }
    
    g[0] += text.replace("[]", " ") + "[]"
    
    b = list(zip(g[0].split("[]"), g[1].split("[]")))
    for r in b:        
        if r[0] != "":
            data["messages"].append(
                {
                    "role": "user",
                    "text": r[0]
                }
            ) 
        if r[1] != "":
            data["messages"].append(
                {
                    "role": "assistant",
                    "text": r[1]
                }
            )
    
    logging.info("Генерация")

    resp = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", 
                headers= {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }, json=data)
    
    logging.debug("Генерация завершена")
    
    print(resp.json())
    
    if resp.status_code == 200 and 'result' in resp.json():
        result = resp.json()['result']["alternatives"][0]["message"]["text"]
        h = count_tokens(g[0].replace("[]", " ") + ". " + (g[1] + " "+result).replace("[]", " "))
        f1(id, ("user", g[0]), ("assis", g[1] + result + "[]"), ("tokens_gpt", g[2] + h))
        if g[3]:
            return (1, resp.json())
        else:
            return (2, resp.json())
    else:
        if g[3]:
            return (4, resp.json())
        else:
            return (5, True)
            
async def gpt1(message, text):        
    g = gpt(message.from_user.id, text) 
    if g[0] == 1 or g[0] == 2:
        if g[1]['result']["alternatives"][0]["message"]["text"] == "":
            await message.answer("Объяснение завершено")
            return
        await message.answer(g[1]['result']["alternatives"][0]["message"]["text"])
        if g[0] == 1:       
            await message.answer(str(g[1]))
        return g[1]['result']["alternatives"][0]["message"]["text"]
    if g[0] == 3:       
        await message.answer("Ты потратил все токены")     
    if g[0] == 4:               
        await message.answer(str(g[1])) 
    if g[0] == 5:
        await message.answer("Ошибка")
    
@rout.message(N.n1, F.text)
async def gpt2(message:Message,state=FSMContext):
    if message.text == "Возврат":
        await state.clear()
        await message.answer("Есть")    
        return
    await gpt1(message, message.text)
    
@rout.message(N.n7, F.content_type.in_({"voice", "text"}))
async def j(message:Message,state=FSMContext):        
    if message.text == "Возврат":
        await message.answer("Есть")
        await state.clear()
        return
    elif message.voice:       
        i = await sst1(message)
        if i == "Возврат":
            await state.clear()
            await message.answer("Есть")
            return
    await tts1(message, await gpt1(message, i))
    

async def job(message):
    g = list(f2(message.from_user.id,"user","assis","tokens_gpt", "Отлад"))
    
    if g[2] > 1000:               
        return
    
    data = {
        "modelUri": f"gpt://b1ghl4q6lijhc0ii8hdf/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 30
        },
        "messages": [{"role": "system", "text": "Извлеки из этого диалога любопытный факт для пользователя"}]
    }
    
    g[0] += "Любопытный факт" + "[]"
    
    b = list(zip(g[0].split("[]"), g[1].split("[]")))
    
    if len(b) > 5:
        for i in range(len(b) - 5):
            b.pop(i)
    
    for r in b:        
        if r[0] != "":
            data["messages"].append(
                {
                    "role": "user",
                    "text": r[0]
                }
            ) 
        if r[1] != "":
            data["messages"].append(
                {
                    "role": "assistant",
                    "text": r[1]
                }
            )
    
    logging.info("Генерация")

    resp = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", 
                headers= {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }, json=data)
    
    print(resp.json())
    
    logging.debug("Генерация завершена")
    
    if resp.status_code == 200 and 'result' in resp.json():
        result = resp.json()['result']["alternatives"][0]["message"]["text"]
        h = count_tokens(g[0].replace("[]", " ") + ". " + (g[1] + " "+result).replace("[]", " "))
        f1(message.from_user.id, ("user", g[0]), ("assis", g[1] + result + "[]"), ("tokens_gpt", g[2] + h))
        await message.answer(result + "\n\nТак как больше 1 сессии нету то вести диалог с этим сообщением не нада")
    else:
        await message.answer("Ошибка")
        logging.debug("Генерация завершена")
        
        

if __name__ == "__main__":
    logging.info("Бот запущен")
    # loop = get_event_loop()
    # task = create_task(main())
    # loop.run_until_complete(gather(task))
    
    lp = get_event_loop()
    lp.run_until_complete(main())



