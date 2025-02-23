import time

import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By

from func import getLast


def login(driver):
    # 登录函数
    driver.get('https://ieeexplore.ieee.org/document/9103211')
    driver.maximize_window()
    time.sleep(2)
    driver.find_element(By.LINK_TEXT, "Personal Sign In").click()
    # 使用placeholder属性来定位输入框
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Email Address"]').send_keys('')
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Password"]').send_keys('')
    # 定位并点击按钮
    driver.find_element(By.CLASS_NAME, "sign-in-btn").click()


def index_to_file():
    file = open("ieee.txt", "w")
    print("输出文件")
    for index in indexList:
        file.write(str(index) + ",")
    file.close()


def scrape_data(month, start_index):
    # 读取 CSV 文件
    df = pd.read_csv(f'ieee\\ieee{month}.csv')
    df['date of publication'] = df['date of publication'].astype(str)
    df['doi'] = df['doi'].astype(str)
    df['abstract'] = df['abstract'].astype(str)
    df['published'] = df['published'].astype(str)
    df['authors'] = df['authors'].astype(str)
    df['title'] = df['title'].astype(str)
    df['keywords'] = df['keywords'].astype(str)
    driver = webdriver.Chrome(options=options)
    login(driver)
    for index, row in df.iterrows():
        if index < start_index:
            continue
        url = row['url']
        if url.startswith('https://ieeexplore.ieee.org') and row['doi'] == 'nan':
            print(f"m{month}:{index}")
            try:
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
                        # print(match_keywords)
                        df.loc[index, 'keywords'] = match_keywords
                except Exception as e:
                    print("无keywords")
                # "DOI:"
                match_doi = tree.xpath('//div[@class="u-pb-1 stats-document-abstract-doi"]//a//text()')
                if match_doi:
                    # print(match_doi)
                    match_doi = match_doi[0]
                    df.loc[index, 'doi'] = match_doi
                else:
                    print("No doi found")
                    df.loc[index, 'doi'] = 'nullxxx'
                # "Abstract:"
                match_abstract = tree.xpath(
                    '//div[@class="col-12"]/div[@class="u-mb-1"]/div//text()|//div[@class="abstract-text row g-0"]/div[@class="col-12 text-base-md-lh"]/div[@class="u-mb-1"]/div/text()')
                if match_abstract:
                    match_abstract = match_abstract[0]
                    df.loc[index, 'abstract'] = match_abstract
                else:
                    print("No abstract found")
                # 期刊
                match_published_in = tree.xpath(
                    '//div[@class="abstract-desktop-div hide-mobile text-base-md-lh"]//div[@class="u-pb-1 '
                    'stats-document-abstract-publishedIn"]/a/text()')
                if match_published_in:
                    match_published_in = match_published_in[0]
                    df.loc[index, 'published'] = match_published_in
                else:
                    print("No published")
                #  "Date of Publication:"
                match_date_of_publication = tree.xpath(
                    '//div[@class="u-pb-1 doc-abstract-pubdate"]/text()|//div[@class="u-pb-1 doc-abstract-dateadded"]/text()')
                if match_date_of_publication:
                    match_date_of_publication = match_date_of_publication[0]
                    df.loc[index, 'date of publication'] = match_date_of_publication
                else:
                    print("No date")
                # 标题
                match_title = tree.xpath('//h1[@class="document-title text-2xl-md-lh"]/span/text()')
                if match_title:
                    match_title = match_title[0]
                    df.loc[index, 'title'] = match_title
                else:
                    print("No title found")
                # 作者
                match_authors = tree.xpath('//span[@class="authors-info"]//a//text()')
                if match_authors:
                    match_authors = ''.join(match_authors)
                    df.loc[index, 'authors'] = match_authors
                else:
                    print("No author found")
                if index >= getLast(f'ieee\\ieee{month}.csv', "https://ieeexplore.ieee.org") - 2:
                    df.to_csv(f'ieee\\ieee{month}.csv', index=False)
                    start_index = len(df) - 1
            except Exception as e:
                print(f"ieee_index{month}:{index} ")
                # 保存当前结果
                df.to_csv(f'ieee\\ieee{month}.csv', index=False)
                time.sleep(1)
                # 更新全局变量 start_index
                start_index = index
                indexList[month] = start_index
                index_to_file()
                # 如果 start_index 小于 20000，则继续循环
                if index < len(df) - 1:
                    if driver:
                        driver.quit()
                    driver = webdriver.Chrome(options=options)
                    login(driver)
                else:
                    df.to_csv(f'ieee\\ieee{month}.csv', index=False)


import concurrent.futures

indexList = [0, 100000, 100000, 25381, 100000, 100000, 100000, 100000, 100000, 19353, 20356, 17459, 14696]
options = webdriver.ChromeOptions()
options.add_argument('--proxy-server=http://127.0.0.1:7890')
# options.add_argument('--proxy-server=https://127.0.0.1:7890')
# options.add_argument('--headless')
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
    }
}
options.add_experimental_option('prefs', prefs)
if __name__ == '__main__':
    for i in range(12, 13):
        if i == 6:
            continue
        scrape_data(i, indexList[i])
    # futures = []
    # with concurrent.futures.ProcessPoolExecutor() as pool:
    #     for i in range(1, 13):
    #         if i == 6:
    #             continue
    #         futures.append(pool.submit(scrape_data, i, indexList[i]))
    #     concurrent.futures.wait(futures)
