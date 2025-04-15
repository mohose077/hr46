import os
import logging
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, ContextTypes, filters
)
from config import TELEGRAM_BOT_TOKEN, ADMIN_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Стан FSM
ASK_PHONE, ASK_QUESTION = range(2)
banned_users = set()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in banned_users:
        return

    keyboard = [
        [InlineKeyboardButton("Вакансії WORK.UA", url="https://www.work.ua/jobs/by-company/2620784/#jobs")],
        [InlineKeyboardButton("Вакансії ROBOTA.UA", url="https://robota.ua/company14232568")],
        [InlineKeyboardButton("Зв'язатися із рекрутером", callback_data="recruiter")],
        [InlineKeyboardButton("Отримати відношення", callback_data="relation")]
    ]

    text = (
        "Вас вітає бот 46 окремої аеромобільної бригади.\n"
        "Якщо хочете до нас перевестися або мобілізуватися, оберіть необхідну дію:"
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# Після натискання кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if user.id in banned_users:
        return

    context.user_data["contact_reason"] = (
        "Зв’язатися із рекрутером" if query.data == "recruiter" else "Отримати відношення"
    )
    await query.message.reply_text("Введіть, будь ласка, свій номер телефону 📱")
    return ASK_PHONE

# Збір телефону
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Дякуємо! А тепер напишіть своє запитання 📝")
    return ASK_QUESTION

# Збір запитання і надсилання адміну
async def finish_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    phone = context.user_data.get("phone", "Невідомо")
    reason = context.user_data.get("contact_reason", "Невідомо")

    user = update.effective_user
    chat_link = f"tg://user?id={user.id}"

    msg = (
        f"📥 <b>{reason}</b>\n"
        f"👤 <a href='{chat_link}'>{user.full_name}</a> (@{user.username})\n"
        f"☎️ Номер: <code>{phone}</code>\n"
        f"📝 Повідомлення: {question}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode='HTML')
    await update.message.reply_text("Дякуємо! Ваше звернення надіслано.")
    return ConversationHandler.END

# Вихід з діалогу
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^(recruiter|relation)$")],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
