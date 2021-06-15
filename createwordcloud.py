# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 16:34:52 2018

@author: gaokuang
"""

import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime, timedelta, timezone
# 获取东八区时间
utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
# print(utc_dt)
cn_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
# print(cn_dt)
update_time = cn_dt.now().strftime('%Y-%m-%d %H:%M:%S')
image_time = cn_dt.now().strftime('%Y-%m-%d')
# 创建停用词list
def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords


# 对句子进行分词  
def seg_sentence(sentence):
    sentence_seged = jieba.cut(sentence.strip())
    stopwords = stopwordslist('stopword.txt')  # 这里加载停用词的路径
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word != '\t':
                outstr += word
                outstr += " "
    return outstr


inputs = open('word.txt', 'r', encoding='utf-8')

outputs = open('output.txt', 'w')

for line in inputs:
    line_seg = seg_sentence(line)  # 这里的返回值是字符串  
    outputs.write(line_seg + '\n')
outputs.close()
inputs.close()

inputs = open('output.txt', 'r', encoding='utf-8')
mytext = inputs.read()
wordcloud = WordCloud(background_color="white", max_words=500, width=2000, height=1600, margin=2,
                      font_path="simsun.ttf").generate(mytext)
plt.imshow(wordcloud)
plt.axis("off")
plt.savefig('微博 %s.jpg' % image_time, dpi=200)
plt.savefig('./wordimg/latest.jpg', dpi=200)
plt.show()
