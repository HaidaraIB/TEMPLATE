from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestUsers,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from admin.admin_settings.keyboards import build_admin_settings_keyboard
from common.back_to_home_page import back_to_admin_home_page_handler
from common.keyboards import (
    build_admin_keyboard,
    build_back_to_home_page_button,
    build_back_button,
)
from common.lang_dicts import *
from custom_filters import PrivateChatAndOwner
from start import admin_command
from Config import Config
import models


async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        keyboard = build_admin_settings_keyboard(lang)
        keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=True)[0])
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["admin_settings_title"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


admin_settings_handler = CallbackQueryHandler(
    admin_settings,
    "^admin_settings$|^back_to_admin_settings$",
)


NEW_ADMIN_ID = range(1)


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.answer()
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=TEXTS[lang]["add_admin_instruction"],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=BUTTONS[lang]["select_admin_button"],
                            request_users=KeyboardButtonRequestUsers(
                                request_id=4, user_is_bot=False
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return NEW_ADMIN_ID


async def new_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        if update.effective_message.users_shared:
            admin_id = update.effective_message.users_shared.users[0].user_id
        else:
            admin_id = int(update.message.text)

        with models.session_scope() as s:
            admin = s.get(models.User, admin_id)

            if not admin:
                admin_chat = await context.bot.get_chat(chat_id=admin_id)
                admin = models.User(
                    user_id=admin_chat.id,
                    username=admin_chat.username if admin_chat.username else "",
                    name=admin_chat.full_name,
                    is_admin=True,
                )
                s.add(admin)
            else:
                admin.is_admin = True

        await update.message.reply_text(
            text=TEXTS[lang]["admin_added_success"],
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=TEXTS[lang]["home_page"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


add_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_admin,
            pattern="^add_admin$",
        ),
    ],
    states={
        NEW_ADMIN_ID: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=new_admin_id,
            ),
            MessageHandler(
                filters=filters.StatusUpdate.USERS_SHARED,
                callback=new_admin_id,
            ),
        ]
    },
    fallbacks=[
        admin_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)


CHOOSE_ADMIN_ID_TO_REMOVE = range(1)


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:

            if update.callback_query.data.isnumeric():
                admin = s.get(models.User, int(update.callback_query.data))

                if admin.user_id == Config.OWNER_ID:
                    await update.callback_query.answer(
                        text=TEXTS[lang]["cannot_remove_owner"],
                        show_alert=True,
                    )
                    return
                admin.is_admin = False
                s.commit()
                await update.callback_query.answer(
                    text=TEXTS[lang]["admin_removed_success"],
                    show_alert=True,
                )

            await update.callback_query.answer()
            admins = s.query(models.User).filter(models.User.is_admin == True).all()
            admin_ids_keyboard = [
                [
                    InlineKeyboardButton(
                        text=admin.name,
                        callback_data=str(admin.user_id),
                    ),
                ]
                for admin in admins
            ]
        admin_ids_keyboard.append(
            build_back_button("back_to_admin_settings", lang=lang)
        )
        admin_ids_keyboard.append(
            build_back_to_home_page_button(lang=lang, is_admin=True)[0]
        )
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["remove_admin_instruction"],
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )
        return CHOOSE_ADMIN_ID_TO_REMOVE


remove_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_admin,
            pattern="^remove_admin$",
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


async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:
            admins = s.query(models.User).filter(models.User.is_admin == True).all()
            text = ""
            for admin in admins:
                if admin.user_id == Config.OWNER_ID:
                    text += f"<b>{TEXTS[lang]['bot_owner']}</b>\n" + str(admin) + "\n\n"
                    continue
                text += str(admin) + "\n\n"
        text += TEXTS[lang]["continue_with_admin_command"]
        await update.callback_query.edit_message_text(text=text)


show_admins_handler = CallbackQueryHandler(
    callback=show_admins,
    pattern="^show_admins$",
)
