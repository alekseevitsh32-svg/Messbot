import os
import json
import random
import time
import asyncio
from http.server import BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, Update

# ==== НАСТРОЙКИ ====
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
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
            await message.reply(
                f"⏳ Подожди ещё {remaining} сек., я коплю энергию для суеты!"
            )
            return

    last_used[chat_id] = now
    await message.answer(random.choice(MESSAGES))


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            update = Update.model_validate_json(body)

            asyncio.run(dp.feed_update(bot, update))

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        except Exception as e:
            print("ERROR:", e)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

    def do_GET(self):
        # Health-check, чтобы можно было открыть в браузере
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")
