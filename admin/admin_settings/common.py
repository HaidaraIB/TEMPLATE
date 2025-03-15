from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Chat, Update
from telegram.ext import ContextTypes, ConversationHandler
from custom_filters import Admin
from common.back_to_home_page import back_to_admin_home_page_button


def build_admin_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة آدمن ➕",
                callback_data="add admin",
            ),
            InlineKeyboardButton(
                text="حذف آدمن ✖️",
                callback_data="remove admin",
            ),
        ],
        [
            InlineKeyboardButton(
                text="عرض آيديات الآدمنز الحاليين 🆔",
                callback_data="show admins",
            )
        ],
    ]
    return keyboard
