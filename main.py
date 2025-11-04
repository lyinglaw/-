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
BOT_TOKEN = os.environ['8239172264:AAE-u-U-JROo-O9gd_gO7bx-jyqFtOb5gdE']

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
        f"Вот наша стандартная форма обратной связи:\n**{FORM_LINK_1}**\n\n"
        "Для **специального запроса** (партнерство, жалоба и т.д.) "
        "просто напишите его в этот чат."
    )
    await message.answer(text)

@router.message(F.text & ~F.text.startswith('/'))
async def handle_text_request(message: Message, bot: Bot):
    user_id = message.from_user.id
    user_text = message.text
    user_name = message.from_user.full_name

    await message.answer("✅ Ваш запрос отправлен на рассмотрение администратору. Ожидайте ответа.")

    builder = InlineKeyboardBuilder()
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
        f"❗️ **Новый запрос** от {user_name} (ID: `{user_id}`)\n\n"
        f"Текст запроса:\n«{user_text}»",
        reply_markup=builder.as_markup()
    )

@router.callback_query(AdminAction.filter())
async def handle_admin_decision(query: CallbackQuery, callback_data: AdminAction, bot: Bot):
    user_id = callback_data.user_id
    action = callback_data.action

    await query.message.edit_reply_markup(reply_markup=None)

    if action == "approve":
        await bot.send_message(
            user_id,
            "🎉 Ваш запрос **одобрен** администратором! Вот специальная форма:\n"
            f"**{FORM_LINK_2}**"
        )
        await query.message.answer(f"✅ Запрос от {user_id} ОДОБРЕН. Форма 2 отправлена.")
    elif action == "reject":
        await bot.send_message(
            user_id,
            "К сожалению, ваш запрос был отклонен администратором."
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
