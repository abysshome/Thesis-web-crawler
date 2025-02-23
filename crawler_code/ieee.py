import time
import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By

from func import getLast

start_index = 1035


# month = sys.argv[1]
def login(driver):
    # 登录函数
    driver.get('https://www.sciencedirect.com/science/article/pii/S1631072119301809')
    # driver.maximize_window()
    time.sleep(2)
    driver.find_element(By.ID, 'gh-cta-btn').click()
    driver.find_element(By.ID, 'bdd-email').send_keys('')
    driver.find_element(By.ID, 'bdd-elsPrimaryBtn').click()
    time.sleep(2)
    driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
    driver.find_element(By.CLASS_NAME, 'els-container-right').click()
    time.sleep(2)
    driver.find_element(By.ID, 'username').send_keys('')
    driver.find_element(By.ID, 'password').send_keys('')
    driver.find_element(By.ID, 'login_submit').click()
    time.sleep(2)



def scrape_data(month):
    global start_index, index
    # 读取 CSV 文件
    df = pd.read_csv(f'data\\month{month}.csv', encoding='utf-8')
    df['date of publication'] = df['date of publication'].astype(str)
    df['doi'] = df['doi'].astype(str)
    df['abstract'] = df['abstract'].astype(str)
    df['published'] = df['published'].astype(str)
    df['authors'] = df['authors'].astype(str)
    df['title'] = df['title'].astype(str)
    df['keywords'] = df['keywords'].astype(str)
    driver = webdriver.Chrome()
    try:
        for index, row in df.iterrows():
            if index < start_index:
                continue
            url = row['url']
            if url.startswith('https://ieeexplore.ieee.org'):
                print(index)
                url = url + "/keywords#keywords"
                driver.get(url)
                html = driver.page_source
                tree = etree.HTML(html)
                try:
                    driver.find_element(By.XPATH, '//button[@id="keywords"]').click()
                    match_keywords = tree.xpath(
                        '//div[@class="stats-keywords-container"]//ul[@class="u-mt-1 u-p-0 List--no-style List--inline"]//a/text()')
                    if match_keywords:
                        match_keywords = ','.join(match_keywords).strip()
                        df.loc[index, 'keywords'] = match_keywords
                except Exception as e:
                    print("无keywords")
                # "DOI:"
                match_doi = tree.xpath('//div[@class="u-pb-1 stats-document-abstract-doi"]//a//text()')
                if match_doi:
                    match_doi = match_doi[0]
                    df.loc[index, 'doi'] = match_doi
                # "Abstract:"
                match_abstract = tree.xpath(
                    '//div[@class="col-12"]/div[@class="u-mb-1"]/div//text()|//div[@class="abstract-text row g-0"]/div[@class="col-12 text-base-md-lh"]/div[@class="u-mb-1"]/div/text()')
                if match_abstract:
                    match_abstract = match_abstract[0]
                    df.loc[index, 'abstract'] = match_abstract
                # 期刊
                match_published_in = tree.xpath(
                    '//div[@class="abstract-desktop-div hide-mobile text-base-md-lh"]//div[@class="u-pb-1 '
                    'stats-document-abstract-publishedIn"]/a/text()')
                if match_published_in:
                    match_published_in = match_published_in[0]
                    df.loc[index, 'published'] = match_published_in
                #  "Date of Publication:"
                match_date_of_publication = tree.xpath(
                    '//div[@class="u-pb-1 doc-abstract-pubdate"]/text()|//div[@class="u-pb-1 doc-abstract-dateadded"]/text()')
                if match_date_of_publication:
                    match_date_of_publication = match_date_of_publication[0]
                    df.loc[index, 'date of publication'] = match_date_of_publication

                # 标题
                match_title = tree.xpath('//h1[@class="document-title text-2xl-md-lh"]/span/text()')
                if match_title:
                    match_title = match_title[0]
                    df.loc[index, 'title'] = match_title
                # 作者
                match_authors = tree.xpath('//span[@class="authors-info"]//a//text()')
                if match_authors:
                    match_authors = ''.join(match_authors)
                    df.loc[index, 'authors'] = match_authors
                if index == getLast(f'data\\month{month}.csv', "https://ieeexplore.ieee.org"):
                    df.to_csv(f'ieee{month}.csv', index=False)
                    start_index = len(df) - 1
    except Exception as e:
        print("出现异常:", e)
        print(f"index:{month}" + str(index))
        # 保存当前结果
        df.to_csv(f'ieee{month}.csv', index=False)
        time.sleep(1)
        # 更新全局变量 start_index
        start_index = index + 1
        # 如果 start_index 小于 20000，则继续循环
        if index < len(df) - 1:
            driver.quit()
            scrape_data(month)
        else:
            df.to_csv(f'ieee{month}.csv', index=False)


for i in range(1, 13):
    if i == 6:
        continue
    # 启动程序
    start_index = 0
    scrape_data(i)
