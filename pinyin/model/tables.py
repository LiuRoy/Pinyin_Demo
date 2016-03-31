# -*- coding=utf8 -*-
"""
    转移概率
"""
import os

from sqlalchemy import Column, String, Integer, Float, create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

current_dir = os.path.dirname(os.path.abspath(__file__))
db_name = os.path.join(current_dir, 'pinyin.sqlite')
engine = create_engine('sqlite:///{}'.format(db_name))
Session = sessionmaker(bind=engine)
BaseModel = declarative_base()


class Transition(BaseModel):

    __tablename__ = 'transition'

    id = Column(Integer, primary_key=True)
    previous = Column(String(2), nullable=False)
    behind = Column(String(2), nullable=False)
    probability = Column(Float, nullable=False)

    @classmethod
    def add(cls, previous, behind, probability):
        """添加转移记录

        Args:
            previous (string): 前面的汉字
            behind (string): 后面的汉字
            probability (float): 转移概率
        """
        session = Session()
        record = cls(previous=previous, behind=behind, probability=probability)
        session.add(record)
        session.commit()
        return record

    @classmethod
    def join_emission(cls, pinyin, character):
        """join emission表查询

        Args:
            pinyin (string): 拼音
            characters (string): 上次的汉字
        """
        session = Session()
        query = session.query(cls.behind,
                              Emission.probability + cls.probability).\
            join(Emission, Emission.character == cls.behind).\
            filter(cls.previous == character).\
            filter(Emission.pinyin == pinyin).\
            order_by(desc(Emission.probability + cls.probability))
        result = query.first()
        session.commit()
        return result


class Emission(BaseModel):

    __tablename__ = 'emission'

    id = Column(Integer, primary_key=True)
    character = Column(String(2), nullable=False)
    pinyin = Column(String(8), nullable=False)
    probability = Column(Float, nullable=False)

    @classmethod
    def add(cls, character, pinyin, probability):
        """添加转移记录

        Args:
            character (string): 汉字
            pinyin (string): 拼音
            probability (float): 概率
        """
        session = Session()
        record = cls(character=character, pinyin=pinyin, probability=probability)
        session.add(record)
        session.commit()
        return record

    @classmethod
    def join_starting(cls, pinyin, limit=50):
        """join starting表查询

        Args:
            pinyin (string): 拼音
            limit (int): 数据个数
        """
        session = Session()
        query = session.query(cls.character,
                              cls.probability + Starting.probability).\
            join(Starting, cls.character == Starting.character).\
            filter(cls.pinyin == pinyin).\
            order_by(desc(cls.probability + Starting.probability)).\
            limit(limit)
        result = query.all()
        session.commit()
        return result


class Starting(BaseModel):

    __tablename__ = 'starting'

    id = Column(Integer, primary_key=True)
    character = Column(String(2), nullable=False)
    probability = Column(Float, nullable=False)

    @classmethod
    def add(cls, character, probability):
        """添加转移记录

        Args:
            character (string): 汉字
            probability (float): 起始概率
        """
        session = Session()
        record = cls(character=character, probability=probability)
        session.add(record)
        session.commit()
        return record


def init_tables():
    """
    创建表
    """
    if os.path.exists(db_name):
        os.remove(db_name)

    with open(db_name, 'w') as f:
        pass

    BaseModel.metadata.create_all(bind=engine)

    session = Session()
    session.execute('create index ix_starting_character on starting(character);')
    session.execute('create index ix_emission_character on emission(character);')
    session.execute('create index ix_emission_pinyin on emission(pinyin);')
    session.execute('create index ix_transition_previous on transition(previous);')
    session.execute('create index ix_transition_behind on transition(behind);')
