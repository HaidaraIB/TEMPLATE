from telegram.ext import (
    ApplicationBuilder,
    Defaults,
    PicklePersistence,
)
from telegram.constants import ParseMode
from ptbcontrib.ptb_jobstores.sqlalchemy import PTBSQLAlchemyJobStore

import os
from start import inits

class MyApp:
    def build_app(self):
        defaults = Defaults(parse_mode=ParseMode.HTML)
        my_persistence = PicklePersistence(
            filepath="data/persistence", single_file=False
        )
        app = (
            ApplicationBuilder()
            .token(os.getenv("BOT_TOKEN"))
            .post_init(inits)
            # .arbitrary_callback_data(True)
            .persistence(persistence=my_persistence)
            .defaults(defaults)
            .concurrent_updates(True)
            .build()
        )
        app.job_queue.scheduler.add_jobstore(
            PTBSQLAlchemyJobStore(
                application=app,
                url="sqlite:///data/jobs.sqlite3",
            )
        )
        return app
