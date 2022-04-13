import logging
import os
from datetime import datetime as dt
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler

from wx import get_weather
from google_api import get_sheet


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def pretty_print(row: list) -> str:
    strs = [
        f"\U0001F4C5: {row[0]}",
        f"\U000023F0: {row[1]}",
        f"\U00002600: {row[3]}",
        f"\U0001F326: {row[4]} %",
        f"\U0001F321: {row[5]} ~ {row[6]}\U00002103",
        f"\U00002728: {row[7]}",
    ]
    return "\n".join(strs)


def ownership(id: str):
    return id == os.getenv("TG_BOT_USER")


def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("help")


def checkin(update: Update, context: CallbackContext):
    if not ownership(str(update.message.chat_id)):
        update.message.reply_text("You are not the owner sorry \U0001F972")
        return
    time_day = dt.today().strftime("%Y-%m-%d")
    time_now = dt.today().strftime("%H:%M:%S")
    row_data = [time_day, time_now, "in"] + get_weather()
    sheet = get_sheet()
    sheet.append_row(row_data, value_input_option="USER_ENTERED")

    update.message.reply_text("\U0001F331 Check in successfully")
    update.message.reply_text(pretty_print(row_data))


def checkout(update: Update, context: CallbackContext):
    if not ownership(str(update.message.chat_id)):
        update.message.reply_text("You are not the owner sorry \U0001F972")
        return
    time_day = dt.today().strftime("%Y-%m-%d")
    time_now = dt.today().strftime("%H:%M:%S")
    sheet = get_sheet()
    row_data = [time_day, time_now, "out"] + get_weather()
    sheet.append_row(row_data, value_input_option="USER_ENTERED")

    update.message.reply_text("\U0001F331 Check out successfully")
    update.message.reply_text(pretty_print(row_data))


def main(token: str) -> None:
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", help_cmd))
    dispatcher.add_handler(CommandHandler("checkin", checkin))
    dispatcher.add_handler(CommandHandler("checkout", checkout))

    # webhook
    updater.start_webhook(
        listen="0.0.0.0", port=int(os.getenv("PORT")), url_path=token
    )
    updater.bot.setWebhook(os.getenv("HOST") + token)

    # local testing
    # updater.start_polling()


if __name__ == "__main__":
    load_dotenv()
    main(os.getenv("TG_BOT_TOKEN"))
