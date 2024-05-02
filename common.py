from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Chat,
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUser,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)


from telegram.constants import (
    ChatMemberStatus,
    ChatType,
)

from telegram.error import TimedOut, NetworkError

import os
import uuid
import traceback
import json
from DB import DB

from custom_filters.User import User
from custom_filters.Admin import Admin

from pyrogram import Client


cpyro = Client(
    name="bot_pyro",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN"),
)


async def check_if_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = await context.bot.get_chat_member(
        chat_id=int(os.getenv("CHANNEL_ID")), user_id=update.effective_user.id
    )
    if chat_member.status == ChatMemberStatus.LEFT:
        text = f"""لبدء استخدام البوت  يجب عليك الانضمام الى قناة البوت أولاً.
        
✅ اشترك أولاً 👇.
🔗 {os.getenv("CHANNEL_LINK")}

ثم اضغط تحقق✅"""
        check_joined_button = [
            [InlineKeyboardButton(text="تحقق✅", callback_data="check joined")]
        ]
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text, reply_markup=InlineKeyboardMarkup(check_joined_button)
            )
        else:
            await update.message.reply_text(
                text=text, reply_markup=InlineKeyboardMarkup(check_joined_button)
            )
        return False
    return True


def build_user_keyboard():
    keyboard = []
    return InlineKeyboardMarkup(keyboard)


def build_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إعدادات الآدمن⚙️🎛",
                callback_data="admin settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="إخفاء/إظهار كيبورد معرفة الآيديات🪄",
                callback_data="hide ids keyboard",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية👥",
                callback_data="broadcast",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def callback_button_uuid_generator():
    return uuid.uuid4().hex


back_to_admin_hom_epage_button = [
    [
        InlineKeyboardButton(
            text="العودة إلى القائمة الرئيسية🔙",
            callback_data="back to admin home page",
        )
    ],
]

back_to_user_hom_epage_button = [
    [
        InlineKeyboardButton(
            text="العودة إلى القائمة الرئيسية🔙",
            callback_data="back to user home page",
        )
    ],
]


async def back_to_user_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        is_user_member = await check_if_user_member(update=update, context=context)

        if not is_user_member:
            return

        text = "القائمة الرئيسية🔝"
        keyboard = build_user_keyboard()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        return ConversationHandler.END


async def back_to_admin_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="القائمة الرئيسية🔝", reply_markup=build_admin_keyboard()
        )
        return ConversationHandler.END


back_to_user_home_page_handler = CallbackQueryHandler(
    back_to_user_home_page, "^back to user home page$"
)
back_to_admin_home_page_handler = CallbackQueryHandler(
    back_to_admin_home_page, "^back to admin home page$"
)


request_buttons = [
    [
        KeyboardButton(
            text="معرفة id مستخدم🆔",
            request_user=KeyboardButtonRequestUser(request_id=0, user_is_bot=False),
        ),
        KeyboardButton(
            text="معرفة id قناة📢",
            request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=True),
        ),
    ],
    [
        KeyboardButton(
            text="معرفة id مجموعة👥",
            request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=False),
        ),
        KeyboardButton(
            text="معرفة id بوت🤖",
            request_user=KeyboardButtonRequestUser(request_id=3, user_is_bot=True),
        ),
    ],
]


async def invalid_callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.callback_query.answer("انتهت صلاحية هذا الزر")
        # try:
        #     await update.callback_query.delete_message()
        # except BadRequest:
        #     pass


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, (TimedOut, NetworkError)):
        return
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    try:
        error = f"""update = {json.dumps(update_str, indent=2, ensure_ascii=False)} 
        
user_data = {str(context.user_data)}
chat_data = {str(context.chat_data)}

{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}

{'-'*100}


    """

        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(error)
    except TypeError:
        error = f"""update = TypeError
        
user_data = {str(context.user_data)}
chat_data = {str(context.chat_data)}

{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}

{'-'*100}


    """

        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(error)
