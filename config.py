from aiogram import Bot
import logging

token =''
iam_token = ""
folder_id = ''

t = Bot(token)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename="Ло.txt", filemode="w")