import logging
import requests
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "<BOT_TOKEN>"
FLASK_APP_URL = "http://localhost:7000"
API_KEY = "your_api_key_here"  # API key for authentication
PASSWORD = "yourpassword"  # Your Password to Continue

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# To save the authentication status of users
authenticated_users = set()

# Queue to handle user commands
user_command_queue = asyncio.Queue()

def lamp_keyboard():
    try:
        headers = {'api-key': API_KEY}
        response_1 = requests.get(f"{FLASK_APP_URL}/get_lamp_state/lamp_1", headers=headers)
        response_2 = requests.get(f"{FLASK_APP_URL}/get_lamp_state/lamp_2", headers=headers)
        response_3 = requests.get(f"{FLASK_APP_URL}/get_lamp_state/lamp_3", headers=headers)
        response_4 = requests.get(f"{FLASK_APP_URL}/get_lamp_state/lamp_4", headers=headers)
        
        lamp_1_status = "❌" if not response_1.json().get('state', False) else "✅"
        lamp_2_status = "❌" if not response_2.json().get('state', False) else "✅"
        lamp_3_status = "❌" if not response_3.json().get('state', False) else "✅"
        lamp_4_status = "❌" if not response_4.json().get('state', False) else "✅"
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

async def lamps_name(lamp_name):
    try:
        headers = {'api-key': API_KEY}
        response = requests.get(f"{FLASK_APP_URL}/get_lamp_state/{lamp_name}", headers=headers)
        logger.info(f"Received response from get_lamp_state: {response.json()}")
        current_state = response.json().get('state')
        if current_state is None:
            raise ValueError(f"Invalid lamp state received for {lamp_name}")

        if current_state:
            response = requests.post(f"{FLASK_APP_URL}/turn_off_lamp/{lamp_name}", headers=headers)
        else:
            response = requests.post(f"{FLASK_APP_URL}/turn_on_lamp/{lamp_name}", headers=headers)

        logger.info(f"Received response from toggling lamp: {response.json()}")
        return response.json().get('message', 'Error toggling lamp')
    except Exception as e:
        logger.error(f"Error toggling lamp {lamp_name}: {e}")
        return f"An error occurred: {e}"

async def process_queue():
    while True:
        update, context = await user_command_queue.get()
        query = update.callback_query
        user_id = query.from_user.id

        if user_id not in authenticated_users:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="لطفاً ابتدا احراز هویت کنید."
            )
            continue

        lamp_name = query.data.split('_')[-1]
        message = await lamps_name(f'lamp_{lamp_name}')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=lamp_keyboard()
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await user_command_queue.put((update, context))
    await update.callback_query.answer(text="در صف انتظار هستید...")

async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in authenticated_users:
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
    if user_id in authenticated_users:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="شما قبلاً احراز هویت شده‌اید.",
            reply_markup=lamp_keyboard()
        )
        return

    password = update.message.text
    if password == PASSWORD:
        authenticated_users.add(user_id)
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

async def turn_on_lamp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in authenticated_users:
        lamp_name = update.message.text.split()[-1]
        message = await lamps_name(f'lamp_{lamp_name}')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=lamp_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفاً ابتدا احراز هویت کنید."
        )

async def turn_off_lamp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in authenticated_users:
        lamp_name = update.message.text.split()[-1]
        message = await lamps_name(f'lamp_{lamp_name}')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=lamp_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفاً ابتدا احراز هویت کنید."
        )

async def help_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    admin_username = "user_name"  # Admin username for sending message
    help_message = (
        "سلام, من یک ربات کنترل لامپ هستم. شما می‌توانید از دستورات زیر استفاده کنید:\n"
        "/start - شروع و احراز هویت\n"
        "/help - دریافت راهنما\n"
        "/turn_on_lamp <lamp_number> - روشن کردن لامپ مشخص شده\n"
        "/turn_off_lamp <lamp_number> - خاموش کردن لامپ مشخص شده\n"
        "اگر سوال یا مشکلی دارید، لطفاً به ادمین پیام دهید: "
        f"[@{admin_username}](tg://user?id={user_id})"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message, parse_mode='Markdown')
 
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in authenticated_users:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفاً ابتدا دستور /start را اجرا کنید."
        )
    else:
        await help_command_handler(update, context)

async def main():
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler('start', start_command_handler))
    bot.add_handler(CommandHandler('help', help_command_handler))
    bot.add_handler(CallbackQueryHandler(button_callback))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler))
    bot.add_handler(CommandHandler('turn_on_lamp', turn_on_lamp_handler))
    bot.add_handler(CommandHandler('turn_off_lamp', turn_off_lamp_handler))
    bot.add_handler(MessageHandler(filters.ALL, message_handler))

    # Initialize the bot
    await bot.initialize()

    # Start processing the queue
    asyncio.create_task(process_queue())

    # Start the bot
    await bot.start()

    # Run the bot until it is stopped
    await bot.updater.start_polling()
    await asyncio.Event().wait()  # Instead of updater.idle()

# Execute the main function
asyncio.run(main())
