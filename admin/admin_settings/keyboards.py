from telegram import InlineKeyboardButton
from common.lang_dicts import BUTTONS
import models


def build_admin_settings_keyboard(lang: models.Language = models.Language.ARABIC):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["add_admin"],
                callback_data="add_admin",
            ),
            InlineKeyboardButton(
                text=BUTTONS[lang]["remove_admin"],
                callback_data="remove_admin",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["show_admins"],
                callback_data="show_admins",
            )
        ],
    ]
    return keyboard
