from telegram import (
    Update,
    Chat,
    Bot,
    ReplyKeyboardMarkup,
    BotCommand,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    Application,
    ConversationHandler,
)


import os
from DB import DB

from common.force_join import check_if_user_member

from common.common import (
    build_user_keyboard,
    build_admin_keyboard,
    request_buttons,
)


async def inits(app: Application):
    bot: Bot = app.bot
    await bot.set_my_commands(
        commands=[BotCommand(command="start", description="home page")]
    )
    await DB.add_new_admin(user_id=int(os.getenv("OWNER_ID")))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        admin = DB.check_admin(user_id=update.effective_user.id)
        if admin:
            if (
                not context.user_data.get("request_keyboard_hidden", None)
                or not context.user_data["request_keyboard_hidden"]
            ):
                context.user_data["request_keyboard_hidden"] = False
                await update.message.reply_text(
                    text="أهلاً بك...",
                    reply_markup=ReplyKeyboardMarkup(
                        request_buttons, resize_keyboard=True
                    ),
                )
            else:
                await update.message.reply_text(
                    text="أهلاً بك...",
                    reply_markup=ReplyKeyboardRemove(),
                )

            text = "تعمل الآن كآدمن🕹"
            keyboard = build_admin_keyboard()

        else:
            old_user = DB.get_user(user_id=update.effective_user.id)
            if not old_user:
                new_user = update.effective_user
                await DB.add_new_user(
                    user_id=new_user.id,
                    username=new_user.username,
                    name=new_user.full_name,
                )

            member = await check_if_user_member(update=update, context=context)
            if not member:
                return

            text = "أهلاً بك..."
            keyboard = build_user_keyboard()

        await update.message.reply_text(
            text=text,
            reply_markup=keyboard,
        )
        return ConversationHandler.END

start_command = CommandHandler(command="start", callback=start)

