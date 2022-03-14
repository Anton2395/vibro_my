from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, DateTime, BigInteger
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker



engine = create_engine("postgresql+psycopg2://mvlab:z1x2c3@10.0.0.2:5432/db1")


base = declarative_base()


class Datchik_1_axel(base):
    __tablename__ = "datchik_1_axel"
    id = Column(Integer, primary_key=True)
    axel_time = Column(Float, index=True)
    axel = Column(Float, index=True)


class Datchik_1_temp(base):
    __tablename__ = "datchik_1_temp"
    id = Column(Integer, primary_key=True)
    temp_time = Column(Float, index=True)
    temp = Column(Float, index=True)


class Datchik_2_axel(base):
    __tablename__ = "datchik_2_axel"
    id = Column(Integer, primary_key=True)
    axel_time = Column(Float, index=True)
    axel = Column(Float, index=True)


class Datchik_2_temp(base):
    __tablename__ = "datchik_2_temp"
    id = Column(Integer, primary_key=True)
    temp_time = Column(Float, index=True)
    temp = Column(Float, index=True)


class Datchik_3_axel(base):
    __tablename__ = "datchik_3_axel"
    id = Column(Integer, primary_key=True)
    axel_time = Column(Float, index=True)
    axel = Column(Float, index=True)


class Datchik_3_temp(base):
    __tablename__ = "datchik_3_temp"
    id = Column(Integer, primary_key=True)
    temp_time = Column(Float, index=True)
    temp = Column(Float, index=True)


class Datchik_4_axel(base):
    __tablename__ = "datchik_4_axel"
    id = Column(Integer, primary_key=True)
    axel_time = Column(Float, index=True)
    axel = Column(Float, index=True)


class Datchik_4_temp(base):
    __tablename__ = "datchik_4_temp"
    id = Column(Integer, primary_key=True)
    temp_time = Column(Float, index=True)
    temp = Column(Float, index=True)


class Datchik_5_axel(base):
    __tablename__ = "datchik_5_axel"
    id = Column(Integer, primary_key=True)
    axel_time = Column(BigInteger, index=True)
    axel = Column(Float, index=True)


class Datchik_5_temp(base):
    __tablename__ = "datchik_5_temp"
    id = Column(Integer, primary_key=True)
    temp_time = Column(BigInteger, index=True)
    temp = Column(Float, index=True)


class User(base):
    __tablename__ = "user"
    chat_id = Column(Integer, primary_key=True)
    username = Column(String(200))
    mailing = Column(Integer, default=0)

base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
