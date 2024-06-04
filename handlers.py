from telegram import (
    Update,
)

from telegram.ext import (
    CallbackQueryHandler,
    Application,
    PicklePersistence,
    InvalidCallbackData,
    Defaults,
)

from telegram.constants import (
    ParseMode,
)

from start import (
    start_command,
    inits,
)

from common.common import (
    invalid_callback_data,
    error_handler,
    create_folders
)

from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_user_home_page_handler
)

from common.force_join import check_joined_handler

from user.user_calls import *

from admin.admin_calls import *
from admin.admin_settings import *
from admin.broadcast import *
from admin.ban import *

import os

from DB import DB


def main():
    DB.creat_tables()
    create_folders()
    defaults = Defaults(parse_mode=ParseMode.HTML)
    my_persistence = PicklePersistence(filepath="data/persistence", single_file=False)
    app = (
        Application.builder()
        .token(os.getenv("BOT_TOKEN"))
        .post_init(inits)
        # .arbitrary_callback_data(True)
        .persistence(persistence=my_persistence)
        .defaults(defaults)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(
        CallbackQueryHandler(
            callback=invalid_callback_data, pattern=InvalidCallbackData
        )
    )
    # ADMIN SETTINGS
    app.add_handler(admin_settings_handler)
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)

    app.add_handler(broadcast_message_handler)

    app.add_handler(check_joined_handler)

    app.add_handler(ban_unban_user_handler)

    app.add_handler(start_command)
    app.add_handler(find_id_handler)
    app.add_handler(hide_ids_keyboard_handler)
    app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)