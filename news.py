import requests
import json
import re
from bs4 import BeautifulSoup

import streamlit as st

news_url = st.text_input(label='请输入网址,图片在侧边栏')


def nikkansports(news_url):
    if '/photonews/photonews_nsInc_' in news_url:
        news_url = news_url.replace(news_url,
                                    f'https://www.nikkansports.com/{re.findall("https://www.nikkansports.com/(.*?)/photonews/photonews", news_url)[0]}/news/{re.findall("photonews/photonews_nsInc_([0-9+]*)", news_url)[0]}.html')

    resp = requests.get(
        news_url,
    ).text

    i = 0

    imgs = []
    orig_imgs = []
    article_title = re.findall(r'<title>(.*?)</title>', resp, re.S)[0]
    st.subheader(article_title)

    for pic in resp:
        imgs = re.findall('<meta name="nsPicture" content="(.*?)">', resp)
        for pic in imgs:
            orig_imgs = imgs[i].replace('w500', 'w1300')
            st.sidebar.image(orig_imgs, width=300)
            i += 1
        break
    if 'entertainment/column/sakamichi' in news_url:
        soup = BeautifulSoup(resp, 'html.parser')

        news_div = soup.find('div', {'id': 'news'})
        p_tags = news_div.find_all('p')

        article_text = ''
        for p in p_tags:
            article_text += str(p)

    else:
        article_text = re.findall(r'<div id="news" class="article-body ">(.*?)</div>', resp, re.S)[0]
    st.markdown(article_text, unsafe_allow_html=True)


def oricon(url):
    if 'full' not in url:
        url = f'{url}/full/'

    resp = requests.get(url).text

    article_title = re.findall('<title>(.*?)</title>', resp, re.S)[0]
    st.subheader(article_title)

    article_text = re.sub(re.compile(r'<.*?>'), '', re.findall('<!--StartText-->(.*?)<!--EndText-->', resp, re.S)[0])
    st.markdown(article_text, unsafe_allow_html=True)
    img_re = re.findall('div class="unit-photo-preview"><h2 class="title">関連写真</h2>(.*?)</div>', resp, re.S)

    # 输出页面部分

    if '関連写真' not in resp:

        img = ''.join(re.findall('<!--StartText-->(.*?)<!--EndText-->', resp, re.S))
        img_list = re.findall('<a\s+[^>]*href="([^"]*photo[^"]*)"[^>]*>', img)
        i = 0
        for url in img_list:
            if 'photo' in url:
                img_url = img_list[i]
                ori_resp = requests.get(img_url).text
                i += 1
                og_imgs = re.findall('<meta property="og:image" content="(.*?)">', ori_resp)
                for pic in og_imgs:
                    og_img = pic.replace('cdn-cgi/image/width=1200,quality=85,format=auto/', '')
                    st.sidebar.image(og_img, width=350)

    else:
        img_url = re.findall('<a href="(.*?)">', ''.join(img_re))

        og_imgs = []

        i = 0
        for pic in img_url:
            ori_url = img_url[i]
            ori_resp = requests.get(ori_url).text
            og_imgs = re.findall('<meta property="og:image" content="(.*?)">', ori_resp)
            for pic in og_imgs:
                og_img = pic.replace('cdn-cgi/image/width=1200,quality=85,format=auto/', '')
                i += 1
                st.sidebar.image(og_img, width=350)


if 'nikkansports' in news_url:
    nikkansports(news_url)
if 'oricon' in news_url:
    oricon(news_url)
