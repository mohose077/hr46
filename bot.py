import logging
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from config import TELEGRAM_BOT_TOKEN, ADMIN_ID

logging.basicConfig(level=logging.INFO)
banned_users = set()

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if user.id in banned_users:
        return

    if query.data in ["recruiter", "relation"]:
        action = "Зв'язатися із рекрутером" if query.data == "recruiter" else "Отримати відношення"
        chat_link = f"tg://user?id={user.id}"
        msg = f"📥 <b>{action}</b>\n👤 <a href='{chat_link}'>{user.full_name}</a> (@{user.username})\nID: <code>{user.id}</code>"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Заблокувати", callback_data=f"ban_{user.id}")]
        ])
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode='HTML', reply_markup=buttons)
        await query.edit_message_text("Дякуємо! Ваш запит отримано.")
        
    elif query.data.startswith("ban_"):
        uid = int(query.data.split("_")[1])
        banned_users.add(uid)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Користувача <code>{uid}</code> заблоковано.", parse_mode='HTML')

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
