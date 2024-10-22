import datetime

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    ForeignKey,
    Text
)
from sqlalchemy.orm import relationship

from src.db.base import BaseModel


class UsersProfile(BaseModel):
    """ Пользователи."""
    __tablename__ = 'users'

    telegram_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    act_code = Column(
        String,
        nullable=False,
        default='000'
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.now
    )

    history = relationship(
        'UsersHistory',
        back_populates='user',
        cascade='all, delete-orphan'
    )


class UsersHistory(BaseModel):
    """ История запросов юзеров. """
    __tablename__ = 'users_history'

    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    chat_id = Column(
        Integer
    )
    message_id = Column(
        Integer
    )
    message_content = Column(
        Text,
        nullable=True,
    )
    state = Column(
        String,
        nullable=True,
    )
    created_at = Column(
        DateTime,
        default=datetime.datetime.now,
    )

    user = relationship(
        'UsersProfile',
        back_populates='history'
    )

