import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.builtin import CommandStart
from dotenv import load_dotenv

# для смены кодировки ogg на wav
import ftransc.core as ft
# для преобразования речи в текст
import speech_recognition as sr

import random

# функция, подгружающая .env константы
load_dotenv()

# получаем токен из .env с помощью функции getenv
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

# инициализируем объект бота
# (параметр parse_mode позволяет установить parse_mode по умолчанию)
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# инициализируем диспетчер
dp = Dispatcher(bot)


# дефолтный хэндлер для команды start
@dp.message_handler(CommandStart())
async def start(message: types.Message):
    text = "\n".join(
        (
            f"В чём дело, {message.from_user.full_name}?",
        )
    )

    await message.answer(text)


# хэндлер для обработки запросов содержащих ругательства
@dp.message_handler()
async def guard_answer(message: types.Message):

    text = message.text
    some = ("привет", "пока")
    if text.startswith(some) or text.endswith(some) or text in some:
        await message.reply("Неуважение к закону - неуважение ко мне.")


@dp.message_handler(content_types=['voice'])
async def voice_processing(message: types.Message):

    flag = False
    guard_phrases = os.listdir("guard/calm")
    agressive_phrases = os.listdir("guard/agressive")


    ogg_file =f"voice/{message.from_user.id}.ogg"
    wav_file = ogg_file.replace("ogg", "wav")

    # функция download сохраняем файл (передаём путь)
    await message.voice.download(ogg_file)

    # функция transcode меняет кодировку файла и сохраняет файл по пути, указанному в аргументе 3
    ft.transcode(ogg_file, 'wav', "voice")

    # инициализируем объект Recognizer
    recognizer = sr.Recognizer()
    # print(f"guard/calm/{str(random.choice(guard_phrases).split('_')[0])}.mp3")

    # вызываем метод WavFile на полученном wav файле и используем результат вызова с контекстным менеджером with
    with sr.WavFile(wav_file) as file:
        # вызываем метод listen экземпляра Reconizer на файле
        audio = recognizer.listen(file)
        try:
            # распознаём речь с помощью распознавателя google (передаём кодировку языка)
            text = recognizer.recognize_google(audio, language="ru-RU")
            print("Working on...")
            print(text)
            if text.endswith("**"):
                flag = True
                print("он нарвался")

        except Exception as ex:
            print(ex)
            print("Something went wrong...try again...")

    # получаем рандомную фразу стражника
    if flag:
        random_phrase = f"guard/agressive/{random.choice(agressive_phrases)}"
    else:
        random_phrase = f"guard/calm/{random.choice(guard_phrases)}"

    with open(random_phrase, "rb") as phrase:
        await message.answer_voice(phrase)

    # удаляем файлы записи сообщения пользователя
    os.remove(ogg_file)
    os.remove(wav_file)


# хэндлер для обработки всех прочих запросов к боту
@dp.message_handler()
async def guard_answer(message: types.Message):
    print(message.content_type)


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
