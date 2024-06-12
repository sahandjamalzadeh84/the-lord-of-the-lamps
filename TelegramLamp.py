from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging
import requests

BOT_TOKEN = "<BOT_TOKEN>" #Your BOT_TOKEN  to use bot
FLASK_APP_URL = "http://localhost:7000"
PASSWORD = "yourpassword"  # Your Password to Continue
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# To save the authentication status of users
password = set()


#This function show the status of Lamps
def lamp_keyboard():
    try:
        lamp_1_status = "❌" if not requests.get(f"{FLASK_APP_URL}/get_lamp_state/lamp_1").json().get('state', False) else "✅"
        lamp_2_status = "❌" if not requests.get(f"{FLASK_APP_URL}/get_lamp_state/lamp_2").json().get('state', False) else "✅"
        lamp_3_status = "❌" if not requests.get(f"{FLASK_APP_URL}/get_lamp_state/lamp_3").json().get('state', False) else "✅"
        lamp_4_status = "❌" if not requests.get(f"{FLASK_APP_URL}/get_lamp_state/lamp_4").json().get('state', False) else "✅"
    except Exception as e:
        logger.error(f"Error fetching lamp state: {e}")
        lamp_1_status = lamp_2_status = lamp_3_status = lamp_4_status = "❓"

    keyboard = [
        [InlineKeyboardButton(f"لامپ ۱ {lamp_1_status}", callback_data='toggle_lamp_1')],
        [InlineKeyboardButton(f"لامپ ۲ {lamp_2_status}", callback_data='toggle_lamp_2')],
        [InlineKeyboardButton(f"لامپ ۳ {lamp_3_status}", callback_data='toggle_lamp_3')],
        [InlineKeyboardButton(f"لامپ ۴ {lamp_4_status}", callback_data='toggle_lamp_4')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def lamps(lamp_name):
    try:
        current_state = requests.get(f"{FLASK_APP_URL}/get_lamp_state/{lamp_name}").json().get('state')
        if current_state is None:
            raise ValueError("Invalid lamp state received")

        if current_state:
            response = requests.post(f"{FLASK_APP_URL}/turn_off_lamp/{lamp_name}")
        else:
            response = requests.post(f"{FLASK_APP_URL}/turn_on_lamp/{lamp_name}")

        return response.json().get('message', 'Error  ')
    except Exception as e:
        logger.error(f"Error   {lamp_name}: {e}")
        return f"An error occurred: {e}"

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Cheking the authentication of users
    if user_id not in password:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفاً ابتدا احراز هویت کنید."
        )
        return

    lamp_name = query.data.split('_')[-1]
    message = await lamps(f'lamp_{lamp_name}')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=lamp_keyboard()
    )

async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in password:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="شما قبلاً احراز هویت شده‌اید.",
            reply_markup=lamp_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفاً رمز عبور را وارد کنید:"
        )

async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in password:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="شما قبلاً احراز هویت شده‌اید.",
            reply_markup=lamp_keyboard()
        )
        return

    password = update.message.text
    if password == PASSWORD:
        password.add(user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="احراز هویت موفقیت‌آمیز بود!",
            reply_markup=lamp_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="رمز عبور اشتباه است. لطفاً دوباره تلاش کنید."
        )
# Handlers to start bot 
if __name__ == "__main__":
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler('start', start_command_handler))
    bot.add_handler(CallbackQueryHandler(button_callback))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler))

    bot.run_polling()
