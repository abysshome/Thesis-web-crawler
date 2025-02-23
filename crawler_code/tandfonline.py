import sys

import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from func import getLast


start_index = 1283
# month = sys.argv[1]


def scrape_data(month):
    global start_index
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
        if url.startswith('https://www.tandfonline.com'):
            try:
                print(index)
                driver = webdriver.Chrome()
                driver.get(url)
                try:
                    driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
                except NoSuchElementException:
                    print('NoSuchElementException')
                # 开始提取
                html = driver.page_source
                tree = etree.HTML(html)
                # doi
                match_doi = tree.xpath('//li[@class="dx-doi"]//text()')
                if match_doi:
                    match_doi = [s[len("https://doi.org/"):] for s in match_doi if "https://doi.org/" in s]
                    # print("doi: " + match_doi[0])
                    df.loc[index, 'doi'] = match_doi[0]
                # 摘要
                match_abstract = tree.xpath('//p[@class="last"]//text()|//p[@class="first last"]//text()')
                if match_abstract:
                    # print("摘要" + ''.join(match_abstract))
                    df.loc[index, 'abstract'] = ''.join(match_abstract)
                # 关键字
                match_keywords = tree.xpath('//div[@class="hlFld-KeywordText"]//ul//text()')
                if match_keywords:
                    # print("关键字" + ''.join(match_keywords))
                    df.loc[index, 'keywords'] = ','.join(match_keywords).strip()
                # 作者
                match_author = tree.xpath('//a[@class="author"]//text()')
                if match_author:
                    # print("作者" + ''.join(match_author))
                    df.loc[index, 'authors'] = ''.join(match_author[0])
                # 日期
                match_date = tree.xpath('//div[@class="itemPageRangeHistory"]//text()')
                if match_date:
                    match_date = ' '.join([s.strip() for s in match_date if s.strip() != ''])
                    # print("日期" + match_date)
                    df.loc[index, 'date of publication'] = match_date
                # 期刊
                match_published = tree.xpath('//span[@class="journal-heading"]//text()')
                if match_published:
                    # print("期刊" + match_published[1].strip())
                    df.loc[index, 'published'] = match_published[1].strip()
                # 标题
                match_title = tree.xpath('//span[@class="NLM_article-title hlFld-title"]//text()')
                if match_title:
                    # print("标题" + match_title)
                    df.loc[index, 'title'] = match_title[0].strip()
                driver.quit()
                if index == getLast(f"data\\month{month}.csv",'https://www.tandfonline.com'):
                    df.to_csv(f'tandfonline{month}.csv', index=False)
                    start_index = 21843
            except Exception as e:
                # print(e)
                print("index: " + str(index))
                start_index = index + 1
                df.to_csv(f'tandfonline{month}.csv', index=False)
                driver.quit()
                if start_index < 21842:
                    scrape_data()
                else:
                    df.to_csv(f'tandfonline{month}.csv', index=False)


for i in range(1, 13):
    if i == 6:
        continue
    # 启动程序
    start_index = 0
    scrape_data(i)

# url = 'https://www.tandfonline.com/doi/full/10.1080/21663831.2020.1743787'
# driver = webdriver.Chrome()
# driver.get(url)
# driver.maximize_window()
# time.sleep(5)
# driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
# # 开始提取
# html = driver.page_source
# tree = etree.HTML(html)
# # doi
# match_doi = tree.xpath('//li[@class="dx-doi"]//text()')
# match_doi = [s[len("https://doi.org/"):] for s in match_doi if "https://doi.org/" in s]
# print(match_doi)
# # 摘要
# match_abstract = tree.xpath('//p[@class="last"]//text()')
# print(''.join(match_abstract))
# # 关键字
# match_keywords = tree.xpath('//div[@class="hlFld-KeywordText"]//ul//text()')
# print(''.join(match_keywords))
# # 作者
# match_author = tree.xpath('//a[@class="author"]//text()')[0]
# print(''.join(match_author))
# # 日期
# match_date = tree.xpath('//div[@class="itemPageRangeHistory"]//text()[contains(.,"Accepted")]')[0].strip()
# print(match_date)
# # 期刊
# match_published = tree.xpath('//span[@class="journal-heading"]//text()')[1].strip()
# print(match_published)
# # 标题
# match_title = tree.xpath('//span[@class="NLM_article-title hlFld-title"]//text()')[0].strip()
# print(match_title)
# driver.quit()
