from config import iam_token
import requests
from database import f1, f2
from config import logging

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
        raise Exception
    
    
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
    

    resp = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", 
                headers= {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }, json=data)
    
    
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
        logging.info("2")
        if g[0] == 1:       
            await message.answer(str(g[1]))
        return g[1]['result']["alternatives"][0]["message"]["text"]
    if g[0] == 3:       
        await message.answer("Ты потратил все токены")     
    if g[0] == 4:               
        await message.answer(str(g)) 
    if g[0] == 5:
        await message.answer("Ошибка")
    return False
        

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
    

    resp = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", 
                headers= {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }, json=data)
    
    print(resp.json())
    
    
    
    if resp.status_code == 200 and 'result' in resp.json():
        result = resp.json()['result']["alternatives"][0]["message"]["text"]
        h = count_tokens(g[0].replace("[]", " ") + ". " + (g[1] + " "+result).replace("[]", " "))
        f1(message.from_user.id, ("user", g[0]), ("assis", g[1] + result + "[]"), ("tokens_gpt", g[2] + h))
        await message.answer(result + "\n\nТак как больше 1 сессии нету то вести диалог с этим сообщением не нада")
    else:
        await message.answer("Ошибка")
        