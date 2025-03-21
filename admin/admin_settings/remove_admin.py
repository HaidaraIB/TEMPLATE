from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from start import admin_command
from common.keyboards import build_back_button
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from admin.admin_settings.admin_settings import admin_settings_handler
import os
from custom_filters import Admin
import models
from common.constants import *


CHOOSE_ADMIN_ID_TO_REMOVE = 0


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.isnumeric():

            admin = models.User.get_by(
                conds={
                    "id": int(update.callback_query.data),
                },
            )

            if admin.user_id == int(os.getenv("OWNER_ID")):
                await update.callback_query.answer(
                    text="لا يمكنك إزالة مالك البوت من قائمة الآدمنز ❗️",
                    show_alert=True,
                )
                return

            await admin.update_one(update_dict={"is_admin": False})
            await update.callback_query.answer(
                text="تمت إزالة الآدمن بنجاح ✅",
                show_alert=True,
            )

        await update.callback_query.answer()
        admins = models.User.get_by(conds={"is_admin": True}, all=True)
        admin_ids_keyboard = [
            [
                InlineKeyboardButton(
                    text=admin.name,
                    callback_data=str(admin.id),
                ),
            ]
            for admin in admins
        ]
        admin_ids_keyboard.append(build_back_button("back_to_admin_settings"))
        admin_ids_keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه الآدمن الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )
        return CHOOSE_ADMIN_ID_TO_REMOVE


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
                remove_admin,
                "^\d+$",
            ),
        ]
    },
    fallbacks=[
        admin_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
