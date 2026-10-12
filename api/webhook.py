import os
import asyncio
import random
import time
from http.server import BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, Update
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError

# ==== НАСТРОЙКИ ====
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
COOLDOWN_SECONDS = 7       # обычный кулдаун на чат
SPAM_WINDOW = 5            # окно подсчёта спама (сек)
SPAM_THRESHOLD = 3         # 3+ команды за окно = спам
SPAM_BLOCK_SECONDS = 10    # блокировка спамера (сек)
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

chat_cooldown: dict[int, float] = {}
user_block: dict[int, float] = {}
user_history: dict[int, list[float]] = {}


async def safe_send(coro):
    try:
        await coro
    except TelegramRetryAfter as e:
        print(f"FLOOD WAIT: {e.retry_after}s")
        await asyncio.sleep(e.retry_after + 0.5)
        try:
            await coro
        except Exception as e2:
            print("RETRY FAILED:", repr(e2))
    except TelegramAPIError as e:
        print("TELEGRAM API ERROR:", repr(e))
    except Exception as e:
        print("SEND ERROR:", repr(e))


@dp.message(Command("messbot"))
async def messbot_handler(message: Message):
    now = time.monotonic()
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0

    # === 1. Проверка: заблокирован ли пользователь за спам ===
    if user_id in user_block:
        remaining = user_block[user_id] - now
        if remaining > 0:
            await safe_send(
                message.reply(f"🚫 Слишком много команд! Жди {int(remaining) + 1} сек.")
            )
            return
        else:
            del user_block[user_id]

    # === 2. Считаем команды пользователя за окно ===
    history = user_history.setdefault(user_id, [])
    history[:] = [t for t in history if now - t < SPAM_WINDOW]
    history.append(now)

    # 3 и больше команд за 5 секунд = спам
    if len(history) >= SPAM_THRESHOLD:
        user_block[user_id] = now + SPAM_BLOCK_SECONDS
        user_history[user_id] = []
        print(f"SPAM BLOCK: user={user_id} chat={chat_id}")
        await safe_send(
            message.reply(
                f"🚫 Слишком много команд! Блок на {SPAM_BLOCK_SECONDS} сек."
            )
        )
        return

    # === 3. Обычный кулдаун на чат ===
    if chat_id in chat_cooldown:
        elapsed = now - chat_cooldown[chat_id]
        if elapsed < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed) + 1
            await safe_send(
                message.reply(
                    f"⏳ Подожди ещё {remaining} сек., я коплю энергию для суеты!"
                )
            )
            return

    # === 4. Отвечаем ===
    chat_cooldown[chat_id] = now
    await safe_send(message.answer(random.choice(MESSAGES)))


async def _async_process_update(update: Update):
    await dp.feed_update(bot, update)


def _process_update(update: Update):
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(_async_process_update(update))
    except Exception as e:
        print("PROCESS ERROR:", repr(e))


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            update = Update.model_validate_json(body)
            _process_update(update)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        except Exception as e:
            print("HANDLER ERROR:", repr(e))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")
