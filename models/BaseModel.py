import sqlalchemy as sa
from models.DB import Base, lock_and_release, connect_and_close
from sqlalchemy.orm import Session


class BaseModel(Base):
    __abstract__ = True

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
