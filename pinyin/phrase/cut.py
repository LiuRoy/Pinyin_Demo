# -*- coding=utf8 -*-
from math import log
from pinyin.model import PhrasePinyin, Pinyin

FREQ = Pinyin.load()


def get_DAG(sentence):
    DAG = {}
    N = len(sentence)
    for k in xrange(N):
        tmplist = []
        i = k
        frag = sentence[k:i+1]
        while i < N:
            if u' '.join(frag) in FREQ:
                tmplist.append(i)
            i += 1
            frag = sentence[k:i + 1]
        if not tmplist:
            tmplist.append(k)
        DAG[k] = tmplist
    return DAG


def calc(sentence, DAG, route):
    N = len(sentence)
    route[N] = (0, 0)
    for idx in xrange(N - 1, -1, -1):
        route[idx] = max((FREQ.get(u' '.join(sentence[idx:x + 1])) + route[x + 1][0], x) for x in DAG[idx])


def cut_DAG_NO_HMM(sentence):
    DAG = get_DAG(sentence)
    route = {}
    calc(sentence, DAG, route)
    x = 0
    N = len(sentence)
    buf = []
    while x < N:
        y = route[x][1] + 1
        l_word = sentence[x:y]
        if len(l_word) == 1:
            buf.extend(l_word)
            x = y
        else:
            if buf:
                yield buf
                buf = []
            yield l_word
            x = y
    if buf:
        yield buf
        buf = []

def get_max_key(m):
    result = sorted(m.items(), key=lambda d: d[1], reverse=True)
    return result[0][0]

if __name__ == '__main__':
    # 但也并不是那么出乎意料或难以置信
    while 1:
        string = raw_input("input:")
        pinyin_list = string.split()
        result = u''
        for x in cut_DAG_NO_HMM(pinyin_list):
            phrase_map = PhrasePinyin.get_by_pinyin(u' '.join(x))
            if phrase_map:
                result += get_max_key(phrase_map)
            else:
                for y in x:
                    result += get_max_key(PhrasePinyin.get_by_pinyin(y))

        print result
