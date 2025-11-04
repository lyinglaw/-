import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# Импортируем "будильник" для 24/7 работы
from keep_alive import keep_alive

# --- Конфигурация ---
# Токен берется из Секретов Replit (ключ: BOT_TOKEN)
BOT_TOKEN = os.environ['BOT_TOKEN']

# ❗️ Вставьте СВОЙ ID администратора (число)
ADMIN_ID = 123456789  

# ❗️ Вставьте ССЫЛКИ на ваши Google Формы
FORM_LINK_1 = "https://docs.google.com/forms/d/e/ВАША_ПЕРВАЯ_ССЫЛКА/viewform" 
FORM_LINK_2 = "https://docs.google.com/forms/d/e/ВАША_ВТОРАЯ_ССЫЛКА/viewform" 

logging.basicConfig(level=logging.INFO)

# --- Логика бота ---

class AdminAction(CallbackData, prefix="admin"):
    action: str
    user_id: int

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        f"Привет, {message.from_user.full_name}!\n"
        f"Вот наша стандартная форма обратной связи:\n<b>{FORM_LINK_1}</b>\n\n"
        "Для <b>специального запроса</b> (партнерство, жалоба и т.д.) "
        "просто напишите его в этот чат."
    )
    await message.answer(text, parse_mode="HTML") # 👈 Добавлен parse_mode="HTML"

@router.message(F.text & ~F.text.startswith('/'))
async def handle_text_request(message: Message, bot: Bot):
    user_id = message.from_user.id
    user_text = message.text
    user_name = message.from_user.full_name

    await message.answer("✅ Ваш запрос отправлен на рассмотрение администратору. Ожидайте ответа.")

    # Создаем кнопки для админа
    builder = InlineKeyboardBuilder()
    
    # Кнопка для ответа (двусторонняя связь)
    chat_url = f"tg://user?id={user_id}" 
    builder.button(
        text="✉️ Ответить пользователю", 
        url=chat_url
    )
    
    # Кнопки для Формы 2
    builder.button(
        text="✅ Одобрить (Форма 2)", 
        callback_data=AdminAction(action="approve", user_id=user_id).pack()
    )
    builder.button(
        text="❌ Отклонить", 
        callback_data=AdminAction(action="reject", user_id=user_id).pack()
    )
    builder.adjust(1) 

    await bot.send_message(
        ADMIN_ID,
        f"❗️ <b>Новый запрос</b> от {user_name} (ID: <code>{user_id}</code>)\n\n" # <code> для ID
        f"Текст запроса:\n«{user_text}»",
        reply_markup=builder.as_markup(),
        parse_mode="HTML" # 👈 Добавлен parse_mode="HTML"
    )

@router.callback_query(AdminAction.filter())
async def handle_admin_decision(query: CallbackQuery, callback_data: AdminAction, bot: Bot):
    user_id = callback_data.user_id
    action = callback_data.action

    await query.message.edit_reply_markup(reply_markup=None)

    if action == "approve":
        # Отправляем пользователю Форму 2. Используем <b> для жирного шрифта.
        await bot.send_message(
            user_id,
            "🎉 Ваш запрос <b>одобрен</b> администратором! Вот специальная форма:\n"
            f"<b>{FORM_LINK_2}</b>",
            parse_mode="HTML" # 👈 Добавлен parse_mode="HTML"
        )
        await query.message.answer(f"✅ Запрос от {user_id} ОДОБРЕН.")
    elif action == "reject":
        await bot.send_message(
            user_id,
            "К сожалению, ваш запрос был <b>отклонен</b> администратором.",
            parse_mode="HTML" # 👈 Добавлен parse_mode="HTML"
        )
        await query.message.answer(f"❌ Запрос от {user_id} ОТКЛОНЕН.")

    await query.answer()

# --- Функция запуска ---
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    keep_alive() 
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
