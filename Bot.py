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
from sqlite3 import connect
from json import load, dump
from random import choice
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Callable, Awaitable, Any, Dict
from config import t, logging
from database import f1, f2
from speechkit import tts1, sst1
from yandexgpt import gpt1, job

dp = Dispatcher(storage = MemoryStorage())

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
            for r in list(zip(g[5].split("[]"), g[6].split("[]"))):        
                k += "Ты: " + r[0] + "\n" + "Нейро: " + r[1] + "\n"
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

        
@rout.message(N.n2, F.text)
async def tts2(message:Message,state=FSMContext):
    await tts1(message, message.text)
        
        
@rout.message(N.n3, F.voice)
async def sst2(message:Message,state=FSMContext):
    await sst1(message)
         
    
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
    if message.voice:       
        i = await sst1(message)
        if i == "Возврат":
            await state.clear()
            await message.answer("Есть")
            return
        elif i == False:
            return
    k = await gpt1(message, i)
    if k == False:
        return
    await tts1(message, k)
    logging.info("Победа")
        
        
if __name__ == "__main__": 
    lp = get_event_loop()
    lp.run_until_complete(main())



