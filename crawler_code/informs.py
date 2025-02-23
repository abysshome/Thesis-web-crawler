import time

import pandas as pd
from lxml import etree
from selenium import webdriver

start_index = 0


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
        if url.startswith('https://pubsonline.informs.org'):
            try:
                driver = webdriver.Chrome(options=options)
                print(index)
                driver.get(url)
                html = driver.page_source
                tree = etree.HTML(html)
                # doi
                match_doi = tree.xpath('//a[@class="epub-section__doi__text"]//text()')
                if match_doi:
                    match_doi = [s[len("https://doi.org/"):] for s in match_doi if "https://doi.org/" in s]
                    print("doi: " + match_doi[0])
                    df.loc[index, 'doi'] = match_doi[0]
                # 摘要
                match_abstract = tree.xpath(
                    '//div[@class="hlFld-Abstract"]/div[@class="abstractSection abstractInFull"]//text()')
                if match_abstract:
                    print("摘要" + ''.join(match_abstract))
                    df.loc[index, 'abstract'] = ''.join(match_abstract)
                # 关键字
                match_keywords = tree.xpath(
                    '//section[@class="article__keyword row separator"]//ul[@class="rlist rlist--inline"]//text()')
                if match_keywords:
                    print("关键字" + ','.join(match_keywords))
                    df.loc[index, 'keywords'] = ','.join(match_keywords).strip()
                # 作者
                match_author = tree.xpath(
                    '//div[@class="citation"]//div[@class="accordion"]//a[@class="entryAuthor"]//text()')
                if match_author:
                    # print("作者"+','.join(match_author))
                    df.loc[index, 'authors'] = ','.join(match_author)
                # 日期
                match_date = tree.xpath('//span[@class="epub-section__date"]//text()')
                if match_date:
                    # print(match_date[0])
                    df.loc[index, 'date of publication'] = match_date[0]
                # 期刊
                match_published = tree.xpath('//a[@class="article__tocHeading"]//text()')
                if match_published:
                    match_published = " ".join(match_published[1:])
                    # print("期刊"+match_published)
                    df.loc[index, 'published'] = match_published
                # 标题
                match_title = tree.xpath('//h1[@class="citation__title"]//text()')
                if match_title:
                    # print("标题: "+match_title[0])
                    df.loc[index, 'title'] = match_title[0]
                driver.quit()
                if index == 21683:
                    df.to_csv(f'informs{month}.csv', index=False)
                    start_index = 21843
            except Exception as e:
                print(e)
                print("index: " + str(index))
                start_index = index + 1
                df.to_csv(f'informs{month}.csv', index=False)
                driver.quit()
                if start_index < 21842:
                    scrape_data()
                else:
                    df.to_csv(f'informs{month}.csv', index=False)


options = webdriver.ChromeOptions()
options.add_argument('--proxy-server=http://127.0.0.1:7890')
for i in range(2, 13):
    if i == 6:
        continue
    # 启动程序
    if i == 2:
        start_index = 0
    else:
        start_index = 0
    scrape_data(i)
