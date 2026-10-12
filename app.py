import asyncio
import random
import time
import os
import threading

from flask import Flask
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# ==== НАСТРОЙКИ ====
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН")
COOLDOWN_SECONDS = 7
# ===================

MESSAGES = [
    "🔥 Кто первый напишет — тот и красавчик!",
    "👀 Я тут суету наведу, вы не против?",
    "🍕 Заказываем пиццу? Я скидываюсь морально.",
    "🤔 А что если... мы все сейчас напишем одновременно?",
    "💀 Кто не активен — тот бот.",
    "🎲 Кидаю кубик: выпало число 7. Что это значит — не знаю.",
    "🚨 ВНИМАНИЕ! В чате замечен подозрительно спокойный человек!",
    "🐸 А вы знали, что жабы не пьют воду через рот?",
    "⚡ СРОЧНО: кто-нибудь, напишите что-то смешное!",
    "🥱 Мне скучно. Развлекайте меня.",
    "🎉 У кого сегодня хорошее настроение? Отметьтесь!",
    "🤖 Я бот. Но я тоже хочу общения.",
    "🍿 Захватите попкорн, сейчас будет движ.",
    "💤 Тишина в чате... подозрительно тихо...",
    "🔥 Горим! Кто в теме?",
    "🎮 Кто в игрушки? Пишите ник.",
    "☕ Кофе уже выпит. Время суеты!",
    "🐱 Мяу. (это сигнал к действию)",
    "🎯 План на вечер: суета.",
    "💥 БУМ! Сообщение-бомба.",
    "🚀 Полетели! Кто со мной?",
    "🎩 Магия: если ответишь на это сообщение — будет удача.",
    "🍩 Пончик тому, кто ответит первым.",
    "🧠 Загадка: что всегда идёт, но никогда не приходит?",
    "🐉 Вызвал дракона. Он в пути.",
    "⭐ Ставлю лайк этому чату.",
    "🌪️ Тут был торнадо. Я выжил.",
    "🎤 Караоке, кто хочет?",
    "📢 Объявление: чат официально проснулся!",
    "🦆 Утка. Просто утка. Всем утка.",
    "💣 Тик-так... тик-так...",
    "🌈 Радуга в чате! Все загадывают желание.",
    "🍺 Кто угощает? Я не пью, но поддержу.",
    "🎪 Цирк приехал. Билеты бесплатные.",
    "👽 Привет, земляне.",
    "🐢 Медленно, но уверенно — к суете.",
    "🔔 Дзынь! Сообщение доставлено.",
    "🎨 Нарисуйте в голове кота. Готово? Молодцы.",
    "🥇 Конкурс: кто напишет самое странное сообщение?",
    "🎵 Танцуют все!",
    "🧨 Петарда! Бах!",
    "🍀 Поймай удачу за хвост!",
    "🐺 Вою на луну. Кто со мной?",
    "🎁 Дарю вам своё внимание.",
    "🕹️ Чат, активируйся!",
    "📣 Эй, вы там! Да-да, вы!",
    "🎈 Шарик улетел. Грустно.",
    "🏆 Вы все — победители.",
    "🥶 Холодно? Согреемся суетой!",
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
last_used: dict[int, float] = {}


@dp.message(Command("messbot"))
async def messbot_handler(message: Message):
    chat_id = message.chat.id
    now = time.monotonic()

    if chat_id in last_used:
        elapsed = now - last_used[chat_id]
        if elapsed < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed) + 1
            await message.reply(f"⏳ Подожди ещё {remaining} сек., я коплю энергию для суеты!")
            return

    last_used[chat_id] = now
    await message.answer(random.choice(MESSAGES))


def run_bot():
    """Запускаем polling в отдельном потоке."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dp.start_polling(bot))


# ==== Flask-заглушка для Render ====
app = Flask(__name__)


@app.route("/")
@app.route("/health")
def health():
    return "Bot is running", 200


if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
