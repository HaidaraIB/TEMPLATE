from telegram import (
    Chat,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)


from common.common import (
    build_admin_keyboard,
    build_back_button,
    request_buttons,
)

from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
    HOME_PAGE_TEXT,
)

from start import admin_command

import os
from DB import DB
from custom_filters.Admin import Admin

(
    NEW_ADMIN_ID,
    CHOOSE_ADMIN_ID_TO_REMOVE,
) = range(2)

admin_settings_keyboard = [
    [
        InlineKeyboardButton(
            text="إضافة آدمن➕",
            callback_data="add admin",
        ),
        InlineKeyboardButton(
            text="حذف آدمن✖️",
            callback_data="remove admin",
        ),
    ],
    [
        InlineKeyboardButton(
            text="عرض آيديات الآدمنز الحاليين🆔",
            callback_data="show admins",
        )
    ],
    back_to_admin_home_page_button[0],
]


async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="إعدادات الآدمن🪄",
            reply_markup=InlineKeyboardMarkup(admin_settings_keyboard),
        )


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="اختر حساب الآدمن الذي تريد إضافته بالضغط على الزر أدناه، أو أرسل id، يمكنك إلغاء العملية بالضغط على /admin.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="اختيار آدمن",
                            request_users=KeyboardButtonRequestUsers(
                                request_id=0, user_is_bot=False
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return NEW_ADMIN_ID


async def new_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.effective_message.users_shared:
            user_id = update.effective_message.users_shared.users[0].user_id
        else:
            user_id = int(update.message.text)
        await DB.add_new_admin(user_id=user_id)
        if (
            not context.user_data.get("request_keyboard_hidden", None)
            or not context.user_data["request_keyboard_hidden"]
        ):
            await update.message.reply_text(
                text="تمت إضافة الآدمن بنجاح ✅",
                reply_markup=ReplyKeyboardMarkup(
                    request_buttons,
                    resize_keyboard=True,
                ),
            )
        else:
            await update.message.reply_text(
                text="تمت إضافة الآدمن بنجاح ✅",
                reply_markup=ReplyKeyboardRemove(),
            )

        await update.message.reply_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )

        return ConversationHandler.END


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        admins = DB.get_admin_ids()
        admin_ids_keyboard = [
            [InlineKeyboardButton(text=str(admin[0]), callback_data=str(admin[0]))]
            for admin in admins
        ]
        admin_ids_keyboard.append(build_back_button("back to admin settings"))
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه id الآدمن الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )
        return CHOOSE_ADMIN_ID_TO_REMOVE


async def choose_admin_id_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        admin_id = int(update.callback_query.data)
        if admin_id == int(os.getenv("OWNER_ID")):
            await update.callback_query.answer(
                text="لا يمكنك إزالة مالك البوت من قائمة الآدمنز ❗️"
            )
            return

        await DB.remove_admin(user_id=admin_id)
        await update.callback_query.answer(text="تمت إزالة الآدمن بنجاح ✅")
        admins = DB.get_admin_ids()
        admin_ids_keyboard = [
            [InlineKeyboardButton(text=str(admin[0]), callback_data=str(admin[0]))]
            for admin in admins
        ]
        admin_ids_keyboard.append(build_back_button("back to admin settings"))
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه id الآدمن الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )

        return CHOOSE_ADMIN_ID_TO_REMOVE


async def back_to_admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="هل تريد:",
            reply_markup=InlineKeyboardMarkup(admin_settings_keyboard),
        )
        return ConversationHandler.END


async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = DB.get_admin_ids()
    text = "آيديات الآدمنز الحاليين:\n\n"
    for admin in admins:
        if admin[0] == int(os.getenv("OWNER_ID")):
            text += "<code>" + str(admin[0]) + "</code>" + " <b>مالك البوت</b>\n"
            continue
        text += "<code>" + str(admin[0]) + "</code>" + "\n"
    text += "\nاختر ماذا تريد أن تفعل:"
    keyboard = build_admin_keyboard()
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard,
    )


admin_settings_handler = CallbackQueryHandler(
    admin_settings,
    "^admin settings$",
)

show_admins_handler = CallbackQueryHandler(
    callback=show_admins,
    pattern="^show admins$",
)

add_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_admin,
            pattern="^add admin$",
        ),
    ],
    states={
        NEW_ADMIN_ID: [
            MessageHandler(
                filters=filters.StatusUpdate.USER_SHARED,
                callback=new_admin_id,
            ),
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=new_admin_id,
            ),
        ]
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
    ],
)

remove_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_admin,
            pattern="^remove admin$",
        ),
    ],
    states={
        CHOOSE_ADMIN_ID_TO_REMOVE: [
            CallbackQueryHandler(
                choose_admin_id_to_remove,
                "^\d+$",
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_admin_settings,
            pattern="^back to admin settings$",
        ),
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
