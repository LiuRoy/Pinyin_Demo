# -*- coding=utf8 -*-
from __future__ import division
from math import log
from pypinyin import lazy_pinyin

from pinyin.utils import iter_dict
from pinyin.model import (
    PhraseSession,
    PhrasePinyin,
    Pinyin,
    init_phrase_tables,
)


def int_phrase_pinyin_map():
    """
    初始化字典中短语的拼音
    """
    result = {}
    total = 0
    for phrase, frequency in iter_dict():
        py = u' '.join(lazy_pinyin(phrase))
        total += frequency
        if py not in result:
            result[py] = {phrase: frequency}
        else:
            result[py][phrase] = result[py].get(phrase, 0) + frequency

    for py, phrase_map in result.iteritems():
        total_frequency = sum(phrase_map.values())
        Pinyin.add(py, log(total_frequency / total))
        for phrase, frequency in phrase_map.iteritems():
            PhrasePinyin.add(phrase, py, log(frequency / total_frequency))


if __name__ == '__main__':
    init_phrase_tables()
    int_phrase_pinyin_map()

    session = PhraseSession()
    session.execute('create index ix_pinyin on phrase_pinyin(pinyin)')
