import sqlalchemy as sa
from models.BaseModel import BaseModel
from enum import Enum


class User(BaseModel):
    __tablename__ = "users"

    user_id = sa.Column(sa.BigInteger, unique=True)
    username = sa.Column(sa.String)
    name = sa.Column(sa.String)
    is_banned = sa.Column(sa.Boolean, default=0)
    is_admin = sa.Column(sa.Boolean, default=0)

    def __repr__(self):
        return f"User(user_id={self.user_id}, username={self.username}, name={self.name}, is_admin={bool(self.is_admin)}, is_banned={bool(self.is_banned)}"
