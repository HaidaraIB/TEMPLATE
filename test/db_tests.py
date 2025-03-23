import os
import sys
from dotenv import load_dotenv
import asyncio

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import *


async def main():
    load_dotenv()
    create_tables()
    admin = User.get_by(conds={"id": 3})
    await admin.delete_one()


asyncio.run(main())
