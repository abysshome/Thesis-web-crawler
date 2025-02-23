import time

import pandas as pd
from lxml import etree
from selenium import webdriver

from func import getLast


def index_to_file():
    file = open("informs_index.txt", "w")
    print("输出文件")
    for index in indexList:
        file.write(str(index) + ",")
    file.close()


def scrape_data(month, start_index):
    df = pd.read_csv(f'informs\\informs{month}.csv')
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
            time.sleep(1)
            driver = webdriver.Chrome(options=options)
            print(f"m{month}:{index}")
            try:
                driver.get(url)
                html = driver.page_source
                tree = etree.HTML(html)
                # doi
                match_doi = tree.xpath('//a[@class="epub-section__doi__text"]//text()')
                if match_doi:
                    match_doi = [s[len("https://doi.org/"):] for s in match_doi if "https://doi.org/" in s]
                    # print("doi: " + match_doi[0])
                    df.loc[index, 'doi'] = match_doi[0]
                else:
                    print("no doi found")
                    df.loc[index, 'doi'] = 'null'
                # 摘要
                match_abstract = tree.xpath(
                    '//div[@class="hlFld-Abstract"]/div[@class="abstractSection abstractInFull"]//text()')
                if match_abstract:
                    # print("摘要" + ''.join(match_abstract))
                    df.loc[index, 'abstract'] = ''.join(match_abstract)
                else:
                    print("No abstract found")
                # 关键字
                match_keywords = tree.xpath(
                    '//section[@class="article__keyword row separator"]//ul[@class="rlist rlist--inline"]//text()')
                if match_keywords:
                    # print("关键字" + ','.join(match_keywords))
                    df.loc[index, 'keywords'] = ','.join(match_keywords).strip()
                else:
                    print("No keywords found")
                # 作者
                match_author = tree.xpath(
                    '//div[@class="citation"]//div[@class="accordion"]//a[@class="entryAuthor"]//text()')
                if match_author:
                    # print("作者" + ','.join(match_author))
                    df.loc[index, 'authors'] = ','.join(match_author)
                else:
                    print("No authors found")
                # 日期
                match_date = tree.xpath('//span[@class="epub-section__date"]//text()')
                if match_date:
                    # print(match_date[0])
                    df.loc[index, 'date of publication'] = match_date[0]
                else:
                    print("No date found")
                # 期刊
                match_published = tree.xpath('//a[@class="article__tocHeading"]//text()')
                if match_published:
                    match_published = " ".join(match_published[1:])
                    # print("期刊" + match_published)
                    df.loc[index, 'published'] = match_published
                else:
                    print("No published")
                # 标题
                match_title = tree.xpath('//h1[@class="citation__title"]//text()')
                if match_title:
                    # print("标题: " + match_title[0])
                    df.loc[index, 'title'] = match_title[0]
                driver.quit()
                if index >= getLast(f'informs\\informs{month}.csv', "https://pubsonline.informs.org") - 1:
                    df.to_csv(f'informs\\informs{month}.csv', index=False)
                    print("over")
                    start_index = len(df) - 1
            except Exception as e:
                # print(e)
                print(f"{month}-index:{index} ")
                start_index = index
                indexList[month] = start_index
                index_to_file()
                df.to_csv(f'informs\\informs{month}.csv', index=False)
                if start_index < len(df) - 1:
                    if driver:
                        driver.quit()
                else:
                    df.to_csv(f'informs\\informs{month}.csv', index=False)


indexList = [0, 84700, 17679, 0, 3467, 2606, 0, 3479, 0, 146, 0, 0, 0]
options = webdriver.ChromeOptions()
options.add_argument('--proxy-server=http://127.0.0.1:7890')
# options.add_argument('--headless')
# options.add_argument('--proxy-server=https://127.0.0.1:7890')
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
        'javascript': 2
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
