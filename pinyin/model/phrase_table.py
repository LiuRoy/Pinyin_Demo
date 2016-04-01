# -*- coding=utf8 -*-
"""
    词语匹配
"""
import os

from sqlalchemy import Column, String, Integer, Float, create_engine, desc
from sqlalchemy.orm import sessionmaker

from pinyin.model.common import current_dir, BaseModel

db_name = os.path.join(current_dir, 'phrase.sqlite')
engine = create_engine('sqlite:///{}'.format(db_name))
PhraseSession = sessionmaker(bind=engine)


class PhrasePinyin(BaseModel):

    __tablename__ = 'phrase_pinyin'

    id = Column(Integer, primary_key=True)
    phrase = Column(String(20), nullable=False)
    pinyin = Column(String(100), nullable=False)
    probability = Column(Float, nullable=False)

    @classmethod
    def add(cls, phrase, pinyin, probability):
        session = PhraseSession()
        record = cls(phrase=phrase, pinyin=pinyin, probability=probability)
        session.add(record)
        session.commit()
        return record

    @classmethod
    def get_by_pinyin(cls, pinyin):
        session = PhraseSession()
        result = session.query(cls).filter(cls.pinyin == pinyin).all()
        session.commit()
        return {x.phrase: x.probability for x in result}


class Pinyin(BaseModel):

    __tablename__ = 'pinyin'

    id = Column(Integer, primary_key=True)
    pinyin = Column(String(100), nullable=False)
    probability = Column(Float, nullable=False)

    @classmethod
    def add(cls, pinyin, probability):
        session = PhraseSession()
        record = cls(pinyin=pinyin, probability=probability)
        session.add(record)
        session.commit()
        return record

    @classmethod
    def load(cls):
        session = PhraseSession()
        result = session.query(cls.pinyin, cls.probability).all()
        session.commit()
        return {py: prob for py, prob in result}


def init_phrase_tables():
    """
    创建表
    """
    if os.path.exists(db_name):
        os.remove(db_name)

    with open(db_name, 'w') as f:
        pass

    BaseModel.metadata.create_all(bind=engine, tables=[PhrasePinyin.__table__,
                                                       Pinyin.__table__])
