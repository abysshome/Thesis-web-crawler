import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from func import getLast


def index_to_file():
    file = open("tandfonline_index.txt", "w")
    print("输出文件")
    for index in indexList:
        file.write(str(index) + ",")
    file.close()


def scrape_data(month, start_index):
    df = pd.read_csv(f'tandfonline\\tandfonline{month}.csv')
    df['date of publication'] = df['date of publication'].astype(str)
    df['doi'] = df['doi'].astype(str)
    df['abstract'] = df['abstract'].astype(str)
    df['published'] = df['published'].astype(str)
    df['authors'] = df['authors'].astype(str)
    df['title'] = df['title'].astype(str)
    df['keywords'] = df['keywords'].astype(str)
    for index, row in df.iterrows():
        if index <= start_index:
            continue  # 跳过已经处理过的部分
        url = row['url']
        if url.startswith('https://www.tandfonline.com') and row['abstract'] == 'nan':
            print(f"m{month}:{index}")
            driver = webdriver.Chrome(options=options)
            try:
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
                else:
                    print("No doi found")
                # 摘要
                match_abstract = tree.xpath('//p[@class="last"]//text()|//p[@class="first last"]//text()')
                if match_abstract:
                    # print("摘要" + ''.join(match_abstract))
                    df.loc[index, 'abstract'] = ''.join(match_abstract)
                else:
                    print("No abstract found")
                    df.loc[index, 'abstract'] = 'null'
                # 关键字
                match_keywords = tree.xpath('//div[@class="hlFld-KeywordText"]//ul//text()')
                if match_keywords:
                    # print("关键字" + ''.join(match_keywords))
                    df.loc[index, 'keywords'] = ','.join(match_keywords).strip()
                else:
                    print("No keywords found")
                # 作者
                match_author = tree.xpath('//a[@class="author"]//text()')
                if match_author:
                    # print("作者" + ''.join(match_author))
                    df.loc[index, 'authors'] = ''.join(match_author[0])
                else:
                    print("No author found")
                # 日期
                match_date = tree.xpath('//div[@class="itemPageRangeHistory"]//text()')
                if match_date:
                    match_date = ' '.join([s.strip() for s in match_date if s.strip() != ''])
                    # print("日期" + match_date)
                    df.loc[index, 'date of publication'] = match_date
                else:
                    print("No date")
                # 期刊
                match_published = tree.xpath('//span[@class="journal-heading"]//text()')
                if match_published:
                    # print("期刊" + match_published[1].strip())
                    df.loc[index, 'published'] = match_published[1].strip()
                else:
                    print("No published")
                # 标题
                match_title = tree.xpath('//span[@class="NLM_article-title hlFld-title"]//text()')
                if match_title:
                    # print("标题" + match_title)
                    df.loc[index, 'title'] = match_title[0].strip()
                else:
                    print("No title")
                driver.quit()
                if index >= getLast(f"tandfonline\\tandfonline{month}.csv", 'https://www.tandfonline.com') - 1:
                    df.to_csv(f'tandfonline\\tandfonline{month}.csv', index=False)
                    start_index = len(df) - 1
            except Exception as e:
                print("index: " + str(index))
                start_index = index
                indexList[month] = start_index
                index_to_file()
                df.to_csv(f'tandfonline\\tandfonline{month}.csv', index=False)
                if driver:
                    driver.quit()
                if start_index >= len(df) - 1:
                    df.to_csv(f'tandfonline\\tandfonline{month}.csv', index=False)


indexList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
options = webdriver.ChromeOptions()
options.add_argument('--proxy-server=http://127.0.0.1:7890')
# options.add_argument('--headless')
# options.add_argument('--start-maximized')
# options.add_argument('--proxy-server=https://127.0.0.1:7890')
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
    }
}
options.add_experimental_option('prefs', prefs)
if __name__ == '__main__':
    for i in range(1, 13):
        if i == 6:
            continue
        scrape_data(i, indexList[i])
    # futures = []
    # with concurrent.futures.ThreadPoolExecutor() as pool:
    #     for i in range(1, 13):
    #         if i == 6:
    #             continue
    #         futures.append(pool.submit(scrape_data, i, indexList[i]))
    #     concurrent.futures.wait(futures)
