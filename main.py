import logging
import os
from datetime import datetime as dt

import pandas as pd
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from draw import plot_timeseries, plot_reg
from google_api import get_sheet
from wx import get_weather

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TYPE_CHOICE, PLOT_TIMESERIES, PLOT_CORRELATION = range(3)
DRAW_TYPE = ["Timeseries", "Correlation"]


def pretty_print(row: list) -> str:
    strs = [
        f"\U0001F4C5: {row[0]}",
        f"\U000023F0: {row[1]}",
        f"\U00002600: {row[3]}",
        f"\U0001F326: {row[4]}%",
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

    update.message.reply_text("\U00002728 Check out successfully")
    update.message.reply_text(pretty_print(row_data))


def draw_start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [DRAW_TYPE]

    update.message.reply_text(
        "Which plot do you want?\n" "Send /cancel to stop.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="",
        ),
    )
    return TYPE_CHOICE


def choose_plot_type(update: Update, context: CallbackContext) -> int:
    sheet = get_sheet()
    df = pd.DataFrame(sheet.get_all_records())
    df["datetime"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    context.user_data["df"] = df

    update.message.reply_text(
        "Which Month do you want to inspect?\n",
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    dt.strptime(str(i), "%m").strftime("%b")
                    for i in set(df["datetime"].dt.month.values)
                ]
                + ["All"]
            ],
            one_time_keyboard=True,
        ),
    )

    if update.message.text == DRAW_TYPE[0]:
        return PLOT_TIMESERIES
    elif update.message.text == DRAW_TYPE[1]:
        return PLOT_CORRELATION
    else:
        update.message.reply_text("No such plot implemented")
    return ConversationHandler.END


def timeseries_plot(update: Update, context: CallbackContext) -> int:
    df = context.user_data["df"]
    df = df[df["check_type"] == "in"]

    user_ans = update.message.text
    if user_ans != "All":
        user_month_choice = int(dt.strptime(user_ans, "%b").strftime("%m"))
        df = df[(df["datetime"].dt.month == user_month_choice)]

    img_buf = plot_timeseries(df, user_ans)
    update.message.reply_photo(img_buf)
    return ConversationHandler.END


def correlation_plot(update: Update, context: CallbackContext) -> int:
    df = context.user_data["df"]
    df = df[df["check_type"] == "in"]

    user_ans = update.message.text
    if user_ans != "All":
        user_month_choice = int(dt.strptime(user_ans, "%b").strftime("%m"))
        df = df[(df["datetime"].dt.month == user_month_choice)]

    img_buf = plot_reg(df, user_ans)
    update.message.reply_photo(img_buf)
    return ConversationHandler.END


def main(token: str) -> None:
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", help_cmd))
    dispatcher.add_handler(CommandHandler("checkin", checkin))
    dispatcher.add_handler(CommandHandler("checkout", checkout))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("draw", draw_start)],
        states={
            TYPE_CHOICE: [
                MessageHandler(
                    Filters.text & ~Filters.command, choose_plot_type
                )
            ],
            PLOT_TIMESERIES: [
                MessageHandler(
                    Filters.text & ~Filters.command, timeseries_plot
                )
            ],
            PLOT_CORRELATION: [
                MessageHandler(
                    Filters.text & ~Filters.command, correlation_plot
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", lambda c, u: ConversationHandler.END)
        ],
    )
    dispatcher.add_handler(conv_handler)

    if os.getenv("ON_HEROKU"):
        # webhook
        updater.start_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", "8443")),
            url_path=token,
            webhook_url=os.getenv("HOST") + token,
        )
    else:
        # local testing
        updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    load_dotenv()
    main(os.getenv("TG_BOT_TOKEN"))
