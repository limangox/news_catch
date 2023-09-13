import requests
import json
import re
from bs4 import BeautifulSoup

import streamlit as st

# 设置锚点
st.markdown("""<a name="top"></a>""",unsafe_allow_html=True)
# 设置页面标题
st.set_page_config(page_title="新闻抓图小工具")

news_url = st.text_input(label='请输入网址,图片在侧边栏 ')
st.caption('*目前支持 Modelpress | 日刊Sports | Oricon news | Mantan-Web*')


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


def mantan(url):
    global img_url
    global url_article
    if 'photo' not in url:
        img_url = url.replace('.html', '/photopage/001.html')
        url_article = url
    if 'photo' in url:
        img_url = url
        url_article = img_url.replace('/photopage/001.html','.html')

    headers = {
        'referer': 'https://mantan-web.jp',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }

    # 文字部分
    resp = requests.get(url_article,headers=headers)
    resp.encoding = 'utf-8'  # 指定UTF-8编码
    html_content = resp.text

    pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
    matches = pattern.findall(html_content)
    if matches:
        # 对匹配到的内容进行解码
        script_content = matches[0]

        # 提取headline字段的内容
        headline_pattern = re.compile(r'"headline"\s*:\s*"(.*?)"')
        headline_match = headline_pattern.search(script_content)

        if headline_match:
            article_title = headline_match.group(1)
            st.subheader(article_title)

    soup = BeautifulSoup(html_content, 'html.parser')
    # 文章部分
    all_p_tags = soup.find_all('p', class_='article__text')
    result_text = '<br></br>'.join([p.get_text(strip=True) for p in all_p_tags])
    st.markdown(result_text, unsafe_allow_html=True)


    # 图片部分

    resp = requests.get(img_url,headers=headers)
    resp.encoding = 'utf-8'  # 指定UTF-8编码
    img_content = resp.text

    img_soup = BeautifulSoup(img_content, 'html.parser')

    script_content = []
    for script_tag in img_soup.find_all('script'):
        if 'var __images = JSON.parse' in script_tag.text:
            script_content = script_tag.text
            break
    img_list = []
    if script_content:
        # 使用正则表达式提取JSON内容部分
        json_match = script_content.split("('")[1].replace("')", '')
        list_ = json.loads(json_match)
        i = 0
        for img in list_:
            pic = list_[i]['src']
            img_list.append(pic)
            i += 1

    i = 0
    img_contnt = '<div style="display:inline">'
    for img in range(len(img_list)):
        pic = img_list[i].split('?')[0]
        img_contnt += f'''<img src='{pic}' width="50%">'''
        i += 1
    st.markdown(img_contnt, unsafe_allow_html=True)



def mdpr(url):

    mdpr_headers = {
        'referer': f'{url}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }

    if 'photo' not in url and 'mdpr.jp' in url:
        mdpr_resp = requests.get(url, headers=mdpr_headers).text
        mdpr_photo_url = re.findall('<a class="c-image__image" href="(.*?)" >', mdpr_resp)[0]
        url = f'https://mdpr.jp{mdpr_photo_url}'
    if "photo" in url:
        url = url
    mdpr_photo_resp = requests.get(url, headers=mdpr_headers).text
    # 标题
    mdpr_arti_title = re.findall('<h1 class="p-articleHeader__title">(.*?)</h1>', mdpr_photo_resp)[0]
    st.subheader(mdpr_arti_title,anchor='title')

    soup = BeautifulSoup(mdpr_photo_resp, 'html.parser')
    # 获取头图
    imageWrapper = soup.find('img', {'class': 'c-image__image'}).get('src').split('?')[0]

    img_list = re.findall('<img src="(.*?)" alt=".*" width="125"', mdpr_photo_resp)
    i = 0
    x = 1
    st.caption(f'图片数量：{len(img_list) + 1}')
    # 图片展示
    st.markdown(f"""<div><img src='{imageWrapper}' width="100%"></div>""", unsafe_allow_html=True)
    i = 0
    img_contnt = '<div style="display:inline">'
    for img in range(len(img_list)):
        pic = img_list[i].split('?')[0]
        img_contnt += f'''<img src='{pic}' width="50%">'''
        i += 1
    st.markdown(img_contnt,unsafe_allow_html=True)



if 'nikkansports' in news_url:
    nikkansports(news_url)
if 'oricon' in news_url:
    oricon(news_url)
if 'mantan' in news_url:
    mantan(news_url)
if 'mdpr' in news_url:
    mdpr(news_url)

if news_url is '':
    pass
else:
    st.markdown("""<a href="#top" style="text-decoration:none;border-radius:30px;padding: 10px 10px 10px 10px;display:block;margin:5px 5px 5px 5px;background-color:#9e3eb2;color:white;text-align:center;">返回顶部</a>""",unsafe_allow_html=True)
