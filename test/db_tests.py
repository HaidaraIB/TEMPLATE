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
    admins = User.get_by(attr="is_admin", val=True, all=True)
    print(admins)


asyncio.run(main())
