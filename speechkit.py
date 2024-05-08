from config import iam_token, folder_id,t,logging
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import Message, FSInputFile
import requests
from database import f1, f2
from math import ceil


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
            logging.info("3")
    elif t[0] == 3:
        await message.answer("Нету символов")
    elif t[0] == 4:
        await message.answer(str(t))
    elif t[0] == 5:
        await message.answer("Ошибка")
        
        
async def sst(id, voice):
    g = f2(id,"tokens_sst", "Отлад")
    
    if g[0] > 13:
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
    print(decoded_data)
    # Проверяем, не произошла ли ошибка при запросе
    if decoded_data.get("error_code") is None and response.status_code == 200:
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
                logging.info("1")
            return s[1]["result"]
    elif s[0] == 3:
        await message.answer("Нету блоков")
    elif s[0] == 4:
        await message.answer(str(sst))
    elif s[0] == 5:
        await message.answer("Ошибка")
    return False