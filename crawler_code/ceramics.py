import time

import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from func import getLast

start_index = 0


def scrape_data(month):
    global start_index
    # 文件名
    df = pd.read_csv(f'data\\month{month}.csv')
    df['date of publication'] = df['date of publication'].astype(str)
    df['doi'] = df['doi'].astype(str)
    df['abstract'] = df['abstract'].astype(str)
    df['published'] = df['published'].astype(str)
    df['authors'] = df['authors'].astype(str)
    df['title'] = df['title'].astype(str)
    df['keywords'] = df['keywords'].astype(str)
    for index, row in df.iterrows():
        if index < start_index:
            continue  # 跳过已经处理过的部分
        url = row['url']
        if url.startswith('https://ceramics.onlinelibrary.wiley.com'):
            try:
                driver = webdriver.Chrome()
                print(index)
                driver.get(url)
                time.sleep(2)
                try:
                    driver.find_element(By.XPATH, '//a[@id="pane-pcw-detailscon"]').click()
                except NoSuchElementException:
                    print('NoSuchElementException')
                html = driver.page_source
                tree = etree.HTML(html)
                time.sleep(2)
                # doi
                match_doi = tree.xpath('//a[@class="epub-doi"]//text()')
                if match_doi:
                    match_doi = [s[len("https://doi.org/"):] for s in match_doi if "https://doi.org/" in s]
                    # print("doi: " + match_doi[0])
                    df.loc[index, 'doi'] = match_doi[0]
                # 摘要
                match_abstract = tree.xpath('//div[@class="article-section__content en main"]//text()')
                if match_abstract:
                    # print("摘要" + ''.join(match_abstract).strip())
                    df.loc[index, 'abstract'] = ''.join(match_abstract).strip()
                # 关键字
                match_keywords = tree.xpath('//section[@class="keywords"]//ul[@class="rlist rlist--inline"]//text()')
                if match_keywords:
                    # print("关键字" + ','.join(match_keywords))
                    df.loc[index, 'keywords'] = ','.join(match_keywords)
                # 作者
                match_author = tree.xpath(
                    '//div[@class="loa-wrapper loa-authors hidden-xs desktop-authors"]//p[@class="author-name"]//text()')
                if match_author:
                    # print("作者" + ','.join(match_author))
                    df.loc[index, 'authors'] = ','.join(match_author)
                # 日期
                match_date = tree.xpath('//span[@class="epub-date"]//text()')
                if match_date:
                    # print(match_date[0])
                    df.loc[index, 'date of publication'] = match_date[0]
                # 期刊
                match_published = tree.xpath('//p[@class="volume-issue"]//text()')
                if match_published:
                    match_published = " ".join(match_published)
                    # print("期刊" + match_published)
                    df.loc[index, 'published'] = match_published
                # 标题
                match_title = tree.xpath('//h1[@class="citation__title"]//text()')
                if match_title:
                    # print("标题: " + match_title[0])
                    df.loc[index, 'title'] = match_title[0]
                driver.quit()
                if index == getLast(f'data\\month{month}.csv', 'https://ceramics.onlinelibrary.wiley.com'):
                    df.to_csv(f'ceramics-over{month}.csv', index=False)
                    start_index = len(df) - 1
            except Exception as e:
                # print(e)
                print("index: " + str(index))
                start_index = index
                df.to_csv(f'ceramics-over{month}.csv', index=False)
                driver.quit()
                if start_index < len(df) - 1:
                    scrape_data(month)
                else:
                    df.to_csv(f'ceramics-over{month}.csv', index=False)


for i in range(2, 13):
    if i == 6: # 6月的数据已经爬取完毕
        continue
    # 启动程序
    if i == 2: # 2月的数据从18508开始
        start_index = 18508
    else: # 其他月份的数据从0开始
        start_index = 0
    scrape_data(i)  # 爬取数据
