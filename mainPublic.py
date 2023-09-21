"""
Bot that will help to learn some popular english words.
"""

import schedule
import wordmanager
import translator
import definitions
import time
import telebot
import threading
import os
import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class WordMessage:
   
   message: str
   audioUrl: Optional[str]

def getBytesFromRequest(url: str):
   
   answer = requests.get(url, stream=True)
   
   return answer.raw

def getRandomWordWithDefinitionTranslated(word: str) -> WordMessage:
   
   wordObject = definitions.getDefinitions(word)
   
   message = f"{word} [{wordObject.phonetic}] - {translator.toRU(word)}\n\nЗНАЧЕНИЯ:\n"
   
   if wordObject.meanings:
      
      index = 1
      
      for meaning in wordObject.meanings:
         
         for definition in meaning.defininions:
            
            message += f"{index}. <b>{definition.definition}</b>\n{translator.toRU(definition.definition)}\n\n"
            index += 1
            
            if index > 10: break
         
         if index > 10: break
         
   else:
      
      message += "Нет значений в базе данных"
   
   #print(wordObject.phoneticAudioUrl)
         
   return WordMessage(message, wordObject.phoneticAudioUrl)
   
         
def getDistributionChats() -> list[int]:
   
   with open('distributionChats.txt', 'r') as distFile:
      
      return list( map(lambda x: int(x), distFile.readlines()) )


def addDistributionChat(chatId: int):
   
   with open('distributionChats.txt', 'a') as distFile:
      
      distFile.write(str(chatId) + "\n")


def removeDistributionChat(chatId: int):
   
   chats = getDistributionChats()
   
   chats.remove(chatId)
   
   with open('distributionChats.txt', 'w') as distFile: distFile.writelines( list( map(lambda x: str(x), chats) ) )


manager = wordmanager.parseWordsFromTextFile("new_commonwords.txt")


bot = telebot.TeleBot() 


chats = getDistributionChats()


trainState = {}


@bot.message_handler(commands=['start'])
def startCommand(message: telebot.types.Message):

   bot.reply_to(message, "Привет! Для подписки на рассылку введи команду /join")
   
@bot.message_handler(commands=["help"])
def helpCommand(message: telebot.types.Message):
   
   bot.reply_to(
      message, 
      "Бот в определенное для всех время рассылает английские слова (2000 самых популярных слов) со значениями и переводом." +
      "\nДля присоеденинения к рассылке введите команду /join\nДля прекращения рассылки введите команду /leave" +
      "\nВремя рассылки (Московское время): 10:00, 12:00, 15:00, 18:00, 21:00"
   )

@bot.message_handler(commands=["trigger"])
def triggerTask(message: telebot.types.Message):
   
   distribution()

@bot.message_handler(commands=["join"])
def joinCommand(message: telebot.types.Message):
   
   if message.chat.id in chats:
      bot.reply_to(message, "Вы уже подписаны на рассылку")
      return
   
   chats.append(message.chat.id)
   addDistributionChat(message.chat.id)
   bot.reply_to(message, "Успешно! Времена рассылки можно узнать через команду /help.")
   
@bot.message_handler(commands=["leave"])
def leaveCommand(message: telebot.types.Message):
   
   if message.chat.id not in chats:
      bot.reply_to(message, "Вы и так не подписаны на рассылку :)")
      return
   
   chats.remove(message.chat.id)
   removeDistributionChat(message.chat.id)
   bot.reply_to(message, "Успешно! Если захотите снова подписаться на рассылку - используйте команду /join")

@bot.message_handler(commands=["train"])
def trainCommand(message: telebot.types.Message):
   
   if fileIsEmpty(message.chat.id):
      
      bot.reply_to(message, "Вы еще не получили никакие слова из рассылки, ожидайте :)")
      return
   
   if trainState.get(message.chat.id, False):
      
      bot.reply_to(message, f"Вы уже запустили тренировку, ваше слово: {trainState[message.chat.id]}")
      return
   
   trainingWord = wordmanager.parseWordsFromTextFile(f"chat_words/{message.chat.id}").getRandom()
   
   trainState[message.chat.id] = trainingWord
   bot.reply_to(message, f"Ваше слово - <b>{trainingWord}</b>. Напишите его перевод в течении минуты.", parse_mode="HTML")

@bot.message_handler(func= lambda message: not message.text.startswith("/"))
def handleTrainText(message: telebot.types.Message):
   
   word = trainState.get(message.chat.id, "")
   
   if word:
      
      translatedWord = translator.toRU(word)
      
      if translatedWord.strip().lower() == message.text.strip().lower():
         bot.reply_to(message, "Правильно! Поздравляю :)")
      else:
         bot.reply_to(message, f"Неправильно :( Перевод слова \"{word}\" - \"{translatedWord}\"")
      
      del trainState[message.chat.id]

def fileIsEmpty(chatId: int|str):
   
   if not checkLearnedWordsFile(chatId): return True
   
   return os.stat(f"chat_words/{chatId}").st_size == 0

def checkLearnedWordsFile(chatId: int|str):
   
   if not os.path.isfile(f"chat_words/{chatId}"):
      
      with open(f"chat_words/{chatId}", "w") as chatFile: return False #create file
      
   return True

def distribution():
   
   for chat in chats:
      
      word = manager.getRandom().capitalize()
      
      message = getRandomWordWithDefinitionTranslated(word)
      
      if len(message.message) > 4096:
         
         i = 0
         while i < len(message.message):
            
            if i + 4096 < len(message.message):
               
               bot.send_message(chat, message.message[i:i+4096], parse_mode="HTML")
               
            else:
               
               bot.send_message(chat, message.message[i:len(message.message)], parse_mode="HTML")
               
            i += 4096
            
      else:
         
         bot.send_message(chat, message.message, parse_mode="HTML")
         
      if message.audioUrl:
         
         audioBytes = getBytesFromRequest(message.audioUrl)
         
         bot.send_audio(chat, audioBytes, title=word)
      
      #checkLearnedWordsFile(chat)
      
      with open(f"chat_words/{chat}", "a") as chatFile: chatFile.write(f"{word}\n")
      
      

distributionTimes = ["10:00", "12:00", "15:00", "18:00", "21:00"]

for distTime in distributionTimes:
   
   schedule.every().day.at(distTime, "Europe/Moscow").do(distribution)


threading.Thread(target=bot.infinity_polling, name="bot_polling", daemon=True).start()
print("bot started")

while True:
   schedule.run_pending()
   time.sleep(1)