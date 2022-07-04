from flask import Flask, render_template
import sqlite3
from wordcloud import WordCloud
import jieba
from matplotlib import pyplot as plt
from PIL import Image
import numpy as np

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/index')
def home():
    return index()


@app.route('/movie')
def movie():
    datalist = []
    con = sqlite3.connect('../database/top250.db')
    cur = con.cursor()
    sql = 'select * from movie'
    data = cur.execute(sql)
    for item in data:
        datalist.append(item)
    cur.close()
    con.close()
    return render_template('movie.html', movies=datalist)


@app.route('/score')
def score():
    score = []
    num = []
    con = sqlite3.connect('../database/top250.db')
    cur = con.cursor()
    sql = "select score,count(score) from movie group by score"
    data = cur.execute(sql)
    for item in data:
        score.append(item[0])
        num.append(item[1])
    cur.close()
    con.close()
    return render_template('score.html', score=score, num=num)


@app.route('/word')
def word():
    sql= 'select instroduction from movie'
    con = sqlite3.connect('../database/top250.db')
    cur = con.cursor()
    ins = cur.execute(sql)
    text = ''
    for item in ins:
        text += item[0]
    img = Image.open('./static/assets/img/2.jpg')
    img_array = np.array(img)
    cut = jieba.lcut(text)
    new_cut=[]
    for i in cut:
        if len(i) >= 2:
            new_cut.append(i)
    print(len(new_cut))
    string = ' '.join(new_cut)
    wc = WordCloud(
        mask=img_array,
        background_color='#f5f9fc',
        font_path='msyh.ttc',
    ).generate_from_text(string)
    plt.figure(figsize=(1024,946), dpi=1)
    plt.imshow(wc)
    plt.axis('off')
    plt.savefig('./static/assets/img/word.png', bbox_inches='tight', facecolor='#f5f9fc')
    cur.close()
    con.close()
    return render_template('word.html')


@app.route('/team')
def team():
    return render_template('team.html')


if __name__ == '__main__':
    app.run()
