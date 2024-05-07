import datetime

import aiosqlite
import sqlalchemy.orm
import datetime as dt
from zoneinfo import ZoneInfo
from sqlalchemy import BigInteger, ForeignKey, select, update, delete, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///database/db.sqlite3')
async_session = async_sessionmaker(engine)

sessions = {}


# models
class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'Users'
    id = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    tz: Mapped[str] = mapped_column(nullable=True)


class Record(Base):
    __tablename__ = 'Records'
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user = mapped_column(ForeignKey('Users.id'))
    calories: Mapped[int] = mapped_column()
    proteins: Mapped[int] = mapped_column(nullable=True)
    fats: Mapped[int] = mapped_column(nullable=True)
    carbohydrates: Mapped[int] = mapped_column(nullable=True)
    u_time: Mapped[float] = mapped_column()


# create tables if not?
async def async_db_connect():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)


# requests
async def add_user(chat_id, tz='Europe/Moscow'):
    async with async_session() as db_session:
        user = await db_session.scalar(select(User).where(User.id == chat_id))
        if not user:
            db_session.add(User(id=chat_id, tz=tz))
            await db_session.commit()


async def add_record(chat_id, calories, proteins=0, fats=0, carbohydrates=0):
    async with async_session() as db_session:
        db_session.add(Record(user=chat_id, calories=calories, u_time=dt.datetime.now().timestamp(),
                              proteins=proteins, fats=fats, carbohydrates=carbohydrates))
        await db_session.commit()


async def get_today_records(chat_id):
    async with async_session() as db_session:
        user = await db_session.scalar(select(User).where(User.id == chat_id))
        if user.tz:
            tz = user.tz
        else:
            tz = 'Europe/Moscowqw'
        now = datetime.datetime.now(tz=ZoneInfo(tz))
        date = datetime.datetime(now.year, now.month, now.day, hour=0, minute=0, second=0, tzinfo=ZoneInfo(tz)).timestamp()
        records = await db_session.execute(
            select(Record.calories, Record.proteins, Record.fats, Record.carbohydrates).
            where(Record.user == chat_id, Record.u_time > date, Record.u_time < (date+86399)))
        return records

